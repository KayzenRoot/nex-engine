"""Strict, bounded validator for nex_gpu_render_profile.v1 exports.

The CLI reads one JSON document from stdin, never opens a caller-supplied path,
uses only the Python standard library, and independently recomputes aggregates.
Validation does not turn synthetic test fixtures or headless runs into hardware
evidence.
"""
from __future__ import annotations

import csv
import datetime as _datetime
import json
import math
import re
import sys
from typing import Any


class ProfileError(ValueError):
    """An invalid, inconsistent, unsupported, or oversized profile document."""


SCHEMA_VERSION = "nex_gpu_render_profile.v1"
FORMULA_VERSION = "nex-percentile-and-one-percent-low-v1"
MAX_BYTES = 8_000_000
MAX_SAMPLES = 16_000
MIN_VALID_SAMPLES = 300
MAX_SAFE_INTEGER = 9_007_199_254_740_991
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_RE = re.compile(r"^\d{10,}-\d{6,}$", re.ASCII)
SERIES_PREFIX = "series."
LOCKED_DURATION_TOLERANCE_SECONDS = 1e-9
ALLOWED_COUNTS = frozenset({25, 50, 100, 200})
ALLOWED_MODES = frozenset({"geometry", "lights", "vfx", "combined"})
TOP_KEYS = frozenset({
    "schema_version", "run_id", "run_status", "run_reason", "captured_at_utc",
    "source_sha", "godot_version", "os", "display", "renderer", "driver",
    "adapter", "viewport", "workload", "settings", "measurement", "series",
    "device_snapshot",
})
SERIES_SPECS = {
    "GPU_RENDER_MS": ("ms", "RenderingServer.viewport_get_measured_render_time_gpu", 60_000.0),
    "CPU_RENDER_MS": ("ms", "RenderingServer.viewport_get_measured_render_time_cpu", 60_000.0),
    "MAIN_LOOP_INTERVAL_MS": ("ms", "SceneTree._process(delta)", 1000.0),
    "RENDERER_ALLOCATION_BYTES": ("bytes", "Performance.RENDER_VIDEO_MEM_USED", MAX_SAFE_INTEGER),
}
MEASUREMENT_KEYS = frozenset({
    "provider", "warmup_seconds", "requested_seconds", "observed_seconds",
    "warmup_frames_discarded", "invalid_main_loop_samples", "percentile_method",
    "formula_version", "one_percent_low_fps_formula", "one_percent_low_fps",
    "temporal_alignment_note",
})
SERIES_KEYS = frozenset({
    "status", "unit", "provider", "samples", "valid_sample_count",
    "invalid_sample_count", "aggregates", "unavailable_reason",
})


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ProfileError("non-JSON numeric constant: " + value)


def _exact_object(value: Any, keys: frozenset[str], name: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ProfileError(name + " must be a JSON object")
    actual = frozenset(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        raise ProfileError(f"{name} fields differ; missing={missing}, extra={extra}")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProfileError(name + " must be a non-empty string")
    return value


def _integer(value: Any, name: str, *, minimum: int = 0, maximum: int = MAX_SAFE_INTEGER) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ProfileError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def _finite_number(value: Any, name: str, *, minimum_exclusive: float = 0.0, maximum: float) -> float:
    if type(value) not in (int, float):
        raise ProfileError(name + " must be a JSON number")
    try:
        numeric = float(value)
    except (OverflowError, ValueError):
        raise ProfileError(name + " is not finite") from None
    if not math.isfinite(numeric) or not minimum_exclusive < numeric <= maximum:
        raise ProfileError(f"{name} must be finite in ({minimum_exclusive},{maximum}]")
    return numeric


def _timestamp(value: Any, name: str) -> str:
    text = _text(value, name)
    try:
        parsed = _datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise ProfileError(name + " must be an ISO-8601 timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProfileError(name + " must include a timezone")
    return text


def _percentile(ordered: list[float], quantile: float) -> float:
    rank = max(1, math.ceil(quantile * len(ordered)))
    return ordered[rank - 1]


def _aggregates(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)
    return {
        "mean": math.fsum(ordered) / len(ordered),
        "p50": _percentile(ordered, 0.50),
        "p95": _percentile(ordered, 0.95),
        "p99": _percentile(ordered, 0.99),
    }


def _one_percent_low_fps(samples: list[float]) -> float:
    slowest_count = max(1, math.ceil(0.01 * len(samples)))
    slowest = sorted(samples)[-slowest_count:]
    return 1000.0 / (math.fsum(slowest) / len(slowest))


def _close(actual: float, expected: float, name: str) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-5, abs_tol=1e-3):
        raise ProfileError(name + " differs from the independently recalculated value")


def _series_label(name: str, field: str = "") -> str:
    return SERIES_PREFIX + name + ("." + field if field else "")


def _validate_series_samples(name: str, samples_raw: Any, maximum: float) -> list[float]:
    label = _series_label(name)
    if type(samples_raw) is not list or len(samples_raw) > MAX_SAMPLES:
        raise ProfileError(label + ".samples exceeds its bound or is not an array")
    samples: list[float] = []
    for index, raw in enumerate(samples_raw):
        metric = _finite_number(raw, f"{label}.samples[{index}]", maximum=maximum)
        if name == "MAIN_LOOP_INTERVAL_MS" and metric >= 1000.0:
            raise ProfileError("main-loop interval must be below 1000 ms")
        samples.append(metric)
    return samples


def _validate_measured_series(name: str, record: dict[str, Any], samples: list[float], valid_count: int, maximum: float) -> None:
    if valid_count < MIN_VALID_SAMPLES or record["unavailable_reason"] != "":
        raise ProfileError("MEASURED series requires enough valid samples and no unavailable reason")
    aggregate_label = _series_label(name, "aggregates")
    aggregates = _exact_object(record["aggregates"], frozenset({"mean", "p50", "p95", "p99"}), aggregate_label)
    for key, expected in _aggregates(samples).items():
        actual = _finite_number(aggregates[key], _series_label(name, "aggregates." + key), maximum=maximum)
        _close(actual, expected, _series_label(name, "aggregates." + key))


def _validate_unavailable_series(record: dict[str, Any], valid_count: int) -> None:
    reason = record["unavailable_reason"]
    if not isinstance(reason, str) or not reason.strip():
        raise ProfileError("UNAVAILABLE series must state a cause")
    if valid_count >= MIN_VALID_SAMPLES or record["aggregates"] is not None:
        raise ProfileError("UNAVAILABLE series cannot hide enough measured samples or claim aggregates")


def _validate_series(name: str, value: Any) -> tuple[dict[str, Any], list[float], dict[str, Any]]:
    unit, provider, maximum = SERIES_SPECS[name]
    label = _series_label(name)
    record = _exact_object(value, SERIES_KEYS, label)
    status = record["status"]
    if status not in {"MEASURED", "UNAVAILABLE"}:
        raise ProfileError(_series_label(name, "status is not an allowed status"))
    if record["unit"] != unit or record["provider"] != provider:
        raise ProfileError(label + " has mismatched measurement provenance")
    samples = _validate_series_samples(name, record["samples"], maximum)
    valid_count = _integer(record["valid_sample_count"], _series_label(name, "valid_sample_count"))
    invalid_count = _integer(record["invalid_sample_count"], _series_label(name, "invalid_sample_count"))
    if valid_count != len(samples):
        raise ProfileError(label + " valid count differs from raw sample count")
    if status == "MEASURED":
        _validate_measured_series(name, record, samples, valid_count, maximum)
    else:
        _validate_unavailable_series(record, valid_count)
    facts = {"status": status, "valid_sample_count": valid_count, "invalid_sample_count": invalid_count}
    return record, samples, facts


DEVICE_KEYS = frozenset({"status", "provider", "scope", "samples", "unavailable_reason"})
DEVICE_SAMPLE_KEYS = frozenset({"status", "provider", "scope", "captured_at_utc", "exit_code", "raw_csv", "unavailable_reason"})


def _validate_measured_device_sample(item: dict[str, Any]) -> None:
    _integer(item["exit_code"], "device snapshot exit_code", maximum=0)
    if not isinstance(item["raw_csv"], str) or not item["raw_csv"].strip() or item["unavailable_reason"] != "":
        raise ProfileError("measured device snapshot must include successful raw nvidia-smi output")
    try:
        columns = next(csv.reader([item["raw_csv"]], skipinitialspace=True))
    except (csv.Error, StopIteration):
        raise ProfileError("device snapshot CSV is invalid") from None
    if len(columns) != 8 or any(not column.strip() for column in columns):
        raise ProfileError("device snapshot must preserve all eight requested device fields")


def _validate_unavailable_device_sample(item: dict[str, Any], index: int) -> None:
    _integer(item["exit_code"], f"device_snapshot.samples[{index}].exit_code", minimum=-1)
    if item["raw_csv"] != "" or not isinstance(item["unavailable_reason"], str) or not item["unavailable_reason"].strip():
        raise ProfileError("unavailable device snapshot must state a cause and contain no raw data")


def _validate_device_sample(index: int, sample: Any) -> bool:
    label = f"device_snapshot.samples[{index}]"
    item = _exact_object(sample, DEVICE_SAMPLE_KEYS, label)
    if item["provider"] != "nvidia-smi" or item["scope"] != "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED":
        raise ProfileError("device snapshot sample provenance is invalid")
    _timestamp(item["captured_at_utc"], label + ".captured_at_utc")
    if item["status"] == "MEASURED":
        _validate_measured_device_sample(item)
        return True
    if item["status"] == "UNAVAILABLE":
        _validate_unavailable_device_sample(item, index)
        return False
    raise ProfileError("device snapshot sample has a spoofed status")


def _validate_device_snapshot(value: Any) -> dict[str, Any]:
    device = _exact_object(value, DEVICE_KEYS, "device_snapshot")
    if device["provider"] != "nvidia-smi --query-gpu (device-wide; never process-attributed under WDDM)":
        raise ProfileError("device snapshot provider is not independently labeled")
    if device["scope"] != "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED":
        raise ProfileError("device-wide telemetry must not be attributed to the Godot process")
    if device["status"] not in {"MEASURED", "UNAVAILABLE"}:
        raise ProfileError("device_snapshot.status is not an allowed status")
    samples = device["samples"]
    if type(samples) is not list or len(samples) > 2:
        raise ProfileError("device_snapshot.samples must contain at most the start/end snapshots")
    measured = sum(_validate_device_sample(index, sample) for index, sample in enumerate(samples))
    _validate_device_snapshot_status(device, measured)
    return {"status": device["status"], "sample_count": measured}


def _validate_device_snapshot_status(device: dict[str, Any], measured: int) -> None:
    if device["status"] == "MEASURED":
        if measured == 0 or device["unavailable_reason"] != "":
            raise ProfileError("MEASURED device snapshot has no successful sample")
        return
    reason = device["unavailable_reason"]
    if measured > 0 or not isinstance(reason, str) or not reason.strip():
        raise ProfileError("UNAVAILABLE device snapshot has measured data or no cause")


def _validate_profile_identity(report: dict[str, Any]) -> tuple[str, str]:
    if report["schema_version"] != SCHEMA_VERSION:
        raise ProfileError("unsupported schema_version")
    run_id = _text(report["run_id"], "run_id")
    if not RUN_ID_RE.fullmatch(run_id):
        raise ProfileError("run_id format is invalid")
    run_status = report["run_status"]
    if run_status not in {"COMPLETE", "INVALID"}:
        raise ProfileError("run_status is not allowed")
    _text(report["run_reason"], "run_reason")
    _timestamp(report["captured_at_utc"], "captured_at_utc")
    if not isinstance(report["source_sha"], str) or not SHA1_RE.fullmatch(report["source_sha"]):
        raise ProfileError("source_sha must be a full lowercase Git SHA-1")
    for key in ("godot_version", "os", "display", "renderer", "driver", "adapter"):
        _text(report[key], key)
    if not report["godot_version"].startswith("4.7.2"):
        raise ProfileError("profile must identify pinned Godot 4.7.2")
    return run_id, run_status


def _validate_viewport(value: Any) -> None:
    viewport = _exact_object(value, frozenset({"rid", "resolution_px"}), "viewport")
    _text(viewport["rid"], "viewport.rid")
    resolution = viewport["resolution_px"]
    if type(resolution) is not list or len(resolution) != 2:
        raise ProfileError("viewport.resolution_px must be [width,height]")
    for index, dimension in enumerate(resolution):
        _integer(dimension, f"viewport.resolution_px[{index}]", minimum=1, maximum=16384)


def _validate_workload(value: Any) -> tuple[int, str]:
    workload = _exact_object(value, frozenset({"scene", "proxy_count", "effect_mode", "layout"}), "workload")
    if workload["scene"] != "Density Ladder" or workload["layout"] != "built-in deterministic grid":
        raise ProfileError("workload scene/layout provenance is invalid")
    count = _integer(workload["proxy_count"], "workload.proxy_count", minimum=1, maximum=200)
    mode = workload["effect_mode"]
    if count not in ALLOWED_COUNTS or mode not in ALLOWED_MODES:
        raise ProfileError("unsupported Density Ladder workload")
    if mode == "combined" and count != 25:
        raise ProfileError("the authorized combined workload is bounded to 25 proxies")
    return count, mode


def _validate_settings(value: Any) -> None:
    settings = _exact_object(value, frozenset({"vsync_mode", "max_fps"}), "settings")
    _integer(settings["vsync_mode"], "settings.vsync_mode", maximum=10)
    _integer(settings["max_fps"], "settings.max_fps", maximum=100_000)


def _validate_measurement(value: Any) -> tuple[float, int]:
    measurement = _exact_object(value, MEASUREMENT_KEYS, "measurement")
    if measurement["provider"] != "Godot RenderingServer per-viewport render timing":
        raise ProfileError("measurement provider is invalid")
    warmup = _finite_number(measurement["warmup_seconds"], "measurement.warmup_seconds", maximum=2.0)
    requested = _finite_number(measurement["requested_seconds"], "measurement.requested_seconds", maximum=30.0)
    if not math.isclose(warmup, 2.0, rel_tol=0.0, abs_tol=LOCKED_DURATION_TOLERANCE_SECONDS):
        raise ProfileError("profile must use the locked 2s warmup and 30s observation")
    if not math.isclose(requested, 30.0, rel_tol=0.0, abs_tol=LOCKED_DURATION_TOLERANCE_SECONDS):
        raise ProfileError("profile must use the locked 2s warmup and 30s observation")
    observed = _finite_number(measurement["observed_seconds"], "measurement.observed_seconds", maximum=30.1)
    _integer(measurement["warmup_frames_discarded"], "measurement.warmup_frames_discarded")
    invalid_loop = _integer(measurement["invalid_main_loop_samples"], "measurement.invalid_main_loop_samples")
    if measurement["percentile_method"] != "nearest_rank" or measurement["formula_version"] != FORMULA_VERSION:
        raise ProfileError("percentile or 1% low formula version is unsupported")
    if measurement["one_percent_low_fps_formula"] != "1000 / mean(slowest ceil(0.01*n) positive MAIN_LOOP_INTERVAL_MS samples)":
        raise ProfileError("1% low formula must be explicitly tied to MAIN_LOOP_INTERVAL_MS")
    _text(measurement["temporal_alignment_note"], "measurement.temporal_alignment_note")
    return observed, invalid_loop


def _validate_series_collection(
    value: Any, invalid_loop: int, observed: float
) -> tuple[dict[str, dict[str, Any]], dict[str, list[float]], dict[str, Any]]:
    series_value = _exact_object(value, frozenset(SERIES_SPECS), "series")
    series_facts: dict[str, dict[str, Any]] = {}
    raw_samples: dict[str, list[float]] = {}
    for name in SERIES_SPECS:
        _, samples, facts = _validate_series(name, series_value[name])
        series_facts[name] = facts
        raw_samples[name] = samples
    if invalid_loop != series_facts["MAIN_LOOP_INTERVAL_MS"]["invalid_sample_count"]:
        raise ProfileError("measurement invalid main-loop count differs from its raw series")
    main_loop = raw_samples["MAIN_LOOP_INTERVAL_MS"]
    if not math.isclose(math.fsum(main_loop) / 1000.0, observed, rel_tol=1e-5, abs_tol=0.05):
        raise ProfileError("observed_seconds differs from raw MAIN_LOOP_INTERVAL_MS coverage")
    main_record = series_value["MAIN_LOOP_INTERVAL_MS"]
    return series_facts, raw_samples, main_record


def _validate_one_percent_low(measurement: dict[str, Any], main_record: dict[str, Any], main_loop: list[float]) -> None:
    if main_record["status"] == "MEASURED":
        expected_low = _one_percent_low_fps(main_loop)
        actual_low = _finite_number(measurement["one_percent_low_fps"], "measurement.one_percent_low_fps", maximum=100_000.0)
        _close(actual_low, expected_low, "measurement.one_percent_low_fps")
    elif measurement["one_percent_low_fps"] is not None:
        raise ProfileError("1% low FPS must be unavailable when main-loop samples are insufficient")


def _validate_run_completion(run_status: str, run_reason: str, observed: float, main_record: dict[str, Any]) -> None:
    if run_status == "COMPLETE":
        if run_reason != "requested_observation_window_elapsed" or observed < 29.9:
            raise ProfileError("COMPLETE requires the full requested observation window")
        if main_record["status"] != "MEASURED":
            raise ProfileError("COMPLETE requires measured MAIN_LOOP_INTERVAL_MS")
        return
    if run_reason not in {
        "unsafe_main_loop_interval", "viewport_changed_or_unavailable",
        "sample_cap_reached_before_requested_duration",
    }:
        raise ProfileError("INVALID run reason is not an explicit supported stop condition")


def _validation_result(
    report: dict[str, Any],
    run_id: str,
    run_status: str,
    count: int,
    mode: str,
    observed: float,
    measurement: dict[str, Any],
    series_facts: dict[str, dict[str, Any]],
    raw_samples: dict[str, list[float]],
    device_facts: dict[str, Any],
) -> dict[str, Any]:
    validated_series = {
        name: {
            **series_facts[name],
            "aggregates": _aggregates(raw_samples[name]) if series_facts[name]["status"] == "MEASURED" else None,
        }
        for name in SERIES_SPECS
    }
    return {
        "status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "run_status": run_status,
        "source_sha": report["source_sha"],
        "workload": {"proxy_count": count, "effect_mode": mode},
        "observed_seconds": observed,
        "series": validated_series,
        "one_percent_low_fps": measurement["one_percent_low_fps"],
        "device_snapshot": device_facts,
        "limitations": "Per-viewport render time is not input-to-photon; renderer allocation is not total VRAM; device-wide WDDM memory is not process-attributed.",
    }


def validate_report(document: Any) -> dict[str, Any]:
    """Validate a complete bounded report and return independently computed metrics."""
    report = _exact_object(document, TOP_KEYS, "profile")
    run_id, run_status = _validate_profile_identity(report)
    _validate_viewport(report["viewport"])
    count, mode = _validate_workload(report["workload"])
    _validate_settings(report["settings"])
    measurement = _exact_object(report["measurement"], MEASUREMENT_KEYS, "measurement")
    observed, invalid_loop = _validate_measurement(measurement)
    series_facts, raw_samples, main_record = _validate_series_collection(report["series"], invalid_loop, observed)
    main_loop = raw_samples["MAIN_LOOP_INTERVAL_MS"]
    _validate_one_percent_low(measurement, main_record, main_loop)
    _validate_run_completion(run_status, report["run_reason"], observed, main_record)
    device_facts = _validate_device_snapshot(report["device_snapshot"])
    return _validation_result(report, run_id, run_status, count, mode, observed, measurement, series_facts, raw_samples, device_facts)


def validate_payload(payload: bytes) -> dict[str, Any]:
    if len(payload) > MAX_BYTES:
        raise ProfileError("profile input exceeds 8 MB limit")
    try:
        document = json.loads(
            payload.decode("utf-8-sig"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileError("invalid UTF-8 profile JSON: " + str(exc)) from None
    return validate_report(document)


def main(input_bytes: bytes | None = None) -> int:
    try:
        payload = sys.stdin.buffer.read(MAX_BYTES + 1) if input_bytes is None else input_bytes
        result = validate_payload(payload)
    except (ProfileError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

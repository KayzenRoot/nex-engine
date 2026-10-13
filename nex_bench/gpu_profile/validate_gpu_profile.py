"""Strict, bounded validator for versioned nex_gpu_render_profile exports.

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


SCHEMA_VERSION = "nex_gpu_render_profile.v2"
LEGACY_SCHEMA_VERSION = "nex_gpu_render_profile.v1"
FORMULA_VERSION_V1 = "nex-percentile-and-one-percent-low-v1"
FORMULA_VERSION_V2 = "nex-percentile-and-one-percent-low-monotonic-v2"
FRAME_PACING_PROVIDER = "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback"
FRAME_PACING_FORMULA = "1000 / mean(slowest ceil(0.01*n) positive FRAME_PACING_INTERVAL_MS samples)"
MAX_BYTES = 8_000_000
MAX_SAMPLES = 16_000
MIN_VALID_SAMPLES = 300
MAX_SAFE_INTEGER = 9_007_199_254_740_991
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_RE = re.compile(r"^\d{10,}-\d{6,}$", re.ASCII)
SERIES_PREFIX = "series."
LOCKED_DURATION_TOLERANCE_SECONDS = 1e-9
INVALID_V2_OBSERVED_SECONDS_ERROR = "measurement.observed_seconds must be finite and non-negative for an invalid v2 run"
DELTA_DERIVED_ONE_PERCENT_LOW_FIELD = "measurement.delta_derived_one_percent_low_fps"
ALLOWED_COUNTS = frozenset({25, 50, 100, 200})
ALLOWED_MODES = frozenset({"geometry", "lights", "vfx", "combined"})
TOP_KEYS = frozenset({
    "schema_version", "run_id", "run_status", "run_reason", "captured_at_utc",
    "source_sha", "godot_version", "os", "display", "renderer", "driver",
    "adapter", "viewport", "workload", "settings", "measurement", "series",
    "device_snapshot",
})
SERIES_SPECS_V1 = {
    "GPU_RENDER_MS": ("ms", "RenderingServer.viewport_get_measured_render_time_gpu", 60_000.0),
    "CPU_RENDER_MS": ("ms", "RenderingServer.viewport_get_measured_render_time_cpu", 60_000.0),
    "MAIN_LOOP_INTERVAL_MS": ("ms", "SceneTree._process(delta)", 1000.0),
    "RENDERER_ALLOCATION_BYTES": ("bytes", "Performance.RENDER_VIDEO_MEM_USED", MAX_SAFE_INTEGER),
}
SERIES_SPECS_V2 = {
    **SERIES_SPECS_V1,
    "FRAME_PACING_INTERVAL_MS": ("ms", FRAME_PACING_PROVIDER, 1000.0),
}
MEASUREMENT_KEYS_V1 = frozenset({
    "provider", "warmup_seconds", "requested_seconds", "observed_seconds",
    "warmup_frames_discarded", "invalid_main_loop_samples", "percentile_method",
    "formula_version", "one_percent_low_fps_formula", "one_percent_low_fps",
    "temporal_alignment_note",
})
MEASUREMENT_KEYS_V2 = MEASUREMENT_KEYS_V1 | frozenset({
    "one_percent_low_fps_source", "frame_pacing_provider", "frame_pacing_status",
    "frame_pacing_unavailable_reason", "invalid_frame_pacing_samples",
    "delta_derived_one_percent_low_fps_label", "delta_derived_one_percent_low_fps",
    "frame_pacing_limitation",
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
        if name in {"MAIN_LOOP_INTERVAL_MS", "FRAME_PACING_INTERVAL_MS"} and metric >= 1000.0:
            raise ProfileError(name.lower() + " must be below 1000 ms")
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


def _validate_unavailable_series(
    record: dict[str, Any], valid_count: int, *, allow_partial_samples: bool = False
) -> None:
    reason = record["unavailable_reason"]
    if not isinstance(reason, str) or not reason.strip():
        raise ProfileError("UNAVAILABLE series must state a cause")
    if (valid_count >= MIN_VALID_SAMPLES and not allow_partial_samples) or record["aggregates"] is not None:
        raise ProfileError("UNAVAILABLE series cannot hide enough measured samples or claim aggregates")


def _validate_series(
    name: str,
    value: Any,
    series_specs: dict[str, tuple[str, str, float]],
    *,
    allow_partial_unavailable: bool = False,
) -> tuple[dict[str, Any], list[float], dict[str, Any]]:
    unit, provider, maximum = series_specs[name]
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
        if allow_partial_unavailable and valid_count >= MIN_VALID_SAMPLES and invalid_count == 0:
            raise ProfileError(label + " cannot discard valid ticks without a recorded invalid sample")
        _validate_unavailable_series(record, valid_count, allow_partial_samples=allow_partial_unavailable)
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


def _validate_profile_identity(report: dict[str, Any]) -> tuple[str, str, str]:
    schema_version = report["schema_version"]
    if schema_version not in {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}:
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
    return run_id, run_status, schema_version


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


def _validate_locked_measurement_timing(measurement: dict[str, Any]) -> None:
    warmup = _finite_number(measurement["warmup_seconds"], "measurement.warmup_seconds", maximum=2.0)
    requested = _finite_number(measurement["requested_seconds"], "measurement.requested_seconds", maximum=30.0)
    if not math.isclose(warmup, 2.0, rel_tol=0.0, abs_tol=LOCKED_DURATION_TOLERANCE_SECONDS):
        raise ProfileError("profile must use the locked 2s warmup and 30s observation")
    if not math.isclose(requested, 30.0, rel_tol=0.0, abs_tol=LOCKED_DURATION_TOLERANCE_SECONDS):
        raise ProfileError("profile must use the locked 2s warmup and 30s observation")


def _validate_observed_seconds(measurement: dict[str, Any], schema_version: str, run_status: str) -> float:
    if schema_version != SCHEMA_VERSION or run_status != "INVALID":
        return _finite_number(measurement["observed_seconds"], "measurement.observed_seconds", maximum=30.1)
    raw_observed = measurement["observed_seconds"]
    if type(raw_observed) not in (int, float):
        raise ProfileError(INVALID_V2_OBSERVED_SECONDS_ERROR)
    try:
        observed = float(raw_observed)
    except (OverflowError, ValueError):
        raise ProfileError(INVALID_V2_OBSERVED_SECONDS_ERROR) from None
    if not math.isfinite(observed) or not 0.0 <= observed <= 30.1:
        raise ProfileError(INVALID_V2_OBSERVED_SECONDS_ERROR)
    return observed


def _validate_measurement_formula(measurement: dict[str, Any], schema_version: str) -> None:
    expected_version = FORMULA_VERSION_V1 if schema_version == LEGACY_SCHEMA_VERSION else FORMULA_VERSION_V2
    expected_low_formula = (
        "1000 / mean(slowest ceil(0.01*n) positive MAIN_LOOP_INTERVAL_MS samples)"
        if schema_version == LEGACY_SCHEMA_VERSION else FRAME_PACING_FORMULA
    )
    if measurement["percentile_method"] != "nearest_rank" or measurement["formula_version"] != expected_version:
        raise ProfileError("percentile or 1% low formula version is unsupported")
    if measurement["one_percent_low_fps_formula"] != expected_low_formula:
        raise ProfileError("1% low formula is not tied to the schema's declared interval series")
    _text(measurement["temporal_alignment_note"], "measurement.temporal_alignment_note")


def _validate_frame_pacing_status(measurement: dict[str, Any]) -> int:
    if measurement["one_percent_low_fps_source"] != "FRAME_PACING_INTERVAL_MS":
        raise ProfileError("v2 1% low source must be monotonic frame pacing")
    if measurement["frame_pacing_provider"] != FRAME_PACING_PROVIDER:
        raise ProfileError("v2 frame pacing provider is invalid")
    status = measurement["frame_pacing_status"]
    if status not in {"MEASURED", "UNAVAILABLE"}:
        raise ProfileError("v2 frame pacing status is invalid")
    frame_reason = measurement["frame_pacing_unavailable_reason"]
    if status == "MEASURED" and frame_reason != "":
        raise ProfileError("MEASURED frame pacing cannot include an unavailable reason")
    if status == "UNAVAILABLE" and (not isinstance(frame_reason, str) or not frame_reason.strip()):
        raise ProfileError("UNAVAILABLE frame pacing must state a cause")
    invalid_count = _integer(measurement["invalid_frame_pacing_samples"], "measurement.invalid_frame_pacing_samples")
    if status == "MEASURED" and invalid_count != 0:
        raise ProfileError("MEASURED frame pacing cannot contain invalid monotonic ticks")
    if "invalid_monotonic_tick" in frame_reason and invalid_count == 0:
        raise ProfileError("invalid monotonic tick reason requires a positive invalid tick count")
    return invalid_count


def _validate_frame_pacing_derived(measurement: dict[str, Any]) -> None:
    if measurement["delta_derived_one_percent_low_fps_label"] != "DELTA_DERIVED_VSYNC_LIMITED":
        raise ProfileError("legacy delta-derived FPS must be labeled DELTA_DERIVED_VSYNC_LIMITED")
    delta_low = measurement["delta_derived_one_percent_low_fps"]
    if delta_low is not None:
        _finite_number(delta_low, DELTA_DERIVED_ONE_PERCENT_LOW_FIELD, maximum=100_000.0)
    _text(measurement["frame_pacing_limitation"], "measurement.frame_pacing_limitation")


def _validate_measurement(value: Any, schema_version: str, run_status: str) -> tuple[dict[str, Any], float, int, int]:
    measurement_keys = MEASUREMENT_KEYS_V1 if schema_version == LEGACY_SCHEMA_VERSION else MEASUREMENT_KEYS_V2
    measurement = _exact_object(value, measurement_keys, "measurement")
    if measurement["provider"] != "Godot RenderingServer per-viewport render timing":
        raise ProfileError("measurement provider is invalid")
    _validate_locked_measurement_timing(measurement)
    observed = _validate_observed_seconds(measurement, schema_version, run_status)
    _integer(measurement["warmup_frames_discarded"], "measurement.warmup_frames_discarded")
    invalid_loop = _integer(measurement["invalid_main_loop_samples"], "measurement.invalid_main_loop_samples")
    _validate_measurement_formula(measurement, schema_version)
    invalid_frame_pacing = 0
    if schema_version == SCHEMA_VERSION:
        invalid_frame_pacing = _validate_frame_pacing_status(measurement)
        _validate_frame_pacing_derived(measurement)
    return measurement, observed, invalid_loop, invalid_frame_pacing

def _validate_interval_coverage(samples: list[float], observed: float, label: str) -> None:
    if not math.isclose(math.fsum(samples) / 1000.0, observed, rel_tol=1e-5, abs_tol=0.05):
        raise ProfileError(label)


def _validate_v2_pacing_consistency(
    series_value: dict[str, Any],
    series_facts: dict[str, dict[str, Any]],
    raw_samples: dict[str, list[float]],
    measurement: dict[str, Any],
    invalid_frame_pacing: int,
    observed: float,
) -> None:
    record = series_value["FRAME_PACING_INTERVAL_MS"]
    facts = series_facts["FRAME_PACING_INTERVAL_MS"]
    if invalid_frame_pacing != facts["invalid_sample_count"]:
        raise ProfileError("measurement invalid frame-pacing count differs from its raw series")
    if measurement["frame_pacing_status"] != facts["status"]:
        raise ProfileError("measurement frame-pacing status differs from its series")
    if measurement["frame_pacing_unavailable_reason"] != record["unavailable_reason"]:
        raise ProfileError("measurement frame-pacing reason differs from its series")
    _validate_interval_coverage(
        raw_samples["FRAME_PACING_INTERVAL_MS"], observed,
        "observed_seconds differs from monotonic FRAME_PACING_INTERVAL_MS coverage",
    )


def _validate_series_collection(
    value: Any,
    invalid_loop: int,
    invalid_frame_pacing: int,
    observed: float,
    schema_version: str,
    measurement: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[float]], dict[str, dict[str, Any]]]:
    series_specs = SERIES_SPECS_V1 if schema_version == LEGACY_SCHEMA_VERSION else SERIES_SPECS_V2
    series_value = _exact_object(value, frozenset(series_specs), "series")
    series_facts: dict[str, dict[str, Any]] = {}
    raw_samples: dict[str, list[float]] = {}
    for name in series_specs:
        _, samples, facts = _validate_series(
            name,
            series_value[name],
            series_specs,
            allow_partial_unavailable=(schema_version == SCHEMA_VERSION and name == "FRAME_PACING_INTERVAL_MS"),
        )
        series_facts[name] = facts
        raw_samples[name] = samples
    if invalid_loop != series_facts["MAIN_LOOP_INTERVAL_MS"]["invalid_sample_count"]:
        raise ProfileError("measurement invalid main-loop count differs from its raw series")
    if schema_version == LEGACY_SCHEMA_VERSION:
        _validate_interval_coverage(
            raw_samples["MAIN_LOOP_INTERVAL_MS"], observed,
            "observed_seconds differs from raw MAIN_LOOP_INTERVAL_MS coverage",
        )
    else:
        _validate_v2_pacing_consistency(
            series_value, series_facts, raw_samples, measurement, invalid_frame_pacing, observed
        )
    return series_facts, raw_samples, series_value

def _validate_delta_derived_one_percent_low(
    measurement: dict[str, Any],
    series_records: dict[str, dict[str, Any]],
    raw_samples: dict[str, list[float]],
) -> None:
    main_record = series_records["MAIN_LOOP_INTERVAL_MS"]
    delta_low = measurement["delta_derived_one_percent_low_fps"]
    if main_record["status"] == "MEASURED":
        if delta_low is None:
            raise ProfileError("delta-derived diagnostic is missing despite measured MAIN_LOOP_INTERVAL_MS")
        _close(
            _finite_number(delta_low, DELTA_DERIVED_ONE_PERCENT_LOW_FIELD, maximum=100_000.0),
            _one_percent_low_fps(raw_samples["MAIN_LOOP_INTERVAL_MS"]),
            DELTA_DERIVED_ONE_PERCENT_LOW_FIELD,
        )
    elif delta_low is not None:
        raise ProfileError("delta-derived diagnostic must be unavailable when MAIN_LOOP_INTERVAL_MS is unavailable")


def _validate_one_percent_low(
    measurement: dict[str, Any],
    series_records: dict[str, dict[str, Any]],
    raw_samples: dict[str, list[float]],
    schema_version: str,
) -> None:
    source = "MAIN_LOOP_INTERVAL_MS" if schema_version == LEGACY_SCHEMA_VERSION else "FRAME_PACING_INTERVAL_MS"
    record = series_records[source]
    if record["status"] == "MEASURED":
        expected_low = _one_percent_low_fps(raw_samples[source])
        actual_low = _finite_number(measurement["one_percent_low_fps"], "measurement.one_percent_low_fps", maximum=100_000.0)
        _close(actual_low, expected_low, "measurement.one_percent_low_fps")
    elif measurement["one_percent_low_fps"] is not None:
        raise ProfileError("1% low FPS must be unavailable when its authoritative interval series is unavailable")
    if schema_version == SCHEMA_VERSION:
        _validate_delta_derived_one_percent_low(measurement, series_records, raw_samples)

def _validate_invalid_run_reason(
    run_reason: str, schema_version: str, series_records: dict[str, dict[str, Any]]
) -> None:
    if run_reason not in {
        "unsafe_main_loop_interval", "viewport_changed_or_unavailable",
        "sample_cap_reached_before_requested_duration", "invalid_monotonic_tick",
        "insufficient_frame_pacing_samples",
    }:
        raise ProfileError("INVALID run reason is not an explicit supported stop condition")
    if schema_version != SCHEMA_VERSION:
        return
    if run_reason == "invalid_monotonic_tick":
        pacing_record = series_records["FRAME_PACING_INTERVAL_MS"]
        if pacing_record["status"] != "UNAVAILABLE" or int(pacing_record["invalid_sample_count"]) < 1:
            raise ProfileError("invalid_monotonic_tick must fail closed with an unavailable frame-pacing series")
    if run_reason == "insufficient_frame_pacing_samples":
        pacing_record = series_records["FRAME_PACING_INTERVAL_MS"]
        if pacing_record["status"] != "UNAVAILABLE" or int(pacing_record["valid_sample_count"]) >= MIN_VALID_SAMPLES:
            raise ProfileError("insufficient frame-pacing run must remain unavailable below the sample threshold")


def _validate_run_completion(
    run_status: str,
    run_reason: str,
    observed: float,
    series_records: dict[str, dict[str, Any]],
    schema_version: str,
) -> None:
    source = "MAIN_LOOP_INTERVAL_MS" if schema_version == LEGACY_SCHEMA_VERSION else "FRAME_PACING_INTERVAL_MS"
    if run_status == "COMPLETE":
        if run_reason != "requested_observation_window_elapsed" or observed < 29.9:
            raise ProfileError("COMPLETE requires the full requested observation window")
        if series_records[source]["status"] != "MEASURED":
            raise ProfileError("COMPLETE requires its schema's authoritative frame-interval series to be MEASURED")
        return
    _validate_invalid_run_reason(run_reason, schema_version, series_records)

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
        for name in series_facts
    }
    return {
        "status": "PASS",
        "schema_version": report["schema_version"],
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
    run_id, run_status, schema_version = _validate_profile_identity(report)
    _validate_viewport(report["viewport"])
    count, mode = _validate_workload(report["workload"])
    _validate_settings(report["settings"])
    measurement, observed, invalid_loop, invalid_frame_pacing = _validate_measurement(
        report["measurement"], schema_version, run_status
    )
    series_facts, raw_samples, series_records = _validate_series_collection(
        report["series"], invalid_loop, invalid_frame_pacing, observed, schema_version, measurement
    )
    _validate_one_percent_low(measurement, series_records, raw_samples, schema_version)
    _validate_run_completion(run_status, report["run_reason"], observed, series_records, schema_version)
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

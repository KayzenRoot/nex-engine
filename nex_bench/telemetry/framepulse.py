"""Deterministic analysis of synthetic telemetry_run.v1 traces.

This module validates a deliberately bounded subset of the pinned contract. It
does not implement a full Draft 2020-12 JSON Schema validator and never measures
hardware or claims real frame-rate performance.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any


class FramePulseError(ValueError):
    """Raised when a telemetry trace violates the supported v1 contract."""


_ROOT_KEYS = {
    "schema_version",
    "run_id",
    "git_sha",
    "scene_id",
    "scene_sha256",
    "renderer_id",
    "toolchain",
    "execution_mode",
    "clock",
    "frame_time_unit",
    "warmup_count",
    "sample_count",
    "samples",
    "gpu",
    "vram",
}
_RENDERERS = {
    "godot.forward_plus",
    "godot.mobile",
    "godot.compatibility",
}
_RUN_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
_SCENE_ID = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SCENE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAX_SAMPLE_COUNT = 1_000_000


def _duplicate_checked_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise FramePulseError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _finite_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise FramePulseError("JSON number must be finite")
    return value


def _reject_json_constant(token: str) -> None:
    raise FramePulseError(f"non-standard JSON number is not allowed: {token}")


def analyze_json(text: str, *, slow_frame_threshold_ms: float = 33.333) -> dict[str, Any]:
    """Parse strict JSON and return deterministic synthetic-only metrics."""
    if not isinstance(text, str):
        raise FramePulseError("JSON input must be text")
    try:
        run = json.loads(
            text,
            object_pairs_hook=_duplicate_checked_object,
            parse_float=_finite_json_float,
            parse_constant=_reject_json_constant,
        )
    except FramePulseError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError, OverflowError) as exc:
        raise FramePulseError(f"invalid JSON telemetry: {exc}") from exc
    return analyze_run(run, slow_frame_threshold_ms=slow_frame_threshold_ms)


def _object_with_keys(value: Any, label: str, expected: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FramePulseError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise FramePulseError(f"{label} has invalid fields ({'; '.join(details)})")
    return value


def _bounded_string(value: Any, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise FramePulseError(f"{label} must be a non-empty string of at most {maximum} characters")
    return value


def _contract_integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or value < minimum or value > maximum:
        raise FramePulseError(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FramePulseError(f"{label} must be a finite number")
    if isinstance(value, int):
        # Contract bounds are small, so check them before conversion to float.
        try:
            return float(value)
        except OverflowError as exc:
            raise FramePulseError(f"{label} must be a finite number") from exc
    if not math.isfinite(value):
        raise FramePulseError(f"{label} must be a finite number")
    return value


def _validate_source(value: Any, label: str) -> str:
    return _bounded_string(value, label, 512)


def _validate_hardware(value: Any, label: str, measurement: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FramePulseError(f"{label} must be an object")
    availability = value.get("availability")
    if availability == "UNAVAILABLE":
        hardware = _object_with_keys(value, label, {"availability", "source"})
        return {
            "availability": "UNAVAILABLE",
            "source": _validate_source(hardware["source"], f"{label}.source"),
        }
    if availability != "AVAILABLE":
        raise FramePulseError(f"{label}.availability must be AVAILABLE or UNAVAILABLE")

    hardware = _object_with_keys(value, label, {"availability", "source", measurement})
    source = _validate_source(hardware["source"], f"{label}.source")
    raw = hardware[measurement]
    if measurement == "utilization_percent":
        number = _finite_number(raw, f"{label}.{measurement}")
        if number < 0 or number > 100:
            raise FramePulseError(f"{label}.{measurement} must be between 0 and 100")
        normalized: int | float = raw
    else:
        normalized = _contract_integer(raw, f"{label}.{measurement}", 0, 9_007_199_254_740_991)
    return {
        "availability": "AVAILABLE",
        "source": source,
        measurement: normalized,
    }


def _validate_run(run: Any) -> tuple[dict[str, Any], list[float], dict[str, dict[str, Any]]]:
    telemetry = _object_with_keys(run, "telemetry run", _ROOT_KEYS)
    if telemetry["schema_version"] != "telemetry_run.v1":
        raise FramePulseError("schema_version must be telemetry_run.v1")

    run_id = telemetry["run_id"]
    _bounded_string(run_id, "run_id", 128)
    if not _RUN_ID.fullmatch(run_id):
        raise FramePulseError("run_id has invalid characters")

    git_sha = telemetry["git_sha"]
    if not isinstance(git_sha, str) or not _GIT_SHA.fullmatch(git_sha):
        raise FramePulseError("git_sha must be 40 lowercase hexadecimal characters")

    scene_id = telemetry["scene_id"]
    _bounded_string(scene_id, "scene_id", 128)
    if not _SCENE_ID.fullmatch(scene_id):
        raise FramePulseError("scene_id has invalid characters")

    scene_sha256 = telemetry["scene_sha256"]
    if not isinstance(scene_sha256, str) or not _SCENE_SHA256.fullmatch(scene_sha256):
        raise FramePulseError("scene_sha256 must be 64 lowercase hexadecimal characters")

    renderer_id = telemetry["renderer_id"]
    if not isinstance(renderer_id, str) or renderer_id not in _RENDERERS:
        raise FramePulseError("renderer_id is not a telemetry_run.v1 renderer")

    toolchain = _object_with_keys(
        telemetry["toolchain"], "toolchain", {"engine_version", "toolchain_id", "platform"}
    )
    for field in ("engine_version", "toolchain_id", "platform"):
        _bounded_string(toolchain[field], f"toolchain.{field}", 128)

    if telemetry["execution_mode"] != "synthetic":
        raise FramePulseError("FramePulse accepts only synthetic execution_mode")
    clock = _object_with_keys(telemetry["clock"], "clock", {"domain", "timestamp_unit"})
    if clock["domain"] != "monotonic" or clock["timestamp_unit"] != "ms":
        raise FramePulseError("clock must use a monotonic millisecond timestamp")
    if telemetry["frame_time_unit"] != "ms":
        raise FramePulseError("frame_time_unit must be ms")

    warmup_count = _contract_integer(
        telemetry["warmup_count"], "warmup_count", 0, _MAX_SAMPLE_COUNT
    )
    del warmup_count  # Validated for contract compatibility; warmup rows are not present.
    sample_count = _contract_integer(
        telemetry["sample_count"], "sample_count", 1, _MAX_SAMPLE_COUNT
    )
    samples = telemetry["samples"]
    if not isinstance(samples, list) or len(samples) != sample_count:
        raise FramePulseError("sample_count must equal the non-empty samples array length")
    if len(samples) > _MAX_SAMPLE_COUNT:
        raise FramePulseError("samples exceeds the telemetry_run.v1 maximum")

    frame_times: list[float] = []
    previous_timestamp: float | None = None
    for index, raw_sample in enumerate(samples):
        sample = _object_with_keys(
            raw_sample, f"samples[{index}]", {"timestamp_ms", "frame_time_ms"}
        )
        timestamp = _finite_number(sample["timestamp_ms"], f"samples[{index}].timestamp_ms")
        if timestamp < 0 or timestamp > 1_000_000_000_000_000:
            raise FramePulseError(
                f"samples[{index}].timestamp_ms is outside telemetry_run.v1 bounds"
            )
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            raise FramePulseError("timestamp_ms values must be strictly increasing")
        previous_timestamp = timestamp

        frame_time = _finite_number(sample["frame_time_ms"], f"samples[{index}].frame_time_ms")
        if frame_time <= 0 or frame_time > 60_000:
            raise FramePulseError(
                f"samples[{index}].frame_time_ms must be greater than 0 and at most 60000"
            )
        frame_times.append(frame_time)

    hardware = {
        "gpu": _validate_hardware(telemetry["gpu"], "gpu", "utilization_percent"),
        "vram": _validate_hardware(telemetry["vram"], "vram", "used_bytes"),
    }
    provenance = {
        "label": "SYNTHETIC_NOT_MEASURED",
        "schema_version": telemetry["schema_version"],
        "run_id": run_id,
        "git_sha": git_sha,
        "scene_id": scene_id,
        "scene_sha256": scene_sha256,
        "renderer_id": renderer_id,
        "toolchain": dict(toolchain),
        "execution_mode": telemetry["execution_mode"],
        "clock": dict(clock),
        "frame_time_unit": telemetry["frame_time_unit"],
        "warmup_count": telemetry["warmup_count"],
    }
    return provenance, frame_times, hardware


def _percentile(sorted_values: list[float], percentile: float) -> float:
    """Linear interpolation at position p * (N - 1), where p is in [0, 1]."""
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = percentile * (len(sorted_values) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return sorted_values[lower_index]
    fraction = position - lower_index
    return sorted_values[lower_index] + (
        sorted_values[upper_index] - sorted_values[lower_index]
    ) * fraction


def _stutter_clusters(frame_times: list[float], threshold_ms: float) -> list[dict[str, int]]:
    clusters: list[dict[str, int]] = []
    start: int | None = None
    for index, frame_time in enumerate(frame_times):
        if frame_time >= threshold_ms:
            if start is None:
                start = index
        elif start is not None:
            clusters.append(
                {"start_index": start, "end_index": index - 1, "frame_count": index - start}
            )
            start = None
    if start is not None:
        clusters.append(
            {
                "start_index": start,
                "end_index": len(frame_times) - 1,
                "frame_count": len(frame_times) - start,
            }
        )
    return clusters


def analyze_run(
    run: Any, *, slow_frame_threshold_ms: float = 33.333
) -> dict[str, Any]:
    """Analyze one synthetic telemetry_run.v1 object without hardware inference."""
    threshold = _finite_number(slow_frame_threshold_ms, "slow_frame_threshold_ms")
    if threshold <= 0:
        raise FramePulseError("slow_frame_threshold_ms must be greater than zero")

    provenance, frame_times, hardware = _validate_run(run)
    ordered = sorted(frame_times)
    sample_count = len(ordered)
    slowest_count = max(1, (sample_count + 99) // 100)
    slowest = sorted(frame_times, reverse=True)[:slowest_count]
    mean_slowest = math.fsum(slowest) / slowest_count
    clusters = _stutter_clusters(frame_times, threshold)

    return {
        "classification": "SYNTHETIC_NOT_MEASURED",
        "provenance": provenance,
        "sample_count": sample_count,
        "quantiles_ms": {
            "p50": _percentile(ordered, 0.50),
            "p95": _percentile(ordered, 0.95),
            "p99": _percentile(ordered, 0.99),
        },
        "synthetic_one_percent_sample_count": slowest_count,
        "synthetic_one_percent_low_fps": 1000.0 / mean_slowest,
        "slow_frame_threshold_ms": threshold,
        "slow_frame_count": sum(1 for value in frame_times if value >= threshold),
        "stutter_clusters": clusters,
        "hardware": hardware,
    }

"""Validate F10 main-loop frame observation JSON without inventing GPU metrics.

No third-party packages, network calls, destructive operations, or Godot dependency.
Only the single exported observation and its internally consistent aggregates are
validated. This is NOT proof of screenshot quality or real GPU frame time.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any


class ObservationError(ValueError):
    """An invalid, inconsistent or unsupported F10 observation."""


MAX_BYTES = 1_000_000
MIN_FRAMES = 60
MAX_FRAMES = 1500
ALLOWED_COUNTS = frozenset({25, 50, 100, 200})
ALLOWED_MODES = frozenset({"geometry", "lights", "vfx", "combined"})
MEASUREMENT = "OBSERVED_MAIN_LOOP_DELTA_NOT_GPU_TIME"


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ObservationError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ObservationError("non-JSON numeric constant: " + value)


def _number(report: dict[str, Any], key: str, *, positive: bool = False) -> float:
    value = report.get(key)
    if type(value) not in (int, float):
        raise ObservationError(key + " must be a JSON number")
    try:
        numeric = float(value)
    except (OverflowError, ValueError):
        raise ObservationError(key + " is not finite") from None
    if not math.isfinite(numeric) or (positive and numeric <= 0.0):
        raise ObservationError(key + " must be finite" + (" and positive" if positive else ""))
    return numeric


def _integer(report: dict[str, Any], key: str) -> int:
    value = report.get(key)
    if type(value) is not int:
        raise ObservationError(key + " must be an integer")
    return value


def _close(report: dict[str, Any], key: str, expected: float) -> None:
    value = _number(report, key, positive=True)
    # Godot JSON serialization can round floating point displays slightly.
    if not math.isclose(value, expected, rel_tol=1e-5, abs_tol=1e-3):
        raise ObservationError(key + " differs from independently computed samples")


def _percentile(sorted_samples: list[float], quantile: float) -> float:
    index = min(len(sorted_samples) - 1, max(0, math.ceil(quantile * len(sorted_samples)) - 1))
    return sorted_samples[index]


def validate_report(document: Any) -> dict[str, Any]:
    """Return recalculated, bounded validation facts; raise on any inconsistency."""
    if type(document) is not dict:
        raise ObservationError("observation must be a JSON object")
    if document.get("schema_version") != "nex_frame_observation.v1":
        raise ObservationError("unsupported schema_version")
    if document.get("measurement") != MEASUREMENT:
        raise ObservationError("missing main-loop-only provenance")
    if document.get("frame_intervals_units") != "ms":
        raise ObservationError("frame_intervals_units must be ms")
    if document.get("proxy_count") not in ALLOWED_COUNTS or type(document.get("proxy_count")) is not int:
        raise ObservationError("proxy_count must be one of 25/50/100/200")
    if document.get("effect_mode") not in ALLOWED_MODES:
        raise ObservationError("invalid effect_mode")
    for name in ("godot", "os", "renderer", "driver", "captured_at_utc"):
        if not isinstance(document.get(name), str) or not document[name].strip():
            raise ObservationError(name + " is missing")
    if not math.isclose(_number(document, "warmup_seconds", positive=True), 2.0):
        raise ObservationError("unexpected warmup_seconds")
    if not math.isclose(_number(document, "requested_seconds", positive=True), 8.0):
        raise ObservationError("unexpected requested_seconds")
    count = _integer(document, "sample_count")
    samples = document.get("frame_intervals_ms")
    if type(samples) is not list or not MIN_FRAMES <= len(samples) <= MAX_FRAMES:
        raise ObservationError("frame_intervals_ms must contain 60..1500 samples")
    if count != len(samples):
        raise ObservationError("sample_count differs from number of frame_intervals_ms")
    values: list[float] = []
    for position, value in enumerate(samples):
        if type(value) not in (int, float):
            raise ObservationError("frame interval contains a non-number at index " + str(position))
        try:
            numeric = float(value)
        except (OverflowError, ValueError):
            raise ObservationError("frame interval too large at index " + str(position)) from None
        if not math.isfinite(numeric) or not (0.0 < numeric < 1000.0):
            raise ObservationError("frame interval outside (0,1000) ms at index " + str(position))
        values.append(numeric)

    total_ms = math.fsum(values)
    mean_ms = total_ms / count
    ordered = sorted(values)
    expected = {
        "observed_seconds": total_ms / 1000.0,
        "mean_interval_ms": mean_ms,
        "p50_interval_ms": _percentile(ordered, 0.50),
        "p95_interval_ms": _percentile(ordered, 0.95),
        "p99_interval_ms": _percentile(ordered, 0.99),
        "observed_mean_fps": 1000.0 / mean_ms,
    }
    for key, calculated in expected.items():
        _close(document, key, calculated)
    return {
        "status": "PASS",
        "schema_version": document["schema_version"],
        "measurement": MEASUREMENT,
        "proxy_count": document["proxy_count"],
        "effect_mode": document["effect_mode"],
        "sample_count": count,
        "frame_intervals_units": "ms",
        "recalculated": expected,
        "limitations": "Main-loop delta only; VSync may cap intervals; not GPU time, GPU memory or input-to-photon.",
    }


def validate_file(source: Path) -> dict[str, Any]:
    if not source.is_file():
        raise ObservationError("observation file does not exist")
    if source.stat().st_size > MAX_BYTES:
        raise ObservationError("observation file exceeds 1 MB limit")
    try:
        document = json.loads(
            source.read_text(encoding="utf-8-sig"),
            object_pairs_hook=_object_pairs,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ObservationError("invalid UTF-8 JSON observation: " + str(exc)) from None
    return validate_report(document)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed independent F10 interval validation; NOT a GPU benchmark."
    )
    parser.add_argument("file", type=Path, help="Godot F10 frame_observations/density_*.json")
    args = parser.parse_args(argv)
    try:
        result = validate_file(args.file)
    except (ObservationError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

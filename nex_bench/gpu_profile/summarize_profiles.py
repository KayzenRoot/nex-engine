"""Read-only, fail-closed repeatability summary of validated NEX GPU v2 captures.

Accepts explicitly named local files, never overwrites captures or screenshots.
A mean of per-run 1% lows is NOT a pooled 1% low, display presentation
metric, causal A/B result, or evidence of extra GPU measurements.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import statistics
import sys
from typing import Any

if __package__:
    from .validate_gpu_profile import MAX_BYTES, ProfileError, SCHEMA_VERSION, validate_payload
else:
    from validate_gpu_profile import MAX_BYTES, ProfileError, SCHEMA_VERSION, validate_payload

MIN_REPEATS = 3
MAX_INPUTS = 24


def _device_driver_version(device: dict[str, Any]) -> str:
    versions: set[str] = set()
    for snapshot in device["samples"]:
        if snapshot["status"] != "MEASURED":
            continue
        for row in csv.reader(io.StringIO(snapshot["raw_csv"])):
            if len(row) >= 2 and row[1].strip():
                versions.add(row[1].strip())
    return next(iter(versions)) if len(versions) == 1 else "UNVERIFIED"


def _context(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": document["schema_version"],
        "source_sha": document["source_sha"],
        "godot_version": document["godot_version"],
        "os": document["os"],
        "display": document["display"],
        "renderer": document["renderer"],
        "driver": document["driver"],
        "adapter": document["adapter"],
        "device_driver_version": _device_driver_version(document["device_snapshot"]),
        "resolution_px": document["viewport"]["resolution_px"],
        "workload": document["workload"],
        "settings": document["settings"],
    }


def _read_profile(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise ProfileError("capture input must be a regular non-symlink file")
    with path.open("rb") as handle:
        payload = handle.read(MAX_BYTES + 1)
    verified = validate_payload(payload)
    if verified["schema_version"] != SCHEMA_VERSION:
        raise ProfileError("repeatability requires v2 callback pacing, not historic v1 1% low")
    if verified["run_status"] != "COMPLETE":
        raise ProfileError("repeatability cannot include incomplete or INVALID captures")
    document = json.loads(payload.decode("utf-8-sig"))
    return _context(document), verified


def _distribution(values: list[float]) -> dict[str, Any]:
    return {
        "per_run_values": values,
        "mean_of_run_values": round(statistics.fmean(values), 6),
        "median_of_run_values": round(statistics.median(values), 6),
        "minimum": round(min(values), 6),
        "maximum": round(max(values), 6),
        "range": round(max(values) - min(values), 6),
    }


def _series_metric(runs: list[dict[str, Any]], series_name: str, aggregate: str) -> dict[str, Any]:
    records = [run["series"][series_name] for run in runs]
    if any(record["status"] != "MEASURED" for record in records):
        return {
            "status": "INCONCLUSIVE",
            "reason": "one_or_more_runs_lack_measurement",
            "per_run_values": [
                record["aggregates"][aggregate] if record["status"] == "MEASURED" else None
                for record in records
            ],
        }
    return {
        "status": "MEASURED",
        **_distribution([float(record["aggregates"][aggregate]) for record in records]),
    }


def _group_summary(context: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(runs, key=lambda run: run["run_id"])
    return {
        "context": context,
        "repeat_count": len(ordered),
        "run_ids": [run["run_id"] for run in ordered],
        "environment_status": (
            "DRIVER_VERSION_UNVERIFIED"
            if context["device_driver_version"] == "UNVERIFIED" else "DRIVER_VERSION_RECORDED"
        ),
        "observed_seconds": _distribution([float(run["observed_seconds"]) for run in ordered]),
        "cpu_callback_one_percent_low_fps": {
            "status": "MEASURED_CALLBACK_ONLY",
            **_distribution([float(run["one_percent_low_fps"]) for run in ordered]),
        },
        "gpu_render_p95_ms_per_run": _series_metric(ordered, "GPU_RENDER_MS", "p95"),
        "cpu_render_p95_ms_per_run": _series_metric(ordered, "CPU_RENDER_MS", "p95"),
        "renderer_allocation_p95_bytes_per_run": _series_metric(
            ordered, "RENDERER_ALLOCATION_BYTES", "p95"
        ),
    }


def summarize(paths: list[Path]) -> dict[str, Any]:
    if not MIN_REPEATS <= len(paths) <= MAX_INPUTS:
        raise ProfileError("repeatability requires 3 to 24 explicitly selected input captures")
    groups: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    seen_run_ids: set[str] = set()
    for path in paths:
        context, verified = _read_profile(path)
        run_id = verified["run_id"]
        if run_id in seen_run_ids:
            raise ProfileError("duplicate run_id cannot count as an independent repeat")
        seen_run_ids.add(run_id)
        key = json.dumps(context, sort_keys=True, ensure_ascii=False)
        if key not in groups:
            groups[key] = (context, [])
        groups[key][1].append(verified)
    if any(len(runs) < MIN_REPEATS for _, runs in groups.values()):
        raise ProfileError("each identical source/environment/workload group needs 3 complete repeats")
    return {
        "status": "PASS",
        "schema_version": "nex_gpu_repeatability.v1",
        "source": "STRICT_V2_VALIDATED_RAW_CAPTURE",
        "captures_validated": len(seen_run_ids),
        "groups": [_group_summary(*groups[key]) for key in sorted(groups)],
        "limitations": [
            "No cross-group ranking or A/B inference; different workloads/settings are incomparable.",
            "Mean of per-run callback 1% lows is not the pooled raw-series 1% low.",
            "Callback pacing is not displayed-frame presentation or input-to-photon latency.",
            "Renderer allocation is not whole-device or process-attributed GPU VRAM.",
            "UNVERIFIED driver version and missing metrics remain explicit uncertainties.",
            "Repeatability is exploratory and does not assert 60/120 FPS playability.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize 3+ comparable, validated GPU v2 captures")
    parser.add_argument("captures", type=Path, nargs="+", help="explicit local JSON file paths")
    arguments = parser.parse_args(argv)
    try:
        result = summarize(arguments.captures)
    except (ProfileError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

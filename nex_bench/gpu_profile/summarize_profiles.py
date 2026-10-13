"""Summarize comparable NEX GPU v2 runs from bounded JSON on stdin only.

No file paths, file output, network, subprocesses, or GPU access. All runs
must independently satisfy the existing strict report validator. The returned
statistics are exploratory CPU-callback and per-viewport diagnostics only.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from typing import Any

if __package__:
    from .validate_gpu_profile import MAX_BYTES, ProfileError, SCHEMA_VERSION, validate_report
else:
    from validate_gpu_profile import MAX_BYTES, ProfileError, SCHEMA_VERSION, validate_report

MIN_REPEATS = 3
MAX_REPEATS = 12
MAX_BATCH_BYTES = 48_000_000


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError("batch contains a duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_non_json_number(value: str) -> None:
    raise ProfileError("batch contains a non-JSON number: " + value)


def _driver_version(document: dict[str, Any]) -> str | None:
    versions: set[str] = set()
    for snapshot in document["device_snapshot"]["samples"]:
        if snapshot["status"] == "MEASURED":
            columns = next(csv.reader([snapshot["raw_csv"]], skipinitialspace=True))
            versions.add(columns[1].strip())
    if len(versions) > 1:
        raise ProfileError("driver version drift within a single capture")
    return next(iter(versions)) if versions else None


def _context(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_sha": document["source_sha"],
        "godot_version": document["godot_version"],
        "os": document["os"],
        "display": document["display"],
        "renderer": document["renderer"],
        "driver": document["driver"],
        "adapter": document["adapter"],
        "nvidia_driver_version": _driver_version(document),
        "viewport_resolution_px": document["viewport"]["resolution_px"],
        "workload": document["workload"],
        "settings": document["settings"],
    }


def _distribution(values: list[float]) -> dict[str, Any]:
    if any(not math.isfinite(value) for value in values):
        raise ProfileError("aggregate contains a non-finite result")
    return {
        "per_run": values,
        "mean_of_run_metrics": statistics.fmean(values),
        "median_of_run_metrics": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "range": max(values) - min(values),
    }


def _series_p95(runs: list[dict[str, Any]], name: str) -> dict[str, Any]:
    records = [run["series"][name] for run in runs]
    if any(record["status"] != "MEASURED" for record in records):
        return {
            "status": "INCONCLUSIVE",
            "reason": "one_or_more_runs_unavailable",
            "per_run": [
                record["aggregates"]["p95"] if record["status"] == "MEASURED" else None
                for record in records
            ],
        }
    return {
        "status": "MEASURED",
        **_distribution([float(record["aggregates"]["p95"]) for record in records]),
    }


def summarize(batch: Any) -> dict[str, Any]:
    if type(batch) is not dict or frozenset(batch) != frozenset({"captures"}):
        raise ProfileError("batch must contain only the captures array")
    captures = batch["captures"]
    if type(captures) is not list or not MIN_REPEATS <= len(captures) <= MAX_REPEATS:
        raise ProfileError("batch requires 3 to 12 captured documents")
    verified_runs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    reference: dict[str, Any] | None = None
    for index, document in enumerate(captures):
        if type(document) is not dict:
            raise ProfileError("capture is not a JSON object")
        serialized = json.dumps(document, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        if len(serialized.encode("utf-8")) > MAX_BYTES:
            raise ProfileError("an individual capture exceeds the strict 8 MB budget")
        run = validate_report(document)
        if run["schema_version"] != SCHEMA_VERSION or run["run_status"] != "COMPLETE":
            raise ProfileError("repeatability requires COMPLETE v2 captures, not v1 or INVALID")
        if run["run_id"] in seen_ids:
            raise ProfileError("duplicate run_id is not an independent repetition")
        seen_ids.add(run["run_id"])
        current = _context(document)
        if reference is None:
            reference = current
        elif current != reference:
            raise ProfileError("mixed capture context at index " + str(index))
        verified_runs.append(run)
    verified_runs.sort(key=lambda item: item["run_id"])
    return {
        "status": "PASS",
        "schema_version": "nex_gpu_repeatability.v1",
        "context": reference,
        "repeat_count": len(verified_runs),
        "run_ids": [run["run_id"] for run in verified_runs],
        "cpu_callback_one_percent_low_fps": {
            "status": "MEASURED_CALLBACK_ONLY",
            **_distribution([float(run["one_percent_low_fps"]) for run in verified_runs]),
        },
        "gpu_render_p95_ms": _series_p95(verified_runs, "GPU_RENDER_MS"),
        "cpu_render_p95_ms": _series_p95(verified_runs, "CPU_RENDER_MS"),
        "renderer_allocation_p95_bytes": _series_p95(verified_runs, "RENDERER_ALLOCATION_BYTES"),
        "environment_status": (
            "NVIDIA_DRIVER_VERSION_UNVERIFIED"
            if reference["nvidia_driver_version"] is None else "DRIVER_VERSION_RECORDED"
        ),
        "limitations": [
            "Within ONE pinned source, environment, resolution, settings and workload only.",
            "Averaged per-run 1% lows are NOT a pooled raw-sample 1% low.",
            "Callback pacing is neither display presentation nor input-to-photon latency.",
            "Renderer allocation is not device-wide or process-attributed VRAM.",
            "Identical run IDs are rejected; truly independent hardware sessions cannot be proved.",
            "Complete reports on pre-R3 code do not independently prove resize invariance.",
            "No cross-workload performance ranking or production-FPS qualification.",
        ],
    }


def validate_batch_payload(payload: bytes) -> dict[str, Any]:
    if len(payload) > MAX_BATCH_BYTES:
        raise ProfileError("batch exceeds 48 MB input budget")
    try:
        document = json.loads(
            payload.decode("utf-8-sig"),
            object_pairs_hook=_unique_pairs,
            parse_constant=_reject_non_json_number,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileError("invalid UTF-8 JSON batch: " + str(exc)) from None
    return summarize(document)


def main(input_bytes: bytes | None = None) -> int:
    try:
        payload = (
            sys.stdin.buffer.read(MAX_BATCH_BYTES + 1)
            if input_bytes is None else input_bytes
        )
        result = validate_batch_payload(payload)
    except (ProfileError, OSError, ValueError, OverflowError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

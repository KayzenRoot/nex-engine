"""Shared loaders and statistics for the NEX M09 preset reports."""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from common import load_json

RUNS_SCHEMA = "preset_ab_runs.v1"
METRIC_KEYS = ("GPU_RENDER_MS", "CPU_RENDER_MS", "FRAME_PACING_INTERVAL_MS")
PERCENTILES = ("p50", "p95", "p99")


def load_manifest(path: Path, expected_runs: int, allowed_counts: tuple[int, ...] | None,
                  allowed_presets: tuple[str, ...]) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("schema_version") != RUNS_SCHEMA:
        raise ValueError("runs manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != expected_runs:
        raise ValueError(f"runs manifest must contain {expected_runs} runs")
    if [run.get("sequence") for run in runs] != list(range(1, expected_runs + 1)):
        raise ValueError(f"runs manifest sequence must be 1..{expected_runs}")
    if len({run.get("run_id") for run in runs}) != expected_runs:
        raise ValueError("runs manifest run ids must be unique")
    for run in runs:
        if run.get("preset_id") not in allowed_presets:
            raise ValueError("runs manifest preset is invalid")
        if allowed_counts is not None and run.get("proxy_count") not in allowed_counts:
            raise ValueError("runs manifest proxy count is invalid")
    return manifest


def load_capture(evidence: Path, run_id: str, scene: str, layout: str, count: int,
                 include_allocation: bool = False) -> dict[str, Any]:
    path = evidence / f"gpu_profile_{run_id}.json"
    if not path.is_file():
        raise ValueError(f"capture not found: {run_id}")
    document = load_json(path)
    if document.get("run_status") != "COMPLETE":
        raise ValueError(f"{run_id}: run_status is not COMPLETE")
    workload = document.get("workload", {})
    if (workload.get("scene") != scene or workload.get("layout") != layout
            or workload.get("proxy_count") != count or workload.get("effect_mode") != "lights"):
        raise ValueError(f"{run_id}: workload provenance is invalid")
    settings = document.get("settings", {})
    if settings.get("max_fps") != 240 or settings.get("vsync_mode") != 0:
        raise ValueError(f"{run_id}: settings provenance is invalid")
    series = document.get("series", {})
    metrics: dict[str, Any] = {}
    for key in METRIC_KEYS:
        entry = series.get(key, {})
        if entry.get("status") != "MEASURED":
            raise ValueError(f"{run_id}: {key} is not MEASURED")
        aggregates = entry.get("aggregates", {})
        metrics[key] = {name: float(aggregates[name]) for name in PERCENTILES}
    validation_path = evidence / f"gpu_profile_{run_id}.json.validation.json"
    validation = load_json(validation_path)
    if validation.get("status") != "PASS":
        raise ValueError(f"{run_id}: validation is not PASS")
    if validation.get("source_sha") != document.get("source_sha"):
        raise ValueError(f"{run_id}: validation source_sha mismatch")
    result = {
        "run_id": run_id,
        "source_sha": document.get("source_sha"),
        "captured_at_utc": document.get("captured_at_utc"),
        "metrics": metrics,
        "one_percent_low_fps": float(document["measurement"]["one_percent_low_fps"]),
        "observed_seconds": float(document["measurement"]["observed_seconds"]),
        "viewport": document.get("viewport", {}).get("resolution_px"),
    }
    if include_allocation:
        result["renderer_allocation_bytes"] = int(
            series["RENDERER_ALLOCATION_BYTES"]["aggregates"]["p50"]
        )
    return result


def metric_value(run: dict[str, Any], key: str, percentile: str = "p95") -> float:
    return float(run["metrics"][key][percentile])


def transform_run(entry: dict[str, Any], capture: dict[str, Any], include_allocation: bool = False) -> dict[str, Any]:
    run = {
        "sequence": entry["sequence"],
        "run_id": entry["run_id"],
        "preset_id": entry["preset_id"],
        "captured_at_utc": capture["captured_at_utc"],
        "observed_seconds": round(capture["observed_seconds"], 3),
        "gpu_ms": {name: round(capture["metrics"]["GPU_RENDER_MS"][name], 3) for name in PERCENTILES},
        "cpu_ms": {name: round(capture["metrics"]["CPU_RENDER_MS"][name], 3) for name in PERCENTILES},
        "pacing_ms": {name: round(capture["metrics"]["FRAME_PACING_INTERVAL_MS"][name], 3) for name in PERCENTILES},
        "one_percent_low_fps": round(capture["one_percent_low_fps"], 2),
    }
    if include_allocation:
        run["renderer_allocation_bytes"] = capture["renderer_allocation_bytes"]
    return run


def summarize(group: list[dict[str, Any]], include_allocation: bool = False) -> dict[str, Any]:
    result = {
        "runs": len(group),
        "gpu_p50_ms": round(median([run["gpu_ms"]["p50"] for run in group]), 3),
        "gpu_p95_ms": round(median([run["gpu_ms"]["p95"] for run in group]), 3),
        "gpu_p99_ms": round(median([run["gpu_ms"]["p99"] for run in group]), 3),
        "cpu_p95_ms": round(median([run["cpu_ms"]["p95"] for run in group]), 3),
        "pacing_p95_ms": round(median([run["pacing_ms"]["p95"] for run in group]), 3),
        "one_percent_low_fps": round(median([run["one_percent_low_fps"] for run in group]), 2),
        "gpu_p95_spread_pct": spread([run["gpu_ms"]["p95"] for run in group]),
        "one_percent_low_spread_pct": spread([run["one_percent_low_fps"] for run in group]),
    }
    if include_allocation:
        result["renderer_allocation_bytes_median"] = int(median([run["renderer_allocation_bytes"] for run in group]))
    return result


def median(values: list[float]) -> float:
    return statistics.median(values)


def spread(values: list[float]) -> float:
    return round((max(values) - min(values)) / statistics.median(values) * 100.0, 1)


def pct(value: float, baseline: float) -> float:
    return round((value - baseline) / baseline * 100.0, 1)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

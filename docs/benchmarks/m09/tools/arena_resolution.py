"""Shared core for single-resolution arena measurement reports."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from common import load_json
from preset_report import load_capture, load_manifest, pct, summarize, transform_run

REPO_ROOT = Path(__file__).resolve().parents[4]
MODEL_REPORT = REPO_ROOT / "docs/benchmarks/m03/budget-validation.v1.json"
SCENE_ID = "arena_combat"
SCENE = "M01 Arena A/B/A"
LAYOUT = "M01 arena_combat + deterministic fillers"
PRESETS = ("ab-low", "ab-high")
RUNS = 6
HARDWARE = {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"}
GODOT_VERSION = "4.7.2-stable (official ed1daf0bf)"


def _validate_cells(manifest: dict[str, Any], proxy_count: int, width: int, height: int) -> None:
    for preset in PRESETS:
        group = [run for run in manifest["runs"]
                 if run.get("preset_id") == preset
                 and run.get("proxy_count") == proxy_count
                 and run.get("viewport_px") == [width, height]]
        if len(group) != 3 or sorted(run.get("repetition") for run in group) != [1, 2, 3]:
            raise ValueError(f"runs manifest cell is invalid: {proxy_count}/{width}x{height}/{preset}")


def _model_predictions() -> dict[str, float]:
    report = load_json(MODEL_REPORT)
    values = {cell["preset_id"]: float(cell["predicted_gpu_ms"])
              for cell in report.get("cells", []) if cell.get("scene_id") == SCENE_ID}
    if set(values) != set(PRESETS):
        raise ValueError("M03 budget validation is missing arena predictions")
    return values


def _model_cells(cells: dict[str, dict[str, Any]], predictions: dict[str, float]) -> list[dict[str, Any]]:
    result = []
    for preset in PRESETS:
        measured = float(cells[preset]["gpu_p95_ms"])
        predicted = predictions[preset]
        error_pct = (predicted - measured) / measured * 100.0
        result.append({
            "preset_id": preset,
            "predicted_gpu_ms": round(predicted, 3),
            "measured_gpu_p95_ms": measured,
            "error_pct": round(error_pct, 1),
            "within_2pct": abs(error_pct) <= 2.0,
        })
    return result


def build_core(evidence_rel: Path, width: int, height: int, proxy_count: int) -> dict[str, Any]:
    evidence = REPO_ROOT / evidence_rel
    manifest = load_manifest(evidence / "runs.v1.json", RUNS, (proxy_count,), PRESETS)
    _validate_cells(manifest, proxy_count, width, height)
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    for entry in manifest["runs"]:
        capture = load_capture(evidence, entry["run_id"], SCENE, LAYOUT, proxy_count)
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        if capture["viewport"] != [width, height]:
            raise ValueError(f"{entry['run_id']}: viewport mismatch")
        runs.append(transform_run(entry, capture))
    cells = []
    for preset in PRESETS:
        group = [run for run in runs if run["preset_id"] == preset]
        cells.append({"proxy_count": proxy_count, "width": width, "height": height,
                      "preset_id": preset, **summarize(group)})
    by_preset = {cell["preset_id"]: cell for cell in cells}
    low, high = by_preset["ab-low"], by_preset["ab-high"]
    predictions = _model_predictions()
    return {
        "source_sha": source_sha,
        "evidence_bundle": evidence_rel.as_posix(),
        "session_date": "2026-11-14",
        "hardware": dict(HARDWARE),
        "godot_version": GODOT_VERSION,
        "workload": {"scene_id": SCENE_ID, "scene": SCENE, "layout": LAYOUT,
                     "proxy_count": proxy_count, "effect_mode": "lights"},
        "settings": {"vsync_mode": 0, "max_fps": 240, "native_resolution": True},
        "runs": RUNS,
        "cells": cells,
        "deltas_high_vs_low": {
            "gpu_p95_pct": pct(high["gpu_p95_ms"], low["gpu_p95_ms"]),
            "gpu_p99_pct": pct(high["gpu_p99_ms"], low["gpu_p99_ms"]),
            "cpu_p95_pct": pct(high["cpu_p95_ms"], low["cpu_p95_ms"]),
            "pacing_p95_pct": pct(high["pacing_p95_ms"], low["pacing_p95_ms"]),
            "one_percent_low_pct": pct(high["one_percent_low_fps"], low["one_percent_low_fps"]),
        },
        "model_context": {
            "source": "docs/benchmarks/m03/budget-validation.v1.json",
            "cells": _model_cells(by_preset, predictions),
        },
    }


def render_model_and_footer(report: dict[str, Any], footer: str) -> list[str]:
    lines = [
        "",
        "## Contexto do modelo M03",
        "",
        "| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |",
        "|---|---:|---:|---:|---|",
    ]
    for cell in report["model_context"]["cells"]:
        lines.append(
            f"| {cell['preset_id']} | {cell['predicted_gpu_ms']:.3f} | {cell['measured_gpu_p95_ms']:.3f} | "
            f"{cell['error_pct']:+.1f}% | {'sim' if cell['within_2pct'] else 'não'} |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", footer, ""])
    return lines

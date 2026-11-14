#!/usr/bin/env python3
"""NEX M09 preset scaling report builder.

Reads the 18 validated captures (3 per preset per proxy count), verifies the
manifest and writes a deterministic JSON/Markdown report. No new measurement
is performed and no general performance claim is made.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "scaling.v1.json"
REPORT_MD = OUTPUT_DIR / "SCALING-REPORT.md"

REPORT_SCHEMA = "m09_preset_scaling.v1"
RUNS_SCHEMA = "preset_ab_runs.v1"
COUNTS = (25, 100, 200)
PRESETS = ("ab-low", "ab-high")


def load_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != RUNS_SCHEMA:
        raise ValueError("runs manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 18:
        raise ValueError("runs manifest must contain 18 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 19)):
        raise ValueError("runs manifest sequence must be 1..18")
    if len({run.get("run_id") for run in runs}) != 18:
        raise ValueError("runs manifest run ids must be unique")
    for run in runs:
        if run.get("proxy_count") not in COUNTS or run.get("preset_id") not in PRESETS:
            raise ValueError("runs manifest cell is invalid")
    return manifest


def load_capture(run_id: str, count: int) -> dict[str, Any]:
    path = EVIDENCE / f"gpu_profile_{run_id}.json"
    if not path.is_file():
        raise ValueError(f"capture not found: {run_id}")
    document = load_json(path)
    if document.get("run_status") != "COMPLETE":
        raise ValueError(f"{run_id}: run_status is not COMPLETE")
    workload = document.get("workload", {})
    if workload.get("scene") != "Preset A/B/A" or workload.get("proxy_count") != count or workload.get("effect_mode") != "lights":
        raise ValueError(f"{run_id}: workload provenance is invalid")
    settings = document.get("settings", {})
    if settings.get("max_fps") != 240 or settings.get("vsync_mode") != 0:
        raise ValueError(f"{run_id}: settings provenance is invalid")
    series = document.get("series", {})
    metrics = {}
    for key in ("GPU_RENDER_MS", "CPU_RENDER_MS", "FRAME_PACING_INTERVAL_MS"):
        entry = series.get(key, {})
        if entry.get("status") != "MEASURED":
            raise ValueError(f"{run_id}: {key} is not MEASURED")
        aggregates = entry.get("aggregates", {})
        metrics[key] = {name: float(aggregates[name]) for name in ("p50", "p95", "p99")}
    validation_path = EVIDENCE / f"gpu_profile_{run_id}.json.validation.json"
    validation = load_json(validation_path)
    if validation.get("status") != "PASS":
        raise ValueError(f"{run_id}: validation is not PASS")
    return {
        "run_id": run_id,
        "source_sha": document.get("source_sha"),
        "captured_at_utc": document.get("captured_at_utc"),
        "metrics": metrics,
        "one_percent_low_fps": float(document["measurement"]["one_percent_low_fps"]),
        "observed_seconds": float(document["measurement"]["observed_seconds"]),
    }


def _median(values: list[float]) -> float:
    return statistics.median(values)


def _spread(values: list[float]) -> float:
    return round((max(values) - min(values)) / statistics.median(values) * 100.0, 1)


def _pct(value: float, baseline: float) -> float:
    return round((value - baseline) / baseline * 100.0, 1)


def build_report() -> dict[str, Any]:
    manifest = load_manifest()
    source_sha = manifest.get("source_sha")
    runs = []
    for entry in manifest["runs"]:
        capture = load_capture(entry["run_id"], entry["proxy_count"])
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        runs.append(
            {
                "sequence": entry["sequence"],
                "run_id": entry["run_id"],
                "proxy_count": entry["proxy_count"],
                "preset_id": entry["preset_id"],
                "captured_at_utc": capture["captured_at_utc"],
                "observed_seconds": round(capture["observed_seconds"], 3),
                "gpu_ms": {name: round(capture["metrics"]["GPU_RENDER_MS"][name], 3) for name in ("p50", "p95", "p99")},
                "cpu_ms": {name: round(capture["metrics"]["CPU_RENDER_MS"][name], 3) for name in ("p50", "p95", "p99")},
                "pacing_ms": {name: round(capture["metrics"]["FRAME_PACING_INTERVAL_MS"][name], 3) for name in ("p50", "p95", "p99")},
                "one_percent_low_fps": round(capture["one_percent_low_fps"], 2),
            }
        )
    cells = []
    for count in COUNTS:
        for preset in PRESETS:
            group = [run for run in runs if run["proxy_count"] == count and run["preset_id"] == preset]
            if len(group) != 3:
                raise ValueError(f"expected 3 runs for {count}/{preset}")
            cells.append(
                {
                    "proxy_count": count,
                    "preset_id": preset,
                    "runs": len(group),
                    "gpu_p95_median_ms": round(_median([run["gpu_ms"]["p95"] for run in group]), 3),
                    "cpu_p95_median_ms": round(_median([run["cpu_ms"]["p95"] for run in group]), 3),
                    "pacing_p95_median_ms": round(_median([run["pacing_ms"]["p95"] for run in group]), 3),
                    "one_percent_low_median_fps": round(_median([run["one_percent_low_fps"] for run in group]), 2),
                    "gpu_p95_spread_pct": _spread([run["gpu_ms"]["p95"] for run in group]),
                    "one_percent_low_spread_pct": _spread([run["one_percent_low_fps"] for run in group]),
                }
            )
    by_cell = {(cell["proxy_count"], cell["preset_id"]): cell for cell in cells}
    deltas = {}
    for count in COUNTS:
        low = by_cell[(count, "ab-low")]
        high = by_cell[(count, "ab-high")]
        deltas[str(count)] = {
            "gpu_p95_pct": _pct(high["gpu_p95_median_ms"], low["gpu_p95_median_ms"]),
            "cpu_p95_pct": _pct(high["cpu_p95_median_ms"], low["cpu_p95_median_ms"]),
            "pacing_p95_pct": _pct(high["pacing_p95_median_ms"], low["pacing_p95_median_ms"]),
            "one_percent_low_pct": _pct(high["one_percent_low_median_fps"], low["one_percent_low_median_fps"]),
        }
    scaling = {
        preset: {
            "gpu_p95_25_to_200_pct": _pct(
                by_cell[(200, preset)]["gpu_p95_median_ms"], by_cell[(25, preset)]["gpu_p95_median_ms"]
            )
        }
        for preset in PRESETS
    }
    observations = [
        f"GPU p95 high vs low: 25 proxies {deltas['25']['gpu_p95_pct']:+.1f}%, 100 proxies {deltas['100']['gpu_p95_pct']:+.1f}%, 200 proxies {deltas['200']['gpu_p95_pct']:+.1f}%.",
        f"GPU p95 scaling 25→200: ab-low {scaling['ab-low']['gpu_p95_25_to_200_pct']:+.1f}%, ab-high {scaling['ab-high']['gpu_p95_25_to_200_pct']:+.1f}%.",
        f"Pacing remains ~{_median([cell['pacing_p95_median_ms'] for cell in cells]):.3f} ms across all cells (240 fps cap).",
        "One 200/low run has an isolated 1% low outlier (157.39); medians are used.",
        "These are measured GPU costs on a synthetic workload, not game FPS, quality or universal recommendations.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "Vulkan 1.4.351"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1280, 720],
        "settings": {"vsync_mode": 0, "max_fps": 240},
        "runs": runs,
        "cells": cells,
        "deltas_high_vs_low": deltas,
        "scaling_25_to_200": scaling,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session; 3 runs per preset per proxy count",
            "synthetic scene at 1280x720; no cross-scene generalization",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "one isolated 1% low outlier in the 200/low cell; medians reported",
            "renderer allocation bytes are session history, not device VRAM",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Preset scaling 25/100/200 — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · vsync {report['settings']['vsync_mode']} · max_fps {report['settings']['max_fps']}",
        "",
        "## Células (medianas de 3 runs)",
        "",
        "| Count | Preset | GPU p95 | CPU p95 | Pacing p95 | 1% low | GPU spread |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['proxy_count']} | {cell['preset_id']} | {cell['gpu_p95_median_ms']:.3f} | "
            f"{cell['cpu_p95_median_ms']:.3f} | {cell['pacing_p95_median_ms']:.3f} | "
            f"{cell['one_percent_low_median_fps']:.2f} | {cell['gpu_p95_spread_pct']:.1f}% |"
        )
    lines.extend(["", "## Deltas high vs low", ""])
    for count in ("25", "100", "200"):
        delta = report["deltas_high_vs_low"][count]
        lines.append(
            f"- {count} proxies: GPU p95 **{delta['gpu_p95_pct']:+.1f}%**, CPU p95 {delta['cpu_p95_pct']:+.1f}%, "
            f"pacing {delta['pacing_p95_pct']:+.1f}%, 1% low {delta['one_percent_low_pct']:+.1f}%."
        )
    lines.extend(
        [
            "",
            "## Escala 25→200",
            "",
            f"- ab-low GPU p95: {report['scaling_25_to_200']['ab-low']['gpu_p95_25_to_200_pct']:+.1f}%.",
            f"- ab-high GPU p95: {report['scaling_25_to_200']['ab-high']['gpu_p95_25_to_200_pct']:+.1f}%.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_scaling.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "SCALING")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

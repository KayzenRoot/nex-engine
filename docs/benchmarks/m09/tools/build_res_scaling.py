#!/usr/bin/env python3
"""NEX M09 preset resolution-scaling report builder.

Reads the 18 validated captures (3 per preset per resolution), verifies the
manifest and viewport provenance, and writes a deterministic JSON/Markdown
report. No new measurement is performed and no general performance claim is
made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import load_capture, load_manifest, median, pct, spread  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "res-scaling.v1.json"
REPORT_MD = OUTPUT_DIR / "RES-SCALING-REPORT.md"

REPORT_SCHEMA = "m09_preset_res_scaling.v1"
SCENE_ID = "arena_combat"
SCENE = "M01 Arena A/B/A"
LAYOUT = "M01 arena_combat + deterministic fillers"
RESOLUTIONS = ((960, 540), (1280, 720), (1920, 1080))
PRESETS = ("ab-low", "ab-high")
PROXY_COUNT = 100


def _cell_key(width: int, height: int) -> str:
    return f"{width}x{height}"


def _validate_manifest(manifest: dict[str, Any]) -> None:
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 18:
        raise ValueError("runs manifest must contain 18 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 19)):
        raise ValueError("runs manifest sequence must be 1..18")
    if len({run.get("run_id") for run in runs}) != 18:
        raise ValueError("runs manifest run ids must be unique")
    for width, height in RESOLUTIONS:
        for preset in PRESETS:
            group = [run for run in runs
                     if run.get("viewport_px") == [width, height] and run.get("preset_id") == preset]
            if len(group) != 3 or sorted(run.get("repetition") for run in group) != [1, 2, 3]:
                raise ValueError(f"runs manifest cell is invalid: {width}x{height}/{preset}")


def _cell(group: list[dict[str, Any]], width: int, height: int, preset: str) -> dict[str, Any]:
    return {
        "width": width,
        "height": height,
        "preset_id": preset,
        "runs": len(group),
        "gpu_p50_median_ms": round(median([run["gpu_ms"]["p50"] for run in group]), 3),
        "gpu_p95_median_ms": round(median([run["gpu_ms"]["p95"] for run in group]), 3),
        "gpu_p99_median_ms": round(median([run["gpu_ms"]["p99"] for run in group]), 3),
        "cpu_p95_median_ms": round(median([run["cpu_ms"]["p95"] for run in group]), 3),
        "pacing_p95_median_ms": round(median([run["pacing_ms"]["p95"] for run in group]), 3),
        "one_percent_low_median_fps": round(median([run["one_percent_low_fps"] for run in group]), 2),
        "gpu_p95_spread_pct": spread([run["gpu_ms"]["p95"] for run in group]),
        "one_percent_low_spread_pct": spread([run["one_percent_low_fps"] for run in group]),
    }


def build_report() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_runs.v1":
        raise ValueError("runs manifest schema is invalid")
    _validate_manifest(manifest)
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    for entry in manifest["runs"]:
        capture = load_capture(EVIDENCE, entry["run_id"], SCENE, LAYOUT, PROXY_COUNT)
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        if capture["viewport"] != entry["viewport_px"]:
            raise ValueError(f"{entry['run_id']}: viewport mismatch")
        runs.append(
            {
                "sequence": entry["sequence"],
                "run_id": entry["run_id"],
                "viewport_px": entry["viewport_px"],
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
    for width, height in RESOLUTIONS:
        for preset in PRESETS:
            group = [run for run in runs if run["viewport_px"] == [width, height] and run["preset_id"] == preset]
            if len(group) != 3:
                raise ValueError(f"expected 3 runs for {width}x{height}/{preset}")
            cells.append(_cell(group, width, height, preset))
    by_cell = {(cell["width"], cell["height"], cell["preset_id"]): cell for cell in cells}
    deltas = {}
    for width, height in RESOLUTIONS:
        low = by_cell[(width, height, "ab-low")]
        high = by_cell[(width, height, "ab-high")]
        deltas[_cell_key(width, height)] = {
            "gpu_p95_pct": pct(high["gpu_p95_median_ms"], low["gpu_p95_median_ms"]),
            "gpu_p99_pct": pct(high["gpu_p99_median_ms"], low["gpu_p99_median_ms"]),
            "cpu_p95_pct": pct(high["cpu_p95_median_ms"], low["cpu_p95_median_ms"]),
            "pacing_p95_pct": pct(high["pacing_p95_median_ms"], low["pacing_p95_median_ms"]),
            "one_percent_low_pct": pct(high["one_percent_low_median_fps"], low["one_percent_low_median_fps"]),
        }
    scaling = {
        preset: {
            "gpu_p95_960_to_1920_pct": pct(
                by_cell[(1920, 1080, preset)]["gpu_p95_median_ms"],
                by_cell[(960, 540, preset)]["gpu_p95_median_ms"],
            )
        }
        for preset in PRESETS
    }
    observations = [
        "ab-high GPU p95 cost grows with resolution: "
        f"{deltas['960x540']['gpu_p95_pct']:+.1f}% at 960x540, "
        f"{deltas['1280x720']['gpu_p95_pct']:+.1f}% at 1280x720 and "
        f"{deltas['1920x1080']['gpu_p95_pct']:+.1f}% at 1920x1080 versus ab-low.",
        f"From 960x540 to 1920x1080, GPU p95 rises {scaling['ab-low']['gpu_p95_960_to_1920_pct']:+.1f}% for ab-low and "
        f"{scaling['ab-high']['gpu_p95_960_to_1920_pct']:+.1f}% for ab-high.",
        "Absolute GPU p95 medians stay below 0.9 ms and pacing stays near the 240 fps cap in every cell.",
        "The 960x540 ab-low p99 has one run at 0.222 ms vs 0.098/0.225 ms; the median is reported and A/A p95 spread is 0.0%.",
        "These are measured costs for one M01 composition, not game FPS, quality or universal recommendations.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "workload": {"scene_id": SCENE_ID, "scene": SCENE, "proxy_count": PROXY_COUNT, "effect_mode": "lights"},
        "settings": {"vsync_mode": 0, "max_fps": 240, "native_resolution": True},
        "runs": runs,
        "cells": cells,
        "deltas_high_vs_low": deltas,
        "scaling_960_to_1920": scaling,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session on one RTX 5050; no cross-device or cross-session generalization",
            "one scene and one 100-mesh composition; fillers may overlap base-scene props",
            "1920x1080 is the largest 16:9 mode tested; 2560x1440 is not covered",
            "native resolution disables the project's canvas_items stretch mode",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Preset resolution scaling — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Workload:** {report['workload']['scene']} · {report['workload']['proxy_count']} meshes · native resolution",
        "",
        "## Células (medianas de 3 runs)",
        "",
        "| Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | GPU spread |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['width']}×{cell['height']} | {cell['preset_id']} | {cell['gpu_p50_median_ms']:.3f} | "
            f"{cell['gpu_p95_median_ms']:.3f} | {cell['gpu_p99_median_ms']:.3f} | "
            f"{cell['cpu_p95_median_ms']:.3f} | {cell['pacing_p95_median_ms']:.3f} | "
            f"{cell['one_percent_low_median_fps']:.2f} | {cell['gpu_p95_spread_pct']:.1f}% |"
        )
    lines.extend(["", "## Deltas ab-high vs ab-low (GPU p95)", ""])
    for key in ("960x540", "1280x720", "1920x1080"):
        delta = report["deltas_high_vs_low"][key]
        lines.append(
            f"- {key}: **{delta['gpu_p95_pct']:+.1f}%** (GPU p99 {delta['gpu_p99_pct']:+.1f}%, "
            f"CPU p95 {delta['cpu_p95_pct']:+.1f}%, 1% low {delta['one_percent_low_pct']:+.1f}%)."
        )
    lines.extend(
        [
            "",
            "## Escala 960×540 → 1920×1080",
            "",
            f"- ab-low GPU p95: {report['scaling_960_to_1920']['ab-low']['gpu_p95_960_to_1920_pct']:+.1f}%.",
            f"- ab-high GPU p95: {report['scaling_960_to_1920']['ab-high']['gpu_p95_960_to_1920_pct']:+.1f}%.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_res_scaling.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "RES_SCALING")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

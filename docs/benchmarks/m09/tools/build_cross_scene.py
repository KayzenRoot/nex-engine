#!/usr/bin/env python3
"""NEX M09 cross-scene interaction report builder.

Reads the 48 validated captures (2 scenes x 2 proxies x 2 resolutions x 2
presets x 3 runs), verifies provenance and writes a deterministic JSON/
Markdown report. No new measurement is performed and no general performance
claim is made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import load_capture, load_manifest, pct, summarize, transform_run  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-cross-scene")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "cross-scene.v1.json"
REPORT_MD = OUTPUT_DIR / "CROSS-SCENE-REPORT.md"

REPORT_SCHEMA = "m09_preset_cross_scene.v1"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A", "M01 corridor_static + deterministic fillers"),
    ("dense_city", "M01 City A/B/A", "M01 dense_city + deterministic fillers"),
)
PROXY_COUNTS = (50, 100)
RESOLUTIONS = ((960, 540), (1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _key(count: int, width: int, height: int) -> str:
    return f"{count}/{width}x{height}"


def _validate_manifest(manifest: dict[str, Any]) -> None:
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 48:
        raise ValueError("runs manifest must contain 48 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 49)):
        raise ValueError("runs manifest sequence must be 1..48")
    if len({run.get("run_id") for run in runs}) != 48:
        raise ValueError("runs manifest run ids must be unique")
    for scene_id, _, _ in SCENES:
        for count in PROXY_COUNTS:
            for width, height in RESOLUTIONS:
                for preset in PRESETS:
                    group = [run for run in runs
                             if run.get("scene_id") == scene_id
                             and run.get("proxy_count") == count
                             and run.get("viewport_px") == [width, height]
                             and run.get("preset_id") == preset]
                    if len(group) != 3 or sorted(run.get("repetition") for run in group) != [1, 2, 3]:
                        raise ValueError(f"runs manifest cell is invalid: {scene_id}/{_key(count, width, height)}/{preset}")


def _scene_report(scene_id: str, scene: str, layout: str, runs: list[dict[str, Any]]) -> dict[str, Any]:
    cells = []
    for count in PROXY_COUNTS:
        for width, height in RESOLUTIONS:
            for preset in PRESETS:
                group = [run for run in runs
                         if run["scene_id"] == scene_id
                         and run["proxy_count"] == count
                         and run["viewport_px"] == [width, height]
                         and run["preset_id"] == preset]
                if len(group) != 3:
                    raise ValueError(f"expected 3 runs for {scene_id}/{_key(count, width, height)}/{preset}")
                cells.append({"proxy_count": count, "width": width, "height": height,
                              "preset_id": preset, **summarize(group)})
    by_cell = {(cell["proxy_count"], cell["width"], cell["height"], cell["preset_id"]): cell for cell in cells}
    deltas = {}
    for count in PROXY_COUNTS:
        for width, height in RESOLUTIONS:
            low = by_cell[(count, width, height, "ab-low")]
            high = by_cell[(count, width, height, "ab-high")]
            deltas[_key(count, width, height)] = {
                "gpu_p95_pct": pct(high["gpu_p95_ms"], low["gpu_p95_ms"]),
                "gpu_p99_pct": pct(high["gpu_p99_ms"], low["gpu_p99_ms"]),
                "cpu_p95_pct": pct(high["cpu_p95_ms"], low["cpu_p95_ms"]),
                "pacing_p95_pct": pct(high["pacing_p95_ms"], low["pacing_p95_ms"]),
                "one_percent_low_pct": pct(high["one_percent_low_fps"], low["one_percent_low_fps"]),
            }
    resolution_scaling = {
        str(count): {
            preset: pct(
                by_cell[(count, 1920, 1080, preset)]["gpu_p95_ms"],
                by_cell[(count, 960, 540, preset)]["gpu_p95_ms"],
            )
            for preset in PRESETS
        }
        for count in PROXY_COUNTS
    }
    proxy_scaling = {
        f"{width}x{height}": {
            preset: pct(
                by_cell[(100, width, height, preset)]["gpu_p95_ms"],
                by_cell[(50, width, height, preset)]["gpu_p95_ms"],
            )
            for preset in PRESETS
        }
        for width, height in RESOLUTIONS
    }
    return {
        "scene_id": scene_id,
        "scene": scene,
        "layout": layout,
        "cells": cells,
        "deltas_high_vs_low": deltas,
        "resolution_scaling": resolution_scaling,
        "proxy_scaling": proxy_scaling,
    }


def build_report() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_runs.v1":
        raise ValueError("runs manifest schema is invalid")
    _validate_manifest(manifest)
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    layouts = {scene_id: layout for scene_id, _, layout in SCENES}
    for entry in manifest["runs"]:
        layout = layouts.get(entry["scene_id"])
        if layout is None:
            raise ValueError("runs manifest scene id is invalid")
        capture = load_capture(EVIDENCE, entry["run_id"], entry["scene"], layout, entry["proxy_count"])
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        if capture["viewport"] != entry["viewport_px"]:
            raise ValueError(f"{entry['run_id']}: viewport mismatch")
        run = transform_run(entry, capture)
        run["scene_id"] = entry["scene_id"]
        run["scene"] = entry["scene"]
        run["proxy_count"] = entry["proxy_count"]
        run["viewport_px"] = entry["viewport_px"]
        runs.append(run)
    scenes = [_scene_report(scene_id, scene, layout, runs) for scene_id, scene, layout in SCENES]
    by_scene = {scene["scene_id"]: scene for scene in scenes}
    observations = [
        "The arena pattern repeats in both scenes: resolution dominates GPU cost and the high preset's relative cost grows with resolution.",
        f"Corridor GPU p95 high vs low: {by_scene['corridor_static']['deltas_high_vs_low']['50/960x540']['gpu_p95_pct']:+.1f}% at 50/960x540 "
        f"and {by_scene['corridor_static']['deltas_high_vs_low']['50/1920x1080']['gpu_p95_pct']:+.1f}% at 50/1920x1080.",
        f"City GPU p95 high vs low: {by_scene['dense_city']['deltas_high_vs_low']['50/960x540']['gpu_p95_pct']:+.1f}% at 50/960x540 "
        f"and {by_scene['dense_city']['deltas_high_vs_low']['50/1920x1080']['gpu_p95_pct']:+.1f}% at 50/1920x1080.",
        "Proxy scaling 50 to 100 changes GPU p95 by 0.0-2.9%; resolution scaling 960 to 1920 changes it by 79.4-97.2% (ab-low) and 180.0-191.5% (ab-high).",
        "Pacing remains near 4.25 ms and 1% low deltas are within -0.4% to +1.5%; no gain is claimed.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "workload": {"effect_mode": "lights", "proxy_counts": list(PROXY_COUNTS),
                     "resolutions": [{"width": width, "height": height} for width, height in RESOLUTIONS],
                     "scenes": [{"scene_id": scene_id, "scene": scene, "layout": layout}
                                for scene_id, scene, layout in SCENES]},
        "settings": {"vsync_mode": 0, "max_fps": 240, "native_resolution": True},
        "runs": runs,
        "scenes": scenes,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session on one RTX 5050; no cross-device or cross-session generalization",
            "two scenes only; arena_combat is covered by a separate report",
            "two proxy counts and two resolutions; 200 proxies and 2560x1440 are not covered",
            "native resolution disables the project's canvas_items stretch mode",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def _render_scene(lines: list[str], scene: dict[str, Any]) -> None:
    lines.extend([f"## {scene['scene']}", "", "| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |",
                  "|---:|---|---|---:|---:|---:|---:|---:|---:|"])
    for cell in scene["cells"]:
        lines.append(
            f"| {cell['proxy_count']} | {cell['width']}×{cell['height']} | {cell['preset_id']} | "
            f"{cell['gpu_p50_ms']:.3f} | {cell['gpu_p95_ms']:.3f} | {cell['gpu_p99_ms']:.3f} | "
            f"{cell['cpu_p95_ms']:.3f} | {cell['pacing_p95_ms']:.3f} | {cell['one_percent_low_fps']:.2f} |"
        )
    lines.extend(["", "Deltas high vs low (GPU p95):", ""])
    for count in (50, 100):
        for width, height in ((960, 540), (1920, 1080)):
            delta = scene["deltas_high_vs_low"][f"{count}/{width}x{height}"]
            lines.append(f"- {count} proxies / {width}×{height}: **{delta['gpu_p95_pct']:+.1f}%**.")
    lines.extend(["", "Escala 960×540 → 1920×1080 (GPU p95):", ""])
    for count in (50, 100):
        lines.append(f"- {count} proxies: ab-low {scene['resolution_scaling'][str(count)]['ab-low']:+.1f}%, "
                     f"ab-high {scene['resolution_scaling'][str(count)]['ab-high']:+.1f}%.")
    lines.append("")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Cross-scene interaction — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Workload:** {len(report['scenes'])} cenas · proxies {report['workload']['proxy_counts']} · native resolution",
        "",
    ]
    for scene in report["scenes"]:
        _render_scene(lines, scene)
    lines.extend(["## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_cross_scene.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "CROSS_SCENE")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

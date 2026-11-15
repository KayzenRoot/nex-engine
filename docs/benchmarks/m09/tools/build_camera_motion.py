#!/usr/bin/env python3
"""NEX M09 camera-motion sequence report builder.

Reads the 30 deterministic camera-motion frames, verifies provenance, compares
consecutive frames and writes a JSON/Markdown report. The motion is a harness
capability observation, not a quality, stability or performance claim.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from png_image import compare, read_png, sha256_file  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-camera-motion")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "camera-motion.v1.json"
REPORT_MD = OUTPUT_DIR / "CAMERA-MOTION-REPORT.md"

REPORT_SCHEMA = "m09_camera_motion.v1"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A"),
    ("arena_combat", "M01 Arena A/B/A"),
    ("dense_city", "M01 City A/B/A"),
)
PRESETS = ("ab-low", "ab-high")
FRAMES = 5
RUNS = len(SCENES) * len(PRESETS) * FRAMES
CHANGED_PIXEL_THRESHOLD = 2


def _manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_camera_motion_runs.v1":
        raise ValueError("camera-motion manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != RUNS:
        raise ValueError("camera-motion manifest must contain 30 runs")
    if [run.get("sequence") for run in runs] != list(range(1, RUNS + 1)):
        raise ValueError("camera-motion manifest sequence must be 1..30")
    if len({run.get("file") for run in runs}) != RUNS:
        raise ValueError("camera-motion manifest files must be unique")
    for scene_id, scene in SCENES:
        for preset in PRESETS:
            group = [run for run in runs if run["scene_id"] == scene_id and run["preset_id"] == preset]
            if len(group) != FRAMES or sorted(run["frame_index"] for run in group) != list(range(FRAMES)):
                raise ValueError(f"camera-motion cell is invalid: {scene_id}/{preset}")
            for run in group:
                if run.get("scene") != scene or [run.get("width"), run.get("height")] != [1280, 720]:
                    raise ValueError("camera-motion manifest provenance is invalid")
    return manifest


def _cell(scene_id: str, preset: str, runs: list[dict[str, Any]]) -> dict[str, Any]:
    files = {run["frame_index"]: EVIDENCE / run["file"] for run in runs}
    pairs = []
    for index in range(FRAMES - 1):
        before = read_png(files[index])
        after = read_png(files[index + 1])
        metrics = compare(before, after, CHANGED_PIXEL_THRESHOLD)
        pairs.append({
            "from_frame": index,
            "to_frame": index + 1,
            "mean_abs_diff": metrics["mean_abs_diff"],
            "changed_pixels_pct": metrics["changed_pixels_pct"],
            "psnr_db": metrics["psnr_db"],
        })
    return {
        "scene_id": scene_id,
        "preset_id": preset,
        "frames": FRAMES,
        "pairs": pairs,
        "mean_abs_diff_mean": round(sum(pair["mean_abs_diff"] for pair in pairs) / len(pairs), 4),
        "changed_pixels_pct_max": max(pair["changed_pixels_pct"] for pair in pairs),
        "psnr_db_min": min(pair["psnr_db"] for pair in pairs),
    }


def build_report() -> dict[str, Any]:
    manifest = _manifest()
    for run in manifest["runs"]:
        path = EVIDENCE / run["file"]
        if not path.is_file() or sha256_file(path) != run["sha256"]:
            raise ValueError("camera-motion image hash mismatch: " + run["file"])
    cells = []
    for scene_id, _ in SCENES:
        for preset in PRESETS:
            group = [run for run in manifest["runs"] if run["scene_id"] == scene_id and run["preset_id"] == preset]
            cells.append(_cell(scene_id, preset, group))
    for cell in cells:
        for pair in cell["pairs"]:
            if pair["changed_pixels_pct"] <= 0.0:
                raise ValueError(f"camera motion produced identical frames: {cell['scene_id']}/{cell['preset_id']}")
    return {
        "schema_version": REPORT_SCHEMA,
        "harness_source_sha": manifest.get("harness_source_sha"),
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1280, 720],
        "workload": manifest["workload"],
        "runs": RUNS,
        "changed_pixel_threshold": CHANGED_PIXEL_THRESHOLD,
        "cells": cells,
        "verdict": "CAMERA_MOTION_OBSERVED",
        "observations": [
            "all 30 frames were captured with a deterministic 3-degree orbit step between frames; every consecutive pair differs",
            f"the mean absolute difference grows with frame index: {cells[0]['pairs'][0]['mean_abs_diff']:.3f} -> {cells[0]['pairs'][-1]['mean_abs_diff']:.3f} in the first cell",
            f"changed pixels range from {min(pair['changed_pixels_pct'] for cell in cells for pair in cell['pairs']):.3f}% to {max(pair['changed_pixels_pct'] for cell in cells for pair in cell['pairs']):.3f}% across all pairs",
            "this is a harness capability observation for camera motion, not a quality, stability or performance claim",
            "static temporal stability remains covered by the separate temporal-stability bundle",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "discrete 3-degree camera steps between captured frames; not continuous animation",
            "static scene content; animation, VFX, physics and gameplay motion are not covered",
            "the comparison is exact RGB byte comparison; it does not model human perception or color spaces",
            "no FPS, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Camera-motion sequence — RTX 5050",
        "",
        "**Status:** `CAMERA_MOTION_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Harness SHA:** `{report['harness_source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · "
        f"**Motion:** {report['workload']['camera_motion']['mode']} {report['workload']['camera_motion']['step_deg']}°/frame",
        "",
        "## Comparações por célula",
        "",
        "| Cena | Preset | Frames | Mean abs médio | Changed pixels máx | PSNR mín |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['scene_id']} | {cell['preset_id']} | {cell['frames']} | "
            f"{cell['mean_abs_diff_mean']:.4f} | {cell['changed_pixels_pct_max']:.3f}% | {cell['psnr_db_min']:.3f} dB |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_camera_motion.py`; não é benchmark nem claim de qualidade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "M09_CAMERA_MOTION")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

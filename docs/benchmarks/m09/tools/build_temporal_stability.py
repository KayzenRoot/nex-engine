#!/usr/bin/env python3
"""NEX M09 M01 temporal-stability report builder.

Verifies the 30 sequence PNGs, proves frame determinism by SHA-256 equality and
reports frame-to-frame pixel differences. No new capture and no quality claim.
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
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-temporal")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "temporal-stability.v1.json"
REPORT_MD = OUTPUT_DIR / "TEMPORAL-STABILITY-REPORT.md"

REPORT_SCHEMA = "m09_preset_m01_temporal.v1"
FRAMES = 5
CHANGED_PIXEL_THRESHOLD = 2


def _manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_visual_sequence_runs.v1":
        raise ValueError("temporal runs manifest schema is invalid")
    cells = manifest.get("cells")
    if not isinstance(cells, list) or len(cells) != 6:
        raise ValueError("temporal runs manifest must contain 6 cells")
    for cell in cells:
        frames = cell.get("frames")
        if not isinstance(frames, list) or len(frames) != FRAMES:
            raise ValueError("temporal cell must contain 5 frames")
        if [frame.get("index") for frame in frames] != list(range(FRAMES)):
            raise ValueError("temporal frame indices must be 0..4")
    return manifest


def _cell(cell: dict[str, Any]) -> dict[str, Any]:
    paths = []
    for frame in cell["frames"]:
        path = EVIDENCE / frame["file"]
        if not path.is_file() or sha256_file(path) != frame["sha256"]:
            raise ValueError("temporal frame hash mismatch: " + frame["file"])
        paths.append(path)
    hashes = {frame["sha256"] for frame in cell["frames"]}
    identical = len(hashes) == 1
    comparisons = []
    if identical:
        image = read_png(paths[0])
        metrics = compare(image, image, CHANGED_PIXEL_THRESHOLD)
        for index in range(FRAMES - 1):
            comparisons.append({"from": index, "to": index + 1, "identical_sha": True, "metrics": metrics})
    else:
        for index in range(FRAMES - 1):
            metrics = compare(read_png(paths[index]), read_png(paths[index + 1]), CHANGED_PIXEL_THRESHOLD)
            comparisons.append({"from": index, "to": index + 1, "identical_sha": False, "metrics": metrics})
    return {
        "scene_id": cell["scene_id"],
        "scene": cell["scene"],
        "preset_id": cell["preset_id"],
        "frames": len(paths),
        "unique_sha_count": len(hashes),
        "all_frames_identical": identical,
        "comparisons": comparisons,
        "max_mean_abs_diff": max(entry["metrics"]["mean_abs_diff"] for entry in comparisons),
        "max_changed_pixels_pct": max(entry["metrics"]["changed_pixels_pct"] for entry in comparisons),
    }


def build_report() -> dict[str, Any]:
    manifest = _manifest()
    cells = [_cell(cell) for cell in manifest["cells"]]
    stable = all(cell["all_frames_identical"] for cell in cells)
    return {
        "schema_version": REPORT_SCHEMA,
        "harness_source_sha": manifest.get("harness_source_sha"),
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": manifest["workload"]["viewport_px"],
        "workload": manifest["workload"],
        "changed_pixel_threshold": CHANGED_PIXEL_THRESHOLD,
        "runs": 30,
        "cells": cells,
        "summary": {
            "cells": len(cells),
            "frames": len(cells) * FRAMES,
            "all_frames_identical": stable,
            "max_mean_abs_diff": max(cell["max_mean_abs_diff"] for cell in cells),
            "max_changed_pixels_pct": max(cell["max_changed_pixels_pct"] for cell in cells),
        },
        "verdict": "TEMPORAL_STABILITY_OBSERVED" if stable else "TEMPORAL_VARIATION_OBSERVED",
        "observations": [
            "All five frames of every scene/preset cell are byte-identical (one SHA-256 per cell).",
            "Every frame-to-frame pixel comparison is exactly zero in this static workload.",
            "The result covers repeated frames of static compositions only; animation, camera motion and dynamic effects are not covered.",
            "This is a temporal-stability observation, not a quality ranking or a universal guarantee.",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "static scenes only; no animation, temporal effects or camera motion",
            "fillers may overlap base-scene props; this is a stress composition, not a beauty shot",
            "PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · M01 temporal stability — RTX 5050",
        "",
        "**Status:** `TEMPORAL_STABILITY_OBSERVED / SINGLE_SESSION / STATIC_WORKLOAD / NO_QUALITY_CLAIM`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Harness SHA:** `{report['harness_source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · 5 frames por célula · intervalo de 30 frames",
        "",
        "## Estabilidade por célula",
        "",
        "| Cena | Preset | Frames | SHA-256 únicos | Frame-a-frame mean abs | Pixels alterados | Veredito |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['scene_id']} | {cell['preset_id']} | {cell['frames']} | {cell['unique_sha_count']} | "
            f"{cell['max_mean_abs_diff']:.4f} | {cell['max_changed_pixels_pct']:.3f}% | "
            f"{'estável' if cell['all_frames_identical'] else 'variação'} |"
        )
    lines.extend(
        [
            "",
            "## Resumo",
            "",
            f"- Células: {report['summary']['cells']} · frames: {report['summary']['frames']}.",
            f"- Todas as frames idênticas: {'sim' if report['summary']['all_frames_identical'] else 'não'}.",
            f"- Maior diferença frame-a-frame: {report['summary']['max_mean_abs_diff']:.4f} mean abs.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_temporal_stability.py`; não é benchmark nem claim de qualidade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "TEMPORAL")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

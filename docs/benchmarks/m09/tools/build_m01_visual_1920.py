#!/usr/bin/env python3
"""NEX M09 M01 visual-truth 1920x1080 report builder.

Verifies the 18 PNG captures, proves A/A determinism by SHA-256 equality,
compares matched low/high images and reports the change relative to the
integrated 1280x720 visual report. No new capture and no quality claim.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import pct  # noqa: E402 - local tool module
from visual_truth import build_visual_core, render_visual_markdown  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-1920")
CONTEXT = REPO_ROOT / "docs/benchmarks/m09/m01-visual.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "m01-visual-1920.v1.json"
REPORT_MD = OUTPUT_DIR / "M01-VISUAL-1920-REPORT.md"

REPORT_SCHEMA = "m09_preset_m01_visual_1920.v1"
VIEWPORT = [1920, 1080]


def _context() -> dict[str, dict[str, float]]:
    report = load_json(CONTEXT)
    values: dict[str, dict[str, float]] = {}
    for scene in report.get("scenes", []):
        summary = scene.get("summary", {})
        values[scene["scene_id"]] = {
            "mean_abs_diff": float(summary["ab_mean_abs_diff_median"]),
            "changed_pixels_pct": float(summary["ab_changed_pixels_pct_median"]),
            "psnr_db": float(summary["ab_psnr_db_median"]),
        }
    return values


def build_report() -> dict[str, Any]:
    core = build_visual_core(EVIDENCE_REL, VIEWPORT)
    context = _context()
    for scene in core["scenes"]:
        ab = scene["ab"]["metrics"]
        baseline = context[scene["scene_id"]]
        scene["comparison_1280"] = {
            **baseline,
            "delta_mean_abs_pct": pct(ab["mean_abs_diff"], baseline["mean_abs_diff"]),
            "delta_changed_pixels_pct": pct(ab["changed_pixels_pct"], baseline["changed_pixels_pct"]),
        }
    return {
        "schema_version": REPORT_SCHEMA,
        **core,
        "context_report": "docs/benchmarks/m09/m01-visual.v1.json",
        "verdict": "VISUAL_DIFFERENCE_OBSERVED",
        "observations": [
            "A/A is exact: all three repetitions of each scene/preset pair share one SHA-256.",
            "ab-high changes the image in every scene at 1920x1080; changed pixels are 3.367% (corridor), 3.354% (arena) and 1.276% (city).",
            "The A/B mean absolute difference is slightly lower at 1920x1080 than at 1280x720 in all three scenes.",
            "The direction is consistent across resolutions: the high preset changes the image, and city has the smallest difference.",
            "This is a pixel-difference observation, not a quality ranking or a universal recommendation.",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "static frame only; animation, temporal effects and camera motion are not covered",
            "fillers may overlap base-scene props; this is a stress composition, not a beauty shot",
            "PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    return render_visual_markdown(
        report,
        "NEX M09 · M01 visual truth at 1920×1080 — RTX 5050",
        "comparison_1280",
        "1280",
        "Relatório gerado por `docs/benchmarks/m09/tools/build_m01_visual_1920.py`; não é benchmark nem claim de qualidade.",
    )


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "M01_VISUAL_1920")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

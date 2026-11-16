#!/usr/bin/env python3
"""Build the M07 2D reference report from the native lab and planner evidence."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from runtime_report import (diff, load_manifest, markdown_document, markdown_mode_table,  # noqa: E402 - shared tool module
                            markdown_quality_table, markdown_tail, mode_rows, parse_pass_line,
                            pct, render_json, report_metadata, run_lab_report)

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m07"
IMAGES = EVIDENCE / "images"
OUTPUT = REPO / "docs" / "benchmarks" / "m07"
REPORT_JSON = OUTPUT / "m07-runtime.v1.json"
REPORT_MD = OUTPUT / "M07-RUNTIME.md"
PLANNER_LOG = REPO / "nex_modules" / "render2d" / "canvas" / "evidence" / "headless-smoke-2026-11-13.log"
SOURCE_SHA = "aa6256a82f6cd34e347b05ac43375ac4042d2ede"
MODES = ("baseline", "lighting", "shadows", "normal", "particles", "parallax",
         "quality_low", "quality_medium", "quality_high")


def _planner_checks() -> int:
    return parse_pass_line(PLANNER_LOG, "NEX_M07_S01_SMOKE_PASS:")


def build_report() -> dict[str, Any]:
    manifest = load_manifest(EVIDENCE / "runs.v1.json", "m07_lab_runs.v1", SOURCE_SHA, 9, MODES)
    planner_checks = _planner_checks()
    if planner_checks < 46:
        raise ValueError("M07 planner smoke is incomplete")
    images = sorted(IMAGES.glob("*.png"))
    if len(images) != 9:
        raise ValueError("M07 lab must contain 9 images")
    rows = mode_rows(EVIDENCE, manifest, MODES, "m07")
    shadows_vs_lighting = diff(IMAGES / "m07_lighting.png", IMAGES / "m07_shadows.png")
    normal_vs_lighting = diff(IMAGES / "m07_lighting.png", IMAGES / "m07_normal.png")
    decisions = [
        {"id": "CanvasPlanner / render2d.v1", "decision": "GO",
         "evidence": f"{planner_checks} headless checks; planning only, no rendering"},
        {"id": "2D lighting / CanvasModulate", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "4 PointLight2D change 16.218% of the frame at +25.0% GPU p95"},
        {"id": "2D shadows / LightOccluder2D", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "shadows add +33.3% GPU over lighting and 9.028% pixel change"},
        {"id": "Normal maps / CanvasTexture", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "normal maps add +9.3% GPU over lighting and 14.542% pixel change"},
        {"id": "GPUParticles2D", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "384 particles add +18.3% GPU over baseline and 0.979% pixel change"},
        {"id": "ParallaxBackground", "decision": "GO",
         "evidence": "3 layers change 23.006% of the frame at +16.7% GPU p95"},
        {"id": "2D quality profiles", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "low/medium/high GPU 0.065/0.081/0.153 ms in one 100-sprite lab"},
    ]
    return {
        "schema_version": "m07_render2d_runtime.v1",
        **report_metadata(SOURCE_SHA),
        "s01": {"planner_checks": planner_checks, "verdict": "CANVAS_PLANNER_VERIFIED"},
        "s02": {"rows": rows, "verdict": "RENDER2D_LIGHTING_DERIVED"},
        "s03": {"rows": rows, "shadows_vs_lighting": shadows_vs_lighting,
                "verdict": "RENDER2D_SHADOWS_GO_WITH_LIMITATIONS"},
        "s04": {"rows": rows, "normal_vs_lighting": normal_vs_lighting,
                "verdict": "RENDER2D_NORMAL_MAPS_GO_WITH_LIMITATIONS"},
        "s05": {"rows": rows, "verdict": "RENDER2D_PARTICLES_GO_WITH_LIMITATIONS"},
        "s06": {"rows": rows, "verdict": "RENDER2D_PARALLAX_GO"},
        "s07": {"rows": rows, "verdict": "RENDER2D_QUALITY_PROFILES_GO_WITH_LIMITATIONS"},
        "s08": {"decisions": decisions, "runs": 9, "images": len(images),
                "planner_checks": planner_checks, "third_party_assets": 0,
                "verdict": "M07_RENDER2D_QA_VERIFIED"},
        "verdict": "M07_RENDER2D_REFERENCE_DERIVED",
        "observations": [
            "9 native 2D runs and 9 captures cover lighting, shadows, normal maps, particles, parallax and quality profiles",
            "baseline GPU p95 is 0.060 ms; quality_high is 0.153 ms in the 100-sprite lab",
            "lighting changes 16.218% of the frame at +25.0% GPU p95 versus baseline",
            "shadows add +33.3% GPU over lighting and 9.028% pixel change",
            "normal maps add +9.3% GPU over lighting and 14.542% pixel change",
            "384 particles add +18.3% GPU over baseline and 0.979% pixel change",
            "parallax changes 23.006% of the frame at +16.7% GPU p95",
            "CanvasPlanner still passes 46 headless checks",
        ],
        "limitations": [
            "single session, one GPU and driver; 1920x1080 static 2D lab",
            "no production 2D renderer, atlas packing, y-sort or transparency rasterization",
            "no input-to-photon, VRAM pressure or cross-device claim",
            "lighting/shadows/normal maps are native Godot features, not a custom renderer",
            "no production art, no PoE2 parity and no generalized FPS claim",
        ],
        "runs": 9,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = markdown_document(
        "NEX M07 · Render2D runtime",
        "M07_RENDER2D_REFERENCE_DERIVED / NATIVE_2D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT",
        report,
    )
    lines.extend([
        "## S01 · CanvasPlanner",
        "",
        f"- **{report['s01']['verdict']}**: {report['s01']['planner_checks']} checks headless.",
        "",
        "## S02 · 2D lighting",
        "",
    ])
    lines.extend(markdown_mode_table(report["s02"]["rows"], MODES))
    lines.extend([
        "",
        "## S03 · Shadows",
        "",
        f"- Shadows vs lighting: **{report['s03']['shadows_vs_lighting']['changed_pixels_pct']:.3f}%** de pixels, "
        f"PSNR {report['s03']['shadows_vs_lighting']['psnr_db']:.2f} dB.",
        f"- GPU p95: lighting **{report['s02']['rows']['lighting']['gpu_p95_ms']:.3f} ms** → "
        f"shadows **{report['s02']['rows']['shadows']['gpu_p95_ms']:.3f} ms**.",
        "",
        "## S04 · Normal maps",
        "",
        f"- Normal vs lighting: **{report['s04']['normal_vs_lighting']['changed_pixels_pct']:.3f}%** de pixels, "
        f"PSNR {report['s04']['normal_vs_lighting']['psnr_db']:.2f} dB.",
        f"- GPU p95: lighting **{report['s02']['rows']['lighting']['gpu_p95_ms']:.3f} ms** → "
        f"normal **{report['s02']['rows']['normal']['gpu_p95_ms']:.3f} ms**.",
        "",
        "## S05 · Particles",
        "",
        f"- 384 particles: GPU **{report['s02']['rows']['particles']['gpu_p95_ms']:.3f} ms** "
        f"({report['s02']['rows']['particles']['gpu_vs_baseline_pct']:+.2f}% vs baseline); "
        f"pixels **{report['s02']['rows']['particles']['changed_pixels_pct']:.3f}%**.",
        "",
        "## S06 · Parallax",
        "",
        f"- 3 layers: GPU **{report['s02']['rows']['parallax']['gpu_p95_ms']:.3f} ms** "
        f"({report['s02']['rows']['parallax']['gpu_vs_baseline_pct']:+.2f}% vs baseline); "
        f"pixels **{report['s02']['rows']['parallax']['changed_pixels_pct']:.3f}%**.",
        "",
        "## S07 · Quality profiles",
        "",
    ])
    lines.extend(markdown_quality_table(report["s07"]["rows"], ("quality_low", "quality_medium", "quality_high")))
    lines.extend(markdown_tail(report, report["s08"]["decisions"]))
    lines.extend(["", "Gerado por `docs/benchmarks/m07/tools/build_m07_runtime.py`; não é paridade com PoE2.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    return run_lab_report(build_report, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                          argv, "M07_RENDER2D_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

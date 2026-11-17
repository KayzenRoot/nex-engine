#!/usr/bin/env python3
"""Build the M10 animation/feedback reference report from the native lab."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parents[1] / "m09" / "tools"))
sys.path.insert(0, str(TOOLS.parents[1] / "tools"))
from common import run_cli  # noqa: E402 - shared local tool module
from runtime_report import (diff, load_manifest, markdown_document, markdown_mode_table,  # noqa: E402 - shared tool module
                            markdown_quality_table, markdown_tail, mode_rows, parse_pass_line,
                            pct, render_json, report_metadata, run_lab_report)

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-17-m10"
IMAGES = EVIDENCE / "images"
OUTPUT = REPO / "docs" / "benchmarks" / "m10"
REPORT_JSON = OUTPUT / "m10-runtime.v1.json"
REPORT_MD = OUTPUT / "M10-RUNTIME.md"
PLANNER_LOG = REPO / "nex_modules" / "animation" / "combat_feedback" / "evidence" / "headless-smoke-2026-11-13.log"
SOURCE_SHA = "818759d5e6daaa3d3f9be922331b0d39d5cd4f5c"
MODES = ("baseline", "blend", "attack", "hit", "hitstop", "camera", "vfx",
         "quality_low", "quality_high")


def _planner_checks() -> int:
    return parse_pass_line(PLANNER_LOG, "NEX_M10_FEEDBACK_SMOKE_PASS:")


def build_report() -> dict[str, Any]:
    manifest = load_manifest(EVIDENCE / "runs.v1.json", "m10_lab_runs.v1", SOURCE_SHA, 9, MODES)
    planner_checks = _planner_checks()
    if planner_checks < 66:
        raise ValueError("M10 feedback planner smoke is incomplete")
    images = sorted(IMAGES.glob("*.png"))
    if len(images) != 9:
        raise ValueError("M10 lab must contain 9 images")
    rows = mode_rows(EVIDENCE, manifest, MODES, "m10")
    hitstop_diff = diff(IMAGES / "m10_attack.png", IMAGES / "m10_hitstop.png")
    decisions = [
        {"id": "FeedbackPlanner / feedback.v1", "decision": "GO",
         "evidence": f"{planner_checks} headless checks; planning only"},
        {"id": "AnimationTree blending", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "blend 0.5 changes 0.493% of the frame at +3.13% GPU"},
        {"id": "Hit reaction", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "hit changes 0.414% of the frame; GPU neutral in the lab"},
        {"id": "Visual hit-stop", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "hit-stop changes 0.000% of the attack pose; timing/pacing only"},
        {"id": "Smooth camera", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "camera mode adds +6.64% GPU and changes 2.661% of the frame"},
        {"id": "M05 VFX synchronization", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "impact changes 3.681% of the frame; SpellFX event accepted"},
        {"id": "Animation quality profiles", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "low/high GPU 0.264/0.274 ms in one animation lab"},
    ]
    return {
        "schema_version": "m10_animation_runtime.v1",
        **report_metadata(SOURCE_SHA),
        "s01": {"planner_checks": planner_checks, "verdict": "FEEDBACK_PLANNER_VERIFIED"},
        "s02": {"rows": rows, "verdict": "ANIMATION_BLENDING_DERIVED"},
        "s03": {"rows": rows, "verdict": "HIT_REACTION_GO_WITH_LIMITATIONS"},
        "s04": {"rows": rows, "hitstop_vs_attack": hitstop_diff,
                "verdict": "HITSTOP_VISUAL_ONLY"},
        "s05": {"rows": rows, "verdict": "SMOOTH_CAMERA_GO_WITH_LIMITATIONS"},
        "s06": {"rows": rows, "verdict": "VFX_SYNC_GO_WITH_LIMITATIONS"},
        "s07": {"rows": rows, "verdict": "ANIMATION_QUALITY_GO_WITH_LIMITATIONS"},
        "s08": {"decisions": decisions, "runs": 9, "images": len(images),
                "planner_checks": planner_checks, "third_party_assets": 0,
                "verdict": "M10_ANIMATION_QA_VERIFIED"},
        "verdict": "M10_ANIMATION_REFERENCE_DERIVED",
        "observations": [
            "9 native animation runs and 9 captures cover idle, blend, attack, hit, hit-stop, camera, VFX and quality profiles",
            "baseline GPU p95 is 0.256 ms; blend 0.264 ms; attack 0.256 ms; hit 0.256 ms; camera 0.273 ms; vfx 0.262 ms",
            "blend 0.5 changes 0.493% of the frame; attack changes 0.931%; hit changes 0.414%",
            "visual hit-stop changes 0.000% of the attack pose; it is a timing/pacing experiment",
            "camera mode adds +6.64% GPU and changes 2.661% of the frame",
            "M05 impact changes 3.681% of the frame and the SpellFX event is accepted",
            "quality low/high GPU p95 is 0.264/0.274 ms",
            "FeedbackPlanner still passes 66 headless checks",
        ],
        "limitations": [
            "single session, one GPU and driver; 1920x1080 static animation lab",
            "the rig is a two-bone proxy, not a production character or skin",
            "hit-stop is visual only; no damage, physics or netcode authority",
            "no input-to-photon, VRAM pressure or cross-device claim",
            "no production art, no PoE2 parity and no generalized FPS claim",
        ],
        "runs": 9,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = markdown_document(
        "NEX M10 · Animation and combat feedback",
        "M10_ANIMATION_REFERENCE_DERIVED / NATIVE_ANIMATION_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT",
        report,
    )
    lines.extend([
        "## S01 · FeedbackPlanner",
        "",
        f"- **{report['s01']['verdict']}**: {report['s01']['planner_checks']} checks headless.",
        "",
        "## S02 · Animation blending",
        "",
    ])
    lines.extend(markdown_mode_table(report["s02"]["rows"], MODES))
    lines.extend([
        "",
        "## S03 · Hit reaction",
        "",
        f"- Hit vs baseline: **{report['s03']['rows']['hit']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s03']['rows']['hit']['gpu_p95_ms']:.3f} ms**.",
        "",
        "## S04 · Visual hit-stop",
        "",
        f"- Hit-stop vs attack: **{report['s04']['hitstop_vs_attack']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s04']['rows']['hitstop']['gpu_p95_ms']:.3f} ms** vs attack "
        f"**{report['s04']['rows']['attack']['gpu_p95_ms']:.3f} ms**.",
        "- O hit-stop é apenas visual; nenhuma autoridade de dano, física ou rede é alterada.",
        "",
        "## S05 · Smooth camera",
        "",
        f"- Camera vs baseline: **{report['s05']['rows']['camera']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s05']['rows']['camera']['gpu_p95_ms']:.3f} ms** "
        f"({report['s05']['rows']['camera']['gpu_vs_baseline_pct']:+.2f}%).",
        "",
        "## S06 · M05 VFX synchronization",
        "",
        f"- VFX vs baseline: **{report['s06']['rows']['vfx']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s06']['rows']['vfx']['gpu_p95_ms']:.3f} ms** "
        f"({report['s06']['rows']['vfx']['gpu_vs_baseline_pct']:+.2f}%).",
        "",
        "## S07 · Quality profiles",
        "",
    ])
    lines.extend(markdown_quality_table(report["s07"]["rows"], ("quality_low", "quality_high")))
    lines.extend(markdown_tail(report, report["s08"]["decisions"]))
    lines.extend(["", "Gerado por `docs/benchmarks/m10/tools/build_m10_runtime.py`; não é paridade com PoE2.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    return run_lab_report(build_report, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                          argv, "M10_ANIMATION_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

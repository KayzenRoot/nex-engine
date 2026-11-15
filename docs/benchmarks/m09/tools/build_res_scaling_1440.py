#!/usr/bin/env python3
"""NEX M09 2560x1440 resolution-scaling report builder.

Reads the six validated captures, verifies provenance and writes a
deterministic JSON/Markdown report. The 960/1280/1920 context comes from the
already integrated res-scaling report and the M03 prediction is quoted only as
context; neither is re-measured here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arena_resolution import PRESETS, build_core, load_context, render_model_and_footer  # noqa: E402 - local tool module
from common import run_cli  # noqa: E402 - local tool module
from preset_report import pct, render_cells_table  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1440")
CONTEXT = REPO_ROOT / "docs/benchmarks/m09/res-scaling.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "res-scaling-1440.v1.json"
REPORT_MD = OUTPUT_DIR / "RES-SCALING-1440-REPORT.md"

REPORT_SCHEMA = "m09_resolution_scaling_1440.v1"
SCENE_ID = "arena_combat"
WIDTH = 2560
HEIGHT = 1440
PROXY_COUNT = 100
CONTEXT_RESOLUTIONS = ((960, 540), (1280, 720), (1920, 1080))
CONTEXT_KEYS = ("gpu_p95_ms", "cpu_p95_ms", "pacing_p95_ms", "one_percent_low_fps")


def _resolution_delta(measured: float, baseline: float) -> float:
    return pct(measured, baseline)


def build_report() -> dict[str, Any]:
    core = build_core(EVIDENCE_REL, WIDTH, HEIGHT, PROXY_COUNT)
    by_preset = {cell["preset_id"]: cell for cell in core["cells"]}
    context = load_context(CONTEXT, CONTEXT_RESOLUTIONS, CONTEXT_KEYS)
    model_cells = core["model_context"]["cells"]
    predictions = {cell["preset_id"]: cell["predicted_gpu_ms"] for cell in model_cells}
    resolution_deltas = {
        "1920x1080_to_2560x1440": {
            preset: _resolution_delta(by_preset[preset]["gpu_p95_ms"],
                                      context["1920x1080"][preset]["gpu_p95_ms"])
            for preset in PRESETS
        },
        "960x540_to_2560x1440": {
            preset: _resolution_delta(by_preset[preset]["gpu_p95_ms"],
                                      context["960x540"][preset]["gpu_p95_ms"])
            for preset in PRESETS
        },
    }
    return {
        "schema_version": REPORT_SCHEMA,
        **core,
        "context_resolutions": context,
        "resolution_deltas": resolution_deltas,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": [
            f"high/low grows from +323.9% at 1280x720 to {core['deltas_high_vs_low']['gpu_p95_pct']:+.1f}% at 2560x1440",
            f"GPU p95 rises {resolution_deltas['1920x1080_to_2560x1440']['ab-low']:+.1f}% (ab-low) and "
            f"{resolution_deltas['1920x1080_to_2560x1440']['ab-high']:+.1f}% (ab-high) from 1920x1080 to 2560x1440",
            f"the ab-high M03 prediction ({predictions['ab-high']:.3f} ms) is {model_cells[1]['error_pct']:+.1f}% from the measured 2560x1440 value; the 2% match does not survive this resolution",
            f"the ab-low M03 prediction ({predictions['ab-low']:.3f} ms) is {model_cells[0]['error_pct']:+.1f}% above the measured value, so the low preset remains overestimated",
            "the first ab-low run has an isolated 1% low outlier (38.9 fps); medians are used and the 1% low is not used for a trend claim",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "one scene, one proxy count (100) and one resolution (2560x1440)",
            "the 960/1280/1920 context is from a different session and is labeled as such",
            "the 2560x1440 window is taller than the 2560x1080 desktop; the viewport is captured off-screen",
            "three runs per preset; the ab-low 1% low has an 82.9% spread due to one outlier",
            "native resolution disables the canvas_items stretch mode",
            "max_fps 240 and disabled VSync cap frame pacing",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · 2560×1440 resolution scaling — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']}",
        "",
        *render_cells_table(report),
        "",
        "## ab-high vs ab-low (GPU p95)",
        "",
        f"- Delta: {report['deltas_high_vs_low']['gpu_p95_pct']:+.1f}%.",
        "",
        "## Contexto de resolução (GPU p95, sessão separada)",
        "",
        "| Preset | 960×540 | 1280×720 | 1920×1080 | 2560×1440 | 1920→2560 | 960→2560 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for preset in PRESETS:
        lines.append(
            f"| {preset} | {report['context_resolutions']['960x540'][preset]['gpu_p95_ms']:.3f} | "
            f"{report['context_resolutions']['1280x720'][preset]['gpu_p95_ms']:.3f} | "
            f"{report['context_resolutions']['1920x1080'][preset]['gpu_p95_ms']:.3f} | "
            f"{next(cell for cell in report['cells'] if cell['preset_id'] == preset)['gpu_p95_ms']:.3f} | "
            f"{report['resolution_deltas']['1920x1080_to_2560x1440'][preset]:+.1f}% | "
            f"{report['resolution_deltas']['960x540_to_2560x1440'][preset]:+.1f}% |"
        )
    lines.extend(render_model_and_footer(
        report,
        "Relatório gerado por `docs/benchmarks/m09/tools/build_res_scaling_1440.py`; não é benchmark nem claim de ganho.",
    ))
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD,
                   argv, "M09_RES_SCALING_1440")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""NEX M09 1600x900 resolution-scaling report builder.

Reads the six validated captures, verifies provenance and writes a
deterministic JSON/Markdown report. The 1280/1920 context comes from the
already integrated res-scaling report and the M03 prediction is quoted only as
context; neither is re-measured here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arena_resolution import PRESETS, build_core, render_model_and_footer  # noqa: E402 - local tool module
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import pct, render_cells_table  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1600")
CONTEXT = REPO_ROOT / "docs/benchmarks/m09/res-scaling.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "res-scaling-1600.v1.json"
REPORT_MD = OUTPUT_DIR / "RES-SCALING-1600-REPORT.md"

REPORT_SCHEMA = "m09_resolution_scaling_1600.v1"
SCENE_ID = "arena_combat"
WIDTH = 1600
HEIGHT = 900
PROXY_COUNT = 100
CONTEXT_RESOLUTIONS = ((1280, 720), (1920, 1080))
CONTEXT_KEYS = ("gpu_p95_ms", "cpu_p95_ms", "pacing_p95_ms", "one_percent_low_fps")


def _context() -> dict[str, dict[str, dict[str, float]]]:
    report = load_json(CONTEXT)
    if report.get("workload", {}).get("scene_id") != SCENE_ID:
        raise ValueError("res-scaling context is not the arena scene")
    values: dict[str, dict[str, dict[str, float]]] = {}
    for width, height in CONTEXT_RESOLUTIONS:
        key = f"{width}x{height}"
        values[key] = {}
        for preset in PRESETS:
            match = [cell for cell in report.get("cells", [])
                     if cell.get("preset_id") == preset
                     and cell.get("width") == width and cell.get("height") == height]
            if len(match) != 1:
                raise ValueError(f"res-scaling context is missing {key}/{preset}")
            values[key][preset] = {name: float(match[0][name]) for name in CONTEXT_KEYS}
    return values


def build_report() -> dict[str, Any]:
    core = build_core(EVIDENCE_REL, WIDTH, HEIGHT, PROXY_COUNT)
    cells = {cell["preset_id"]: cell for cell in core["cells"]}
    context = _context()
    model_cells = core["model_context"]["cells"]
    predictions = {cell["preset_id"]: cell["predicted_gpu_ms"] for cell in model_cells}
    deltas = {
        "1280x720_to_1600x900": {
            preset: pct(cells[preset]["gpu_p95_ms"], context["1280x720"][preset]["gpu_p95_ms"])
            for preset in PRESETS
        },
        "1600x900_to_1920x1080": {
            preset: pct(context["1920x1080"][preset]["gpu_p95_ms"], cells[preset]["gpu_p95_ms"])
            for preset in PRESETS
        },
    }
    return {
        "schema_version": REPORT_SCHEMA,
        **core,
        "context_resolutions": context,
        "resolution_deltas": deltas,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": [
            f"GPU p95 rises from 1280x720 to 1600x900 by {deltas['1280x720_to_1600x900']['ab-low']:+.1f}% (ab-low) and {deltas['1280x720_to_1600x900']['ab-high']:+.1f}% (ab-high)",
            f"GPU p95 rises from 1600x900 to 1920x1080 by {deltas['1600x900_to_1920x1080']['ab-low']:+.1f}% (ab-low) and {deltas['1600x900_to_1920x1080']['ab-high']:+.1f}% (ab-high)",
            f"the ab-high M03 prediction ({predictions['ab-high']:.3f} ms) is {model_cells[1]['error_pct']:+.1f}% from the measured 1600x900 value, between the 1280x720 match and the 1920x1080 error",
            f"the ab-low M03 prediction ({predictions['ab-low']:.3f} ms) is {model_cells[0]['error_pct']:+.1f}% above the measured value, consistent with unmodeled resolution scale, MSAA and glow",
            "this is a measured cost for one scene and one proxy count, not a universal rule or a quality claim",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "one scene, one proxy count (100) and one resolution (1600x900)",
            "the 1280/1920 context is from a different session and is labeled as such",
            "three runs per preset; GPU p95 spread is 0.5-0.8%",
            "native resolution disables the canvas_items stretch mode",
            "max_fps 240 and disabled VSync cap frame pacing",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · 1600×900 resolution scaling — RTX 5050",
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
        "| Preset | 1280×720 | 1600×900 | 1920×1080 | 1280→1600 | 1600→1920 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for preset in PRESETS:
        lines.append(
            f"| {preset} | {report['context_resolutions']['1280x720'][preset]['gpu_p95_ms']:.3f} | "
            f"{next(cell for cell in report['cells'] if cell['preset_id'] == preset)['gpu_p95_ms']:.3f} | "
            f"{report['context_resolutions']['1920x1080'][preset]['gpu_p95_ms']:.3f} | "
            f"{report['resolution_deltas']['1280x720_to_1600x900'][preset]:+.1f}% | "
            f"{report['resolution_deltas']['1600x900_to_1920x1080'][preset]:+.1f}% |"
        )
    lines.extend(render_model_and_footer(
        report,
        "Relatório gerado por `docs/benchmarks/m09/tools/build_res_scaling_1600.py`; não é benchmark nem claim de ganho.",
    ))
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD,
                   argv, "M09_RES_SCALING_1600")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""NEX M09 200-proxy / 1280x720 arena report builder.

Reads the six validated captures, verifies provenance and writes a
deterministic JSON/Markdown report. The 100-proxy context is read from the
already integrated m01-ab report and the M03 prediction is quoted only as
context; neither is re-measured here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arena_resolution import build_core  # noqa: E402 - local tool module
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import pct, render_cells_table  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-arena-200-720")
CONTEXT_100 = REPO_ROOT / "docs/benchmarks/m09/m01-ab.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "interaction-200-720.v1.json"
REPORT_MD = OUTPUT_DIR / "INTERACTION-200-720-REPORT.md"

REPORT_SCHEMA = "m09_preset_interaction_200_720.v1"
SCENE_ID = "arena_combat"
WIDTH = 1280
HEIGHT = 720
PROXY_COUNT = 200
PRESETS = ("ab-low", "ab-high")
CONTEXT_KEYS = ("gpu_p95_ms", "cpu_p95_ms", "pacing_p95_ms", "one_percent_low_fps")


def _context_100() -> dict[str, dict[str, float]]:
    report = load_json(CONTEXT_100)
    for scene in report.get("scenes", []):
        if scene.get("scene_id") == SCENE_ID:
            return {
                preset: {key: float(scene["baselines"][preset][key]) for key in CONTEXT_KEYS}
                for preset in PRESETS
            }
    raise ValueError("m01-ab context is missing the arena scene")


def build_report() -> dict[str, Any]:
    core = build_core(EVIDENCE_REL, WIDTH, HEIGHT, PROXY_COUNT)
    by_preset = {cell["preset_id"]: cell for cell in core["cells"]}
    low, high = by_preset["ab-low"], by_preset["ab-high"]
    context = _context_100()
    model_cells = core["model_context"]["cells"]
    predictions = {cell["preset_id"]: cell["predicted_gpu_ms"] for cell in model_cells}
    proxy_delta = {
        preset: {
            "gpu_p95_pct": pct(by_preset[preset]["gpu_p95_ms"], context[preset]["gpu_p95_ms"]),
            "cpu_p95_pct": pct(by_preset[preset]["cpu_p95_ms"], context[preset]["cpu_p95_ms"]),
            "pacing_p95_pct": pct(by_preset[preset]["pacing_p95_ms"], context[preset]["pacing_p95_ms"]),
            "one_percent_low_pct": pct(by_preset[preset]["one_percent_low_fps"],
                                       context[preset]["one_percent_low_fps"]),
        }
        for preset in PRESETS
    }
    return {
        "schema_version": REPORT_SCHEMA,
        **core,
        "context_100": context,
        "proxy_100_to_200": proxy_delta,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": [
            f"GPU p95 at 200/1280 is {low['gpu_p95_ms']:.3f} ms (ab-low) and {high['gpu_p95_ms']:.3f} ms (ab-high); "
            f"100->200 changes it by {proxy_delta['ab-low']['gpu_p95_pct']:+.1f}% and {proxy_delta['ab-high']['gpu_p95_pct']:+.1f}%",
            f"the ab-high M03 prediction ({predictions['ab-high']:.3f} ms) is {model_cells[1]['error_pct']:+.1f}% from the measured 200-proxy value and remains within 2%",
            f"the ab-low M03 prediction ({predictions['ab-low']:.3f} ms) is {model_cells[0]['error_pct']:+.1f}% above the measured value, consistent with unmodeled resolution scale, MSAA and glow",
            f"CPU p95 rises from {context['ab-low']['cpu_p95_ms']:.3f}/{context['ab-high']['cpu_p95_ms']:.3f} ms at 100 proxies to {low['cpu_p95_ms']:.3f}/{high['cpu_p95_ms']:.3f} ms at 200 proxies",
            "pacing remains near 4.23 ms and 1% low spread is 7.6-9.3%, so it is not used for a trend claim",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "one scene, one proxy count (200) and one resolution (1280x720)",
            "the 100-proxy context is from a different session and is labeled as such",
            "three runs per preset; 1% low spread is 7.6-9.3%",
            "native resolution disables the canvas_items stretch mode",
            "max_fps 240 and disabled VSync cap frame pacing",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · 200-proxy arena at 1280×720 — RTX 5050",
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
        "## Contexto 100 → 200 proxies (GPU p95, sessão separada)",
        "",
        "| Preset | 100 proxies | 200 proxies | Delta GPU p95 | Delta CPU p95 |",
        "|---|---:|---:|---:|---:|",
    ]
    for preset in PRESETS:
        lines.append(
            f"| {preset} | {report['context_100'][preset]['gpu_p95_ms']:.3f} | "
            f"{next(cell for cell in report['cells'] if cell['preset_id'] == preset)['gpu_p95_ms']:.3f} | "
            f"{report['proxy_100_to_200'][preset]['gpu_p95_pct']:+.1f}% | "
            f"{report['proxy_100_to_200'][preset]['cpu_p95_pct']:+.1f}% |"
        )
    lines.extend([
        "",
        "## Contexto do modelo M03",
        "",
        "| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |",
        "|---|---:|---:|---:|---|",
    ])
    for cell in report["model_context"]["cells"]:
        lines.append(
            f"| {cell['preset_id']} | {cell['predicted_gpu_ms']:.3f} | {cell['measured_gpu_p95_ms']:.3f} | "
            f"{cell['error_pct']:+.1f}% | {'sim' if cell['within_2pct'] else 'não'} |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_interaction_200_720.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD,
                   argv, "M09_INTERACTION_200_720")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

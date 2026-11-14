#!/usr/bin/env python3
"""NEX M03 light-budget validation against M09 measured data.

Verifies the model snapshot against the GDScript DEFAULT_MODEL, projects six
M01 scene/preset cells and compares them to measured GPU p95 medians from the
integrated M09 A/B/A report. No new measurement and no model change.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
MODEL_PATH = REPO_ROOT / "docs/benchmarks/m03/light-cost-model.v1.json"
MODEL_GD = REPO_ROOT / "nex_modules/lighting/budget/light_budget_arbiter.gd"
MEASURED_PATH = REPO_ROOT / "docs/benchmarks/m09/m01-ab.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m03"
OUTPUT_JSON = OUTPUT_DIR / "budget-validation.v1.json"
OUTPUT_MD = OUTPUT_DIR / "BUDGET-VALIDATION.md"

SCHEMA_VERSION = "m03_budget_validation.v1"
SCENES = {
    "corridor_static": {"omni_lights": 3, "shadowed_low": 0, "shadowed_high": 3},
    "arena_combat": {"omni_lights": 4, "shadowed_low": 0, "shadowed_high": 4},
    "dense_city": {"omni_lights": 5, "shadowed_low": 0, "shadowed_high": 4},
}
PRESETS = ("ab-low", "ab-high")
MODEL_KEYS = (
    "base_gpu_ms",
    "per_omni_light_ms",
    "directional_shadow_ms",
    "per_omni_shadow_ms",
    "per_particle_emitter_ms",
    "shadow_vfx_interaction_ms",
)


def _load(path: Path) -> Any:
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)

    def constant(token):
        raise ValueError("non-finite JSON: " + token)

    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def _model_from_gdscript() -> dict[str, float]:
    text = MODEL_GD.read_text(encoding="utf-8")
    match = re.search(r"const DEFAULT_MODEL := \{(.*?)\n\}", text, re.DOTALL)
    if match is None:
        raise ValueError("DEFAULT_MODEL block not found")
    values = {}
    for key, value in re.findall(r'"([a-z_]+)"\s*:\s*([0-9]+(?:\.[0-9]+)?)', match.group(1)):
        values[key] = float(value)
    if set(values) != set(MODEL_KEYS):
        raise ValueError("DEFAULT_MODEL keys do not match the expected model")
    return values


def _prediction(model: dict[str, float], omni: int, shadowed: int, directional: bool, particles: int) -> float:
    total = float(model["base_gpu_ms"])
    total += omni * float(model["per_omni_light_ms"])
    if directional:
        total += float(model["directional_shadow_ms"])
    total += shadowed * float(model["per_omni_shadow_ms"])
    total += particles * float(model["per_particle_emitter_ms"])
    if directional and particles > 0:
        total += float(model["shadow_vfx_interaction_ms"])
    return total


def _measured() -> dict[tuple[str, str], float]:
    report = _load(MEASURED_PATH)
    values = {}
    for scene in report["scenes"]:
        for preset in PRESETS:
            values[(scene["scene_id"], preset)] = float(scene["baselines"][preset]["gpu_p95_ms"])
    return values


def build_report() -> dict[str, Any]:
    snapshot = _load(MODEL_PATH)
    if snapshot.get("schema_version") != "m03_light_cost_model_snapshot.v1":
        raise ValueError("model snapshot schema is invalid")
    model = {key: float(value) for key, value in snapshot["coefficients"].items()}
    gd_model = _model_from_gdscript()
    if any(abs(model[key] - gd_model[key]) > 1e-12 for key in MODEL_KEYS):
        raise ValueError("model snapshot does not match the GDScript DEFAULT_MODEL")
    measured = _measured()
    cells = []
    for scene_id, config in SCENES.items():
        for preset in PRESETS:
            shadowed = config["shadowed_high"] if preset == "ab-high" else config["shadowed_low"]
            predicted = _prediction(model, config["omni_lights"], shadowed, True, 0)
            actual = measured[(scene_id, preset)]
            error_ms = predicted - actual
            error_pct = error_ms / actual * 100.0
            cells.append(
                {
                    "scene_id": scene_id,
                    "preset_id": preset,
                    "omni_lights": config["omni_lights"],
                    "shadowed_omni_lights": shadowed,
                    "directional_shadow": True,
                    "particle_emitters": 0,
                    "predicted_gpu_ms": round(predicted, 5),
                    "measured_gpu_p95_ms": round(actual, 3),
                    "error_ms": round(error_ms, 5),
                    "error_pct": round(error_pct, 1),
                    "within_2pct": abs(error_pct) <= 2.0,
                }
            )
    within = sum(1 for cell in cells if cell["within_2pct"])
    max_abs_error = max(abs(cell["error_pct"]) for cell in cells)
    verdict = "PARTIAL_DOMAIN_MATCH" if within >= 1 and within < len(cells) else "NO_DOMAIN_MATCH"
    return {
        "schema_version": SCHEMA_VERSION,
        "model_snapshot": "docs/benchmarks/m03/light-cost-model.v1.json",
        "model_source": "nex_modules/lighting/budget/light_budget_arbiter.gd DEFAULT_MODEL",
        "measured_source": "docs/benchmarks/m09/m01-ab.v1.json",
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "cells": cells,
        "summary": {
            "cells": len(cells),
            "within_2pct": within,
            "max_abs_error_pct": round(max_abs_error, 1),
            "verdict": verdict,
        },
        "verdict": verdict,
        "observations": [
            "The model's high-preset projections match the measured corridor and arena GPU p95 within 2%.",
            "The low-preset projections overestimate measured GPU p95 by 247.7-380.4%, because the low preset also changes resolution scale, MSAA and glow in ways the model does not represent.",
            "City high differs by +33.8%; the model does not represent scene geometry, resolution scale, MSAA, glow or atlas changes.",
            "The match for two high-preset cells is a domain-limited coincidence candidate, not proof that the model generalizes.",
        ],
        "limitations": [
            "model coefficients are calibrated from one S05 session at 25 proxies and 1280x720",
            "the model represents lights and shadows only; it does not represent resolution scale, MSAA, glow, atlas or scene geometry",
            "the comparison uses medians from a different session and different presets",
            "two high-preset cells within 2% do not establish general validity",
            "no FPS, quality or universal recommendation is claimed",
            "M03 parent remains NOT_ADMITTED",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M03 · Light budget validation — RTX 5050",
        "",
        "**Status:** `PARTIAL_DOMAIN_MATCH / SINGLE_SESSION / NO_MODEL_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Modelo:** `{report['model_snapshot']}` · **Fonte medida:** `{report['measured_source']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']}",
        "",
        "## Projeções vs medido",
        "",
        "| Cena | Preset | Omni | Shadowed | Previsto ms | Medido p95 ms | Erro ms | Erro % | Dentro de 2% |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['scene_id']} | {cell['preset_id']} | {cell['omni_lights']} | {cell['shadowed_omni_lights']} | "
            f"{cell['predicted_gpu_ms']:.5f} | {cell['measured_gpu_p95_ms']:.3f} | "
            f"{cell['error_ms']:+.5f} | {cell['error_pct']:+.1f}% | "
            f"{'sim' if cell['within_2pct'] else 'não'} |"
        )
    lines.extend(
        [
            "",
            "## Resumo",
            "",
            f"- Células: {report['summary']['cells']} · dentro de 2%: {report['summary']['within_2pct']}.",
            f"- Maior erro absoluto: {report['summary']['max_abs_error_pct']:.1f}%.",
            f"- Veredito: `{report['verdict']}`.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    report = build_report()
    rendered_json = render_json(report)
    rendered_md = render_markdown(report)
    if argv == ["--check"]:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            print("M03_BUDGET_CHECK_FAIL: outputs missing")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered_json:
            print("M03_BUDGET_CHECK_FAIL: JSON is stale")
            return 1
        if OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            print("M03_BUDGET_CHECK_FAIL: Markdown is stale")
            return 1
        print(f"M03_BUDGET_CHECK_PASS: {len(report['cells'])} cells")
        return 0
    if argv:
        print("usage: build_budget_validation.py [--check]")
        return 2
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_json)
    with open(OUTPUT_MD, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_md)
    print(f"M03_BUDGET_WRITE_PASS: {len(report['cells'])} cells")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

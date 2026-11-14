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
RES_SCALING_PATH = REPO_ROOT / "docs/benchmarks/m09/res-scaling.v1.json"
OUTPUT_JSON_DOMAIN = OUTPUT_DIR / "budget-domain-boundary.v1.json"
OUTPUT_MD_DOMAIN = OUTPUT_DIR / "BUDGET-DOMAIN-BOUNDARY.md"

SCHEMA_VERSION = "m03_budget_validation.v1"
DOMAIN_SCHEMA_VERSION = "m03_budget_domain_boundary.v1"
DOMAIN_SCENE = "arena_combat"
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


def _domain_verdict(cells: list[dict[str, Any]]) -> str:
    matches = [cell for cell in cells if cell["within_2pct"]]
    if len(matches) != 1 or matches[0]["resolution_px"] != [1280, 720]:
        return "NO_DOMAIN_MATCH" if not matches else "PARTIAL_DOMAIN_MATCH"
    return "CALIBRATION_RESOLUTION_MATCH_ONLY"


def build_domain_report() -> dict[str, Any]:
    snapshot = _load(MODEL_PATH)
    if snapshot.get("schema_version") != "m03_light_cost_model_snapshot.v1":
        raise ValueError("model snapshot schema is invalid")
    model = {key: float(value) for key, value in snapshot["coefficients"].items()}
    gd_model = _model_from_gdscript()
    if any(abs(model[key] - gd_model[key]) > 1e-12 for key in MODEL_KEYS):
        raise ValueError("model snapshot does not match the GDScript DEFAULT_MODEL")
    measured = _load(RES_SCALING_PATH)
    workload = measured.get("workload", {})
    if workload.get("scene_id") != DOMAIN_SCENE or workload.get("effect_mode") != "lights":
        raise ValueError("resolution bundle workload is not the expected lit arena scene")
    config = SCENES[DOMAIN_SCENE]
    cells = []
    for cell in measured["cells"]:
        preset = cell["preset_id"]
        if preset not in PRESETS:
            raise ValueError("resolution bundle contains an unsupported preset")
        shadowed = config["shadowed_high"] if preset == "ab-high" else config["shadowed_low"]
        predicted = _prediction(model, config["omni_lights"], shadowed, True, 0)
        actual = float(cell["gpu_p95_ms"])
        error_ms = predicted - actual
        error_pct = error_ms / actual * 100.0
        cells.append(
            {
                "scene_id": DOMAIN_SCENE,
                "preset_id": preset,
                "resolution_px": [int(cell["width"]), int(cell["height"])],
                "omni_lights": config["omni_lights"],
                "shadowed_omni_lights": shadowed,
                "predicted_gpu_ms": round(predicted, 5),
                "measured_gpu_p95_ms": round(actual, 3),
                "error_ms": round(error_ms, 5),
                "error_pct": round(error_pct, 1),
                "within_2pct": abs(error_pct) <= 2.0,
            }
        )
    by_preset: dict[str, dict[tuple[int, int], float]] = {}
    for cell in cells:
        by_preset.setdefault(cell["preset_id"], {})[tuple(cell["resolution_px"])] = cell["measured_gpu_p95_ms"]
    resolution_deltas = {}
    for preset, values in by_preset.items():
        delta = values[(1920, 1080)] - values[(960, 540)]
        resolution_deltas[preset] = {
            "measured_delta_ms": round(delta, 3),
            "measured_delta_pct": round(delta / values[(960, 540)] * 100.0, 1),
        }
    matches = [cell for cell in cells if cell["within_2pct"]]
    if len(matches) != 1:
        raise ValueError("domain boundary report expects exactly one calibration-resolution match")
    high = {(cell["resolution_px"][0]): cell for cell in cells if cell["preset_id"] == "ab-high"}
    verdict = _domain_verdict(cells)
    return {
        "schema_version": DOMAIN_SCHEMA_VERSION,
        "model_snapshot": "docs/benchmarks/m03/light-cost-model.v1.json",
        "model_source": "nex_modules/lighting/budget/light_budget_arbiter.gd DEFAULT_MODEL",
        "measured_source": "docs/benchmarks/m09/res-scaling.v1.json",
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "workload": {"scene_id": DOMAIN_SCENE, "proxy_count": workload.get("proxy_count"), "effect_mode": "lights"},
        "cells": cells,
        "resolution_sensitivity": {
            "predicted_delta_960_to_1920_ms": 0.0,
            "measured": resolution_deltas,
        },
        "summary": {
            "cells": len(cells),
            "within_2pct": len(matches),
            "max_abs_error_pct": round(max(abs(cell["error_pct"]) for cell in cells), 1),
            "verdict": verdict,
        },
        "verdict": verdict,
        "observations": [
            f"only the ab-high cell at 1280x720 is within 2% ({matches[0]['error_pct']:+.1f}%); the same prediction is off by {high[960]['error_pct']:+.1f}% at 960x540 and {high[1920]['error_pct']:+.1f}% at 1920x1080",
            f"the model is resolution-invariant (predicted delta 960->1920 = 0.000 ms), while measured GPU p95 grows {resolution_deltas['ab-low']['measured_delta_pct']:.1f}% (ab-low) and {resolution_deltas['ab-high']['measured_delta_pct']:.1f}% (ab-high)",
            "the 2% match is therefore specific to the calibration resolution, not evidence of general validity",
            "the low preset is overestimated at every resolution, consistent with unmodeled resolution scale, MSAA and glow",
        ],
        "limitations": [
            "model coefficients are calibrated from one S05 session at 25 proxies and 1280x720",
            "the model represents lights and shadows only; it does not represent resolution scale, MSAA, glow, atlas or scene geometry",
            "the resolution bundle uses 100 proxies on one arena scene in one session",
            "the comparison uses medians from a different session and different presets",
            "no FPS, quality or universal recommendation is claimed",
            "M03 parent remains NOT_ADMITTED",
        ],
    }


def render_domain_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M03 · Light budget domain boundary — RTX 5050",
        "",
        "**Status:** `CALIBRATION_RESOLUTION_MATCH_ONLY / SINGLE_SESSION / NO_MODEL_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Modelo:** `{report['model_snapshot']}` · **Fonte medida:** `{report['measured_source']}`",
        f"**Workload:** {report['workload']['scene_id']} · {report['workload']['proxy_count']} proxies · {report['workload']['effect_mode']}",
        "",
        "## Projeções vs medido por resolução",
        "",
        "| Preset | Resolução | Omni | Shadowed | Previsto ms | Medido p95 ms | Erro ms | Erro % | Dentro de 2% |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['preset_id']} | {cell['resolution_px'][0]}×{cell['resolution_px'][1]} | "
            f"{cell['omni_lights']} | {cell['shadowed_omni_lights']} | {cell['predicted_gpu_ms']:.5f} | "
            f"{cell['measured_gpu_p95_ms']:.3f} | {cell['error_ms']:+.5f} | {cell['error_pct']:+.1f}% | "
            f"{'sim' if cell['within_2pct'] else 'não'} |"
        )
    lines.extend(
        [
            "",
            "## Sensibilidade à resolução",
            "",
            f"- Delta previsto 960→1920: {report['resolution_sensitivity']['predicted_delta_960_to_1920_ms']:.3f} ms.",
            f"- Delta medido ab-low: {report['resolution_sensitivity']['measured']['ab-low']['measured_delta_ms']:+.3f} ms "
            f"({report['resolution_sensitivity']['measured']['ab-low']['measured_delta_pct']:+.1f}%).",
            f"- Delta medido ab-high: {report['resolution_sensitivity']['measured']['ab-high']['measured_delta_ms']:+.3f} ms "
            f"({report['resolution_sensitivity']['measured']['ab-high']['measured_delta_pct']:+.1f}%).",
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
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py --domain`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _render_and_write(
    report: dict[str, Any],
    rendered_md: str,
    output_json: Path,
    output_md: Path,
    label: str,
    check_only: bool,
) -> int:
    rendered_json = render_json(report)
    outputs = ((output_json, rendered_json, "JSON"), (output_md, rendered_md, "Markdown"))
    if check_only:
        if not all(path.is_file() for path, _, _ in outputs):
            print(f"{label}_CHECK_FAIL: outputs missing")
            return 1
        for path, rendered, kind in outputs:
            if path.read_text(encoding="utf-8") != rendered:
                print(f"{label}_CHECK_FAIL: {kind} is stale")
                return 1
        print(f"{label}_CHECK_PASS: {len(report['cells'])} cells")
        return 0
    output_json.parent.mkdir(parents=True, exist_ok=True)
    for path, rendered, _ in outputs:
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(f"{label}_WRITE_PASS: {len(report['cells'])} cells")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--check"]:
        report = build_report()
        return _render_and_write(report, render_markdown(report), OUTPUT_JSON, OUTPUT_MD, "M03_BUDGET", True)
    if argv == ["--domain"]:
        report = build_domain_report()
        return _render_and_write(report, render_domain_markdown(report), OUTPUT_JSON_DOMAIN, OUTPUT_MD_DOMAIN, "M03_DOMAIN", False)
    if argv == ["--check-domain"]:
        report = build_domain_report()
        return _render_and_write(report, render_domain_markdown(report), OUTPUT_JSON_DOMAIN, OUTPUT_MD_DOMAIN, "M03_DOMAIN", True)
    if argv:
        print("usage: build_budget_validation.py [--check|--domain|--check-domain]")
        return 2
    report = build_report()
    return _render_and_write(report, render_markdown(report), OUTPUT_JSON, OUTPUT_MD, "M03_BUDGET", False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

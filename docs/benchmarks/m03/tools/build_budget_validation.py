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
PROXY_200_PATH = REPO_ROOT / "docs/benchmarks/m09/interaction-200-720.v1.json"
RES_1440_PATH = REPO_ROOT / "docs/benchmarks/m09/res-scaling-1440.v1.json"
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


def _cell_table_lines(cells: list[dict[str, Any]]) -> list[str]:
    lines = ["", "| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |", "|---|---:|---:|---:|---|"]
    for cell in cells:
        lines.append(
            f"| {cell['preset_id']} | {cell['predicted_gpu_ms']:.3f} | {cell['measured_gpu_p95_ms']:.3f} | "
            f"{cell['error_pct']:+.1f}% | {'sim' if cell['within_2pct'] else 'não'} |"
        )
    return lines


def _summary_and_footer(report: dict[str, Any], footer: str) -> list[str]:
    lines = [
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
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", footer, ""])
    return lines


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
    lines.extend(_summary_and_footer(
        report,
        "Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py`; não é benchmark nem claim de ganho.",
    ))
    return "\n".join(lines)


def _load_model() -> dict[str, float]:
    snapshot = _load(MODEL_PATH)
    if snapshot.get("schema_version") != "m03_light_cost_model_snapshot.v1":
        raise ValueError("model snapshot schema is invalid")
    model = {key: float(value) for key, value in snapshot["coefficients"].items()}
    gd_model = _model_from_gdscript()
    if any(abs(model[key] - gd_model[key]) > 1e-12 for key in MODEL_KEYS):
        raise ValueError("model snapshot does not match the GDScript DEFAULT_MODEL")
    return model


def _domain_cell(model: dict[str, float], config: dict[str, int], preset: str,
                 width: int, height: int, measured: float) -> dict[str, Any]:
    shadowed = config["shadowed_high"] if preset == "ab-high" else config["shadowed_low"]
    predicted = _prediction(model, config["omni_lights"], shadowed, True, 0)
    error_ms = predicted - measured
    error_pct = error_ms / measured * 100.0
    return {
        "scene_id": DOMAIN_SCENE,
        "preset_id": preset,
        "resolution_px": [width, height],
        "omni_lights": config["omni_lights"],
        "shadowed_omni_lights": shadowed,
        "predicted_gpu_ms": round(predicted, 5),
        "measured_gpu_p95_ms": round(measured, 3),
        "error_ms": round(error_ms, 5),
        "error_pct": round(error_pct, 1),
        "within_2pct": abs(error_pct) <= 2.0,
    }


def _evidence_cells(path: Path, model: dict[str, float], config: dict[str, int],
                    width: int, height: int) -> list[dict[str, Any]]:
    report = _load(path)
    workload = report.get("workload", {})
    if workload.get("scene_id") != DOMAIN_SCENE or workload.get("effect_mode") != "lights":
        raise ValueError(f"{path.name}: workload is not the expected lit arena scene")
    cells = []
    for cell in report["cells"]:
        preset = cell["preset_id"]
        if preset not in PRESETS:
            raise ValueError(f"{path.name}: unsupported preset")
        if int(cell["width"]) != width or int(cell["height"]) != height:
            raise ValueError(f"{path.name}: unexpected resolution")
        cells.append(_domain_cell(model, config, preset, width, height, float(cell["gpu_p95_ms"])))
    return cells


def _domain_verdict(cells: list[dict[str, Any]]) -> str:
    matches = [cell for cell in cells if cell["within_2pct"]]
    if len(matches) != 1 or matches[0]["resolution_px"] != [1280, 720]:
        return "NO_DOMAIN_MATCH" if not matches else "PARTIAL_DOMAIN_MATCH"
    return "CALIBRATION_RESOLUTION_MATCH_ONLY"


def build_domain_report() -> dict[str, Any]:
    model = _load_model()
    config = SCENES[DOMAIN_SCENE]
    measured = _load(RES_SCALING_PATH)
    workload = measured.get("workload", {})
    if workload.get("scene_id") != DOMAIN_SCENE or workload.get("effect_mode") != "lights":
        raise ValueError("resolution bundle workload is not the expected lit arena scene")
    cells = []
    for cell in measured["cells"]:
        preset = cell["preset_id"]
        if preset not in PRESETS:
            raise ValueError("resolution bundle contains an unsupported preset")
        cells.append(_domain_cell(model, config, preset, int(cell["width"]), int(cell["height"]),
                                  float(cell["gpu_p95_ms"])))
    proxy_cells = _evidence_cells(PROXY_200_PATH, model, config, 1280, 720)
    highres_cells = _evidence_cells(RES_1440_PATH, model, config, 2560, 1440)
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
    proxy_match = [cell for cell in proxy_cells if cell["within_2pct"]]
    if len(proxy_match) != 1 or proxy_match[0]["preset_id"] != "ab-high":
        raise ValueError("proxy robustness expects the ab-high calibration match")
    highres_matches = [cell for cell in highres_cells if cell["within_2pct"]]
    high = {cell["resolution_px"][0]: cell for cell in cells if cell["preset_id"] == "ab-high"}
    proxy_by_preset = {cell["preset_id"]: cell for cell in proxy_cells}
    highres_by_preset = {cell["preset_id"]: cell for cell in highres_cells}
    verdict = _domain_verdict(cells)
    return {
        "schema_version": DOMAIN_SCHEMA_VERSION,
        "model_snapshot": "docs/benchmarks/m03/light-cost-model.v1.json",
        "model_source": "nex_modules/lighting/budget/light_budget_arbiter.gd DEFAULT_MODEL",
        "measured_source": "docs/benchmarks/m09/res-scaling.v1.json",
        "evidence_bundles": [
            "docs/benchmarks/m09/res-scaling.v1.json",
            "docs/benchmarks/m09/interaction-200-720.v1.json",
            "docs/benchmarks/m09/res-scaling-1440.v1.json",
        ],
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "workload": {"scene_id": DOMAIN_SCENE, "proxy_count": workload.get("proxy_count"), "effect_mode": "lights"},
        "cells": cells,
        "proxy_robustness": {
            "source": "docs/benchmarks/m09/interaction-200-720.v1.json",
            "resolution_px": [1280, 720],
            "proxy_count": 200,
            "cells": proxy_cells,
            "high_within_2pct": True,
        },
        "high_resolution": {
            "source": "docs/benchmarks/m09/res-scaling-1440.v1.json",
            "resolution_px": [2560, 1440],
            "proxy_count": 100,
            "cells": highres_cells,
            "matches_within_2pct": len(highres_matches),
        },
        "resolution_sensitivity": {
            "predicted_delta_960_to_1920_ms": 0.0,
            "measured": resolution_deltas,
        },
        "summary": {
            "cells": len(cells),
            "within_2pct": len(matches),
            "max_abs_error_pct": round(max(abs(cell["error_pct"]) for cell in cells), 1),
            "proxy_cells": len(proxy_cells),
            "high_resolution_cells": len(highres_cells),
            "within_2pct_total": len(matches) + len(proxy_match) + len(highres_matches),
            "verdict": verdict,
        },
        "verdict": verdict,
        "observations": [
            f"in the resolution grid, only the ab-high cell at 1280x720 is within 2% ({matches[0]['error_pct']:+.1f}%); the same prediction is off by {high[960]['error_pct']:+.1f}% at 960x540 and {high[1920]['error_pct']:+.1f}% at 1920x1080",
            f"the model is resolution-invariant (predicted delta 960->1920 = 0.000 ms), while measured GPU p95 grows {resolution_deltas['ab-low']['measured_delta_pct']:.1f}% (ab-low) and {resolution_deltas['ab-high']['measured_delta_pct']:.1f}% (ab-high)",
            f"at 200 proxies and 1280x720 the ab-high prediction remains within 2% ({proxy_by_preset['ab-high']['error_pct']:+.1f}%), while ab-low is {proxy_by_preset['ab-low']['error_pct']:+.1f}% above measured",
            f"at 2560x1440 the ab-high prediction is {highres_by_preset['ab-high']['error_pct']:+.1f}% and ab-low {highres_by_preset['ab-low']['error_pct']:+.1f}%; neither is within 2%",
            "the 2% match is confined to 1280x720 and is robust to a 100->200 proxy change, but not to resolution changes",
        ],
        "limitations": [
            "model coefficients are calibrated from one S05 session at 25 proxies and 1280x720",
            "the model represents lights and shadows only; it does not represent resolution scale, MSAA, glow, atlas or scene geometry",
            "the resolution grid uses 100 proxies on one arena scene in one session",
            "the 200/1280 and 2560/1440 evidence comes from separate sessions and is labeled as such",
            "the comparison uses medians from different sessions and different presets",
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
            "## Robustez a proxies (200/1280)",
            * _cell_table_lines(report["proxy_robustness"]["cells"]),
            "",
            "## Alta resolução (2560×1440)",
            * _cell_table_lines(report["high_resolution"]["cells"]),
        ]
    )
    lines.extend(_summary_and_footer(
        report,
        "Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py --domain`; não é benchmark nem claim de ganho.",
    ))
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

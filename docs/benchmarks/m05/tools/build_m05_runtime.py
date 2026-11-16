#!/usr/bin/env python3
"""Build the M05 VFX runtime report from native captures and stress runs."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png  # noqa: E402 - shared local tool module
from preset_report import load_capture, summarize, transform_run  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
VISUAL = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m05-vfx"
STRESS = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m05-vfx-perf"
BASELINE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m05-vfx-baseline"
SMOKE = VISUAL / "spell-fx-smoke-2026-11-15.json"
OUTPUT = REPO / "docs" / "benchmarks" / "m05"
REPORT_JSON = OUTPUT / "vfx-runtime.v1.json"
REPORT_MD = OUTPUT / "VFX-RUNTIME.md"
SOURCE_SHA = "dd840f86023057a4dc8af92148cdf36911175613"
SCENES = ("corridor_static", "arena_combat", "dense_city")
ELEMENTS = {
    "fire": {"particles": 64, "mesh_instances": 0, "role": "damage over time"},
    "frost": {"particles": 48, "mesh_instances": 0, "role": "control burst"},
    "lightning": {"particles": 40, "mesh_instances": 1, "role": "beam and sparks"},
    "smoke": {"particles": 32, "mesh_instances": 0, "role": "ambient decay"},
    "impact": {"particles": 40, "mesh_instances": 0, "role": "hit echo"},
    "projectile": {"particles": 24, "mesh_instances": 2, "role": "projectile trail"},
}
ALLOWED_VALIDATION = {"PASS"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pct(new: float, old: float) -> float:
    return round((new - old) / old * 100.0, 2)


def _load_manifest(directory: Path, expected: int) -> dict[str, Any]:
    manifest = load_json(directory / "runs.v1.json")
    if manifest.get("schema_version") != "m05_vfx_runs.v1":
        raise ValueError("runs manifest schema is invalid")
    if manifest.get("source_sha") != SOURCE_SHA:
        raise ValueError("runs manifest source SHA is stale")
    runs = manifest.get("runs", [])
    if len(runs) != expected:
        raise ValueError(f"runs manifest must contain {expected} runs")
    if [entry.get("sequence") for entry in runs] != list(range(1, expected + 1)):
        raise ValueError("runs manifest sequence is invalid")
    return manifest


def _group_metrics(manifest: dict[str, Any], directory: Path) -> dict[int, dict[str, Any]]:
    groups: dict[int, list[dict[str, Any]]] = {}
    for entry in manifest["runs"]:
        capture = load_capture(directory, entry["run_id"], entry["scene"], entry["layout"],
                               int(entry["proxy_count"]), include_allocation=True)
        groups.setdefault(int(entry["count"]), []).append(
            transform_run(entry, capture, include_allocation=True))
    return {count: summarize(group, include_allocation=True) for count, group in groups.items()}


def _visual_cells() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for scene in SCENES:
        baseline = read_png(VISUAL / f"{scene}_baseline.png")
        if (baseline.width, baseline.height) != (1920, 1080):
            raise ValueError("baseline capture is not 1920x1080")
        for element in ELEMENTS:
            path = VISUAL / f"{scene}_{element}.png"
            image = read_png(path)
            if (image.width, image.height) != (1920, 1080):
                raise ValueError(f"{path.name} is not 1920x1080")
            diff = compare(baseline, image, 2)
            if float(diff["changed_pixels_pct"]) <= 0.0:
                raise ValueError(f"{path.name} did not change any pixel")
            cells.append({
                "scene": scene,
                "element": element,
                "png_bytes": path.stat().st_size,
                "sha256": _sha(path),
                "changed_pixels_pct": diff["changed_pixels_pct"],
                "mean_abs_diff": diff["mean_abs_diff"],
                "psnr_db": diff["psnr_db"],
            })
    all25 = VISUAL / "arena_combat_all25.png"
    all25_diff = compare(read_png(VISUAL / "arena_combat_baseline.png"), read_png(all25), 2)
    clarity = {
        "path": all25.name,
        "sha256": _sha(all25),
        "png_bytes": all25.stat().st_size,
        "changed_pixels_pct": all25_diff["changed_pixels_pct"],
        "mean_abs_diff": all25_diff["mean_abs_diff"],
        "psnr_db": all25_diff["psnr_db"],
        "events": 25,
        "lights": 8,
    }
    return cells, clarity


def build_report() -> dict[str, Any]:
    smoke = load_json(SMOKE)
    if smoke.get("verdict") not in ALLOWED_VALIDATION or smoke.get("source_sha") != SOURCE_SHA:
        raise ValueError("SpellFX smoke is not a valid PASS for this source")
    if int(smoke.get("checks", 0)) != 12:
        raise ValueError("SpellFX smoke must pass 12 checks")
    cells, clarity = _visual_cells()
    stress = _group_metrics(_load_manifest(STRESS, 9), STRESS)
    baseline = _group_metrics(_load_manifest(BASELINE, 3), BASELINE)
    if sorted(stress) != [1, 25, 100] or sorted(baseline) != [0]:
        raise ValueError("stress groups are incomplete")
    base = baseline[0]
    rows = []
    for count in (1, 25, 100):
        item = stress[count]
        rows.append({
            "events": count,
            "runs": item["runs"],
            "gpu_p95_ms": item["gpu_p95_ms"],
            "gpu_p99_ms": item["gpu_p99_ms"],
            "cpu_p95_ms": item["cpu_p95_ms"],
            "pacing_p95_ms": item["pacing_p95_ms"],
            "one_percent_low_fps": item["one_percent_low_fps"],
            "renderer_allocation_bytes": item["renderer_allocation_bytes_median"],
            "gpu_p95_vs_baseline_pct": _pct(item["gpu_p95_ms"], base["gpu_p95_ms"]),
            "one_percent_low_vs_baseline_pct": _pct(item["one_percent_low_fps"], base["one_percent_low_fps"]),
            "allocation_delta_bytes": item["renderer_allocation_bytes_median"] - base["renderer_allocation_bytes_median"],
            "gpu_p95_spread_pct": item["gpu_p95_spread_pct"],
            "one_percent_low_spread_pct": item["one_percent_low_spread_pct"],
        })
    by_element: dict[str, Any] = {}
    for element, meta in ELEMENTS.items():
        selected = [cell for cell in cells if cell["element"] == element]
        by_element[element] = {
            **meta,
            "scenes": len(selected),
            "changed_pixels_pct_median": round(statistics.median(
                [cell["changed_pixels_pct"] for cell in selected]), 3),
            "changed_pixels_pct_max": max(cell["changed_pixels_pct"] for cell in selected),
            "png_bytes_median": int(statistics.median([cell["png_bytes"] for cell in selected])),
        }
    return {
        "schema_version": "m05_vfx_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "s01": {
            "schema": "spellfx.v1",
            "checks": int(smoke["checks"]),
            "failures": list(smoke["failures"]),
            "max_active": 128,
            "max_per_vfx": 64,
            "quality_tiers": ["low", "medium", "high"],
            "events_in_capture": 6,
            "lights_in_capture": 6,
            "gameplay_authority": "data-only; damage and hit detection remain gameplay-owned",
            "verdict": "SPELLFX_CONTRACT_VERIFIED",
        },
        "s02": {
            "elements": by_element,
            "captures": cells,
            "scenes": list(SCENES),
            "verdict": "ELEMENTAL_FX_RENDERED",
        },
        "s03": {
            "projectile_particles": ELEMENTS["projectile"]["particles"],
            "projectile_meshes": ELEMENTS["projectile"]["mesh_instances"],
            "impact_particles": ELEMENTS["impact"]["particles"],
            "authoritative_hit_detection": False,
            "collision_enabled": False,
            "verdict": "PROJECTILE_HITECHO_VISUAL_ONLY",
        },
        "s04": {
            **clarity,
            "telegraph_system": False,
            "flash_reduction": False,
            "threat_budget_scheduler": False,
            "verdict": "COMBAT_CLARITY_LIMITED",
        },
        "s05": {
            "baseline": {
                "events": 0,
                "runs": base["runs"],
                "gpu_p95_ms": base["gpu_p95_ms"],
                "cpu_p95_ms": base["cpu_p95_ms"],
                "pacing_p95_ms": base["pacing_p95_ms"],
                "one_percent_low_fps": base["one_percent_low_fps"],
                "renderer_allocation_bytes": base["renderer_allocation_bytes_median"],
            },
            "stress": rows,
            "pool_max_active": 128,
            "pool_max_per_vfx": 64,
            "lifecycle_checks": 12,
            "verdict": "FX_BUDGET_AND_LIFECYCLE_DERIVED",
        },
        "s06": {
            "decisions": [
                {"id": "GPUParticles3D elemental library", "decision": "GO",
                 "evidence": "6 original effects rendered in 3 scenes at 1920x1080"},
                {"id": "SpellFX request contract", "decision": "GO",
                 "evidence": "12 smoke checks: idempotency, authority, budgets, cancel and expiry"},
                {"id": "LightBridge VFX lights", "decision": "GO",
                 "evidence": "6 accepted lights for 6 events and 8 accepted for 25/100 events"},
                {"id": "PulsePool lifecycle", "decision": "GO_WITH_LIMITATIONS",
                 "evidence": "request budgets and expiry verified; no warm pool or shader prewarm"},
                {"id": "Projectile/HitEcho", "decision": "GO_WITH_LIMITATIONS",
                 "evidence": "visual trail and impact only; no authoritative hit or collision"},
                {"id": "Combat clarity / ThreatBudget", "decision": "NO_GO",
                 "evidence": "no telegraphs, flash reduction or threat scheduler implemented"},
                {"id": "Cinematic quality / PoE2 parity", "decision": "NO_GO",
                 "evidence": "no production art, no parity claim and no quality metric"},
            ]
        },
        "s07": {
            "visual_captures": len(cells) + 1,
            "baseline_captures": len(SCENES),
            "stress_runs": 9,
            "baseline_runs": 3,
            "scenes": len(SCENES),
            "third_party_assets": 0,
            "verdict": "M05_VFX_QA_VERIFIED",
        },
        "verdict": "M05_VFX_REFERENCE_DERIVED",
        "observations": [
            "6 original elemental effects are rendered in corridor, arena and city scenes",
            f"25 simultaneous effects with 8 accepted lights change {clarity['changed_pixels_pct']:.3f}% of the arena frame",
            f"100 events keep GPU p95 at {rows[2]['gpu_p95_ms']:.3f} ms and 1% low at {rows[2]['one_percent_low_fps']:.2f} FPS on the reference GPU",
            "GPU p95 rises " + " / ".join(f"{row['gpu_p95_vs_baseline_pct']:+.2f}%" for row in rows) + " for 1 / 25 / 100 events versus no VFX",
            "1% low changes " + " / ".join(f"{row['one_percent_low_vs_baseline_pct']:+.2f}%" for row in rows) + " for 1 / 25 / 100 events versus no VFX",
            "SpellFX smoke passes 12 checks and keeps gameplay authority outside the visual layer",
        ],
        "limitations": [
            "single session, one GPU and driver; static frames for the visual matrix",
            "no authoritative hit detection, projectile physics or GPU particle collision",
            "no telegraphs, flash reduction, threat scheduler or accessibility options",
            "no warm pool, shader prewarm, overdraw metric or VRAM budget",
            "no production art, no cinematic-quality metric and no PoE2 parity claim",
        ],
        "runs": 12,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M05 · VFX runtime",
        "",
        "**Status:** `M05_VFX_REFERENCE_DERIVED / NATIVE_CAPTURES / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · SpellFX",
        "",
        f"- Contrato `{report['s01']['schema']}`: **{report['s01']['checks']} checks**, "
        f"falhas `{report['s01']['failures']}`.",
        f"- Budgets: `max_active={report['s01']['max_active']}`, `max_per_vfx={report['s01']['max_per_vfx']}`; "
        f"tiers {', '.join(report['s01']['quality_tiers'])}.",
        f"- Captura: {report['s01']['events_in_capture']} eventos, {report['s01']['lights_in_capture']} luzes aceitas.",
        f"- Autoridade: {report['s01']['gameplay_authority']}.",
        "",
        "## S02 · Biblioteca elemental",
        "",
        "| Elemento | Partículas | Meshes | Diferença mediana | Máximo |",
        "|---|---:|---:|---:|---:|",
    ]
    for element, item in report["s02"]["elements"].items():
        lines.append(f"| {element} | {item['particles']} | {item['mesh_instances']} | "
                     f"{item['changed_pixels_pct_median']:.3f}% | {item['changed_pixels_pct_max']:.3f}% |")
    lines.extend([
        "",
        "| Cena | Elemento | Pixels alterados | Mean abs | PSNR | PNG |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for cell in report["s02"]["captures"]:
        lines.append(f"| {cell['scene']} | {cell['element']} | {cell['changed_pixels_pct']:.3f}% | "
                     f"{cell['mean_abs_diff']:.4f} | {cell['psnr_db']:.2f} dB | {cell['png_bytes']} B |")
    lines.extend([
        "",
        "## S03 · Projectile/HitEcho",
        "",
        f"- Projétil: {report['s03']['projectile_particles']} partículas e "
        f"{report['s03']['projectile_meshes']} meshes de trilha; impacto: "
        f"{report['s03']['impact_particles']} partículas.",
        "- Hit autoritativo, física e colisão: **não implementados**; a camada é somente visual.",
        "",
        "## S04 · Combat clarity",
        "",
        f"- 25 eventos com {report['s04']['lights']} luzes alteram "
        f"**{report['s04']['changed_pixels_pct']:.3f}%** do frame da arena.",
        "- Telegraphs, redução de flashes e ThreatBudget Scheduler: **não implementados**.",
        "",
        "## S05 · FX budget e ciclo de vida",
        "",
        "| Eventos | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | GPU vs base | 1% low vs base |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| 0 | {report['s05']['baseline']['gpu_p95_ms']:.3f} ms | — | "
        f"{report['s05']['baseline']['cpu_p95_ms']:.3f} ms | {report['s05']['baseline']['pacing_p95_ms']:.3f} ms | "
        f"{report['s05']['baseline']['one_percent_low_fps']:.2f} | — | — |",
    ])
    for row in report["s05"]["stress"]:
        lines.append(f"| {row['events']} | {row['gpu_p95_ms']:.3f} ms | {row['gpu_p99_ms']:.3f} ms | "
                     f"{row['cpu_p95_ms']:.3f} ms | {row['pacing_p95_ms']:.3f} ms | "
                     f"{row['one_percent_low_fps']:.2f} | {row['gpu_p95_vs_baseline_pct']:+.2f}% | "
                     f"{row['one_percent_low_vs_baseline_pct']:+.2f}% |")
    lines.extend([
        "",
        f"- Alocação do renderer: {report['s05']['baseline']['renderer_allocation_bytes']} B sem VFX; "
        + "; ".join(f"{row['events']} evento{'s' if row['events'] != 1 else ''} "
                    f"{row['renderer_allocation_bytes']} B ({row['allocation_delta_bytes']:+d} B)"
                    for row in report["s05"]["stress"]) + ".",
        f"- Pool: até {report['s05']['pool_max_active']} ativos e {report['s05']['pool_max_per_vfx']} por VFX; "
        f"{report['s05']['lifecycle_checks']} checks de ciclo de vida.",
        "",
        "## S06 · decisões",
        "",
        "| Tecnologia | Decisão | Evidência |",
        "|---|---|---|",
    ])
    for decision in report["s06"]["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend([
        "",
        "## S07 · QA",
        "",
        f"- {report['s07']['visual_captures']} capturas visuais, "
        f"{report['s07']['baseline_captures']} baselines, "
        f"{report['s07']['stress_runs']} runs de stress e "
        f"{report['s07']['baseline_runs']} runs sem VFX.",
        f"- {report['s07']['scenes']} cenas; {report['s07']['third_party_assets']} assets de terceiros.",
        "",
        "## Observações",
        "",
    ])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m05/tools/build_m05_runtime.py`; não é paridade com PoE2.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M05_VFX_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

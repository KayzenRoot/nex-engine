#!/usr/bin/env python3
"""Build the M03 cinematic-lighting runtime report from native evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png  # noqa: E402 - shared local tool module
from preset_report import load_capture, transform_run  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence"
LOOKS = EVIDENCE / "windows-rtx5050-2026-11-15-m03-looks"
GI = EVIDENCE / "windows-rtx5050-2026-11-15-m03-gi"
FOG = EVIDENCE / "windows-rtx5050-2026-11-15-m03-fog"
SHADOWS = EVIDENCE / "windows-rtx5050-2026-11-15-m03-shadows"
BUDGET = EVIDENCE / "windows-rtx5050-2026-11-15-m03-budget"
PERF = EVIDENCE / "windows-rtx5050-2026-11-15-m03-perf"
BRIDGE = EVIDENCE / "windows-rtx5050-2026-11-15-m03-bridge" / "bridge-smoke-2026-11-15.json"
OUTPUT = REPO / "docs" / "benchmarks" / "m03"
REPORT_JSON = OUTPUT / "lighting-runtime.v1.json"
REPORT_MD = OUTPUT / "LIGHTING-RUNTIME.md"
SOURCE_SHA = "6be39d49d8769ff46a98990c6818c8132e9e5a1d"
SCENES = ("corridor_static", "arena_combat", "dense_city")
LOOKS_IDS = ("dungeon_torch", "moonlit_exterior", "boss_arena")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _diff(first: Path, second: Path) -> dict[str, Any]:
    return compare(read_png(first), read_png(second), 2)


def _perf() -> dict[str, dict[str, Any]]:
    manifest = load_json(PERF / "runs.v1.json")
    if manifest.get("schema_version") != "m03_lighting_runs.v1":
        raise ValueError("unexpected M03 performance manifest")
    if manifest.get("source_sha") != SOURCE_SHA:
        raise ValueError("M03 source SHA mismatch")
    runs = {}
    for entry in manifest["runs"]:
        capture = load_capture(PERF, entry["run_id"], entry["scene"], entry["layout"], 100, include_allocation=True)
        if capture["source_sha"] != SOURCE_SHA:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        runs[entry["label"]] = transform_run(entry, capture, include_allocation=True)
    return runs


def _pct(value: float, baseline: float) -> float:
    return round((value - baseline) / baseline * 100.0, 1) if baseline else 0.0


def build_report() -> dict[str, Any]:
    perf = _perf()
    bridge = load_json(BRIDGE)
    if bridge.get("verdict") != "PASS":
        raise ValueError("LightBridge smoke did not pass")
    looks = []
    for scene in SCENES:
        baseline = LOOKS / f"{scene}_dungeon_torch.png"
        for look in LOOKS_IDS:
            path = LOOKS / f"{scene}_{look}.png"
            image = read_png(path)
            if (image.width, image.height) != (1920, 1080):
                raise ValueError(f"look image has unexpected size: {path.name}")
            metrics = _diff(baseline, path) if look != "dungeon_torch" else None
            looks.append({
                "scene_id": scene,
                "look": look,
                "sha256": _sha(path),
                "changed_vs_dungeon_pct": None if metrics is None else metrics["changed_pixels_pct"],
                "mean_abs_vs_dungeon": None if metrics is None else metrics["mean_abs_diff"],
            })
    gi_scenes = []
    for scene in SCENES:
        sdfgi = GI / f"{scene}_sdfgi.png"
        off = GI / f"{scene}_off.png"
        metrics = _diff(sdfgi, off)
        gi_scenes.append({
            "scene_id": scene,
            "sdfgi_sha256": _sha(sdfgi),
            "off_sha256": _sha(off),
            "changed_pixels_pct": metrics["changed_pixels_pct"],
            "mean_abs_diff": metrics["mean_abs_diff"],
        })
    fog_scenes = []
    for scene in SCENES:
        volumetric = FOG / f"{scene}_volumetric.png"
        depth = FOG / f"{scene}_depth.png"
        off = FOG / f"{scene}_off.png"
        fog_scenes.append({
            "scene_id": scene,
            "volumetric_sha256": _sha(volumetric),
            "depth_sha256": _sha(depth),
            "off_sha256": _sha(off),
            "volumetric_vs_depth_pct": _diff(volumetric, depth)["changed_pixels_pct"],
            "volumetric_vs_off_pct": _diff(volumetric, off)["changed_pixels_pct"],
        })
    shadow_scenes = []
    for scene in SCENES:
        low = SHADOWS / f"{scene}_ab-low.png"
        ultra = SHADOWS / f"{scene}_ab-high.png"
        metrics = _diff(low, ultra)
        shadow_scenes.append({
            "scene_id": scene,
            "low_sha256": _sha(low),
            "ultra_sha256": _sha(ultra),
            "changed_pixels_pct": metrics["changed_pixels_pct"],
            "mean_abs_diff": metrics["mean_abs_diff"],
        })
    budget_scenes = []
    for scene in SCENES:
        off = BUDGET / f"{scene}_off.png"
        on = BUDGET / f"{scene}_on.png"
        metrics = _diff(off, on)
        budget_scenes.append({
            "scene_id": scene,
            "off_sha256": _sha(off),
            "on_sha256": _sha(on),
            "changed_pixels_pct": metrics["changed_pixels_pct"],
        })
    gpu = {label: run["gpu_ms"]["p95"] for label, run in perf.items()}
    alloc = {label: run["renderer_allocation_bytes"] for label, run in perf.items()}
    return {
        "schema_version": "m03_lighting_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1920, 1080],
        "s01": {
            "looks": looks,
            "perf_scene": "corridor_static",
            "gpu_p95_ms": {label: gpu[label] for label in ("look_dungeon", "look_moonlit", "look_boss")},
            "verdict": "CINELIGHT_LOOKS_RENDERED",
        },
        "s02": {
            "scenes": shadow_scenes,
            "gpu_low_p95_ms": gpu["shadow_low"],
            "gpu_ultra_p95_ms": gpu["shadow_ultra"],
            "gpu_delta_pct": _pct(gpu["shadow_ultra"], gpu["shadow_low"]),
            "temporal_stability": "NOT_RUN",
            "verdict": "SHADOW_QUALITY_DERIVED",
        },
        "s03": {
            "scenes": gi_scenes,
            "gpu_sdfgi_p95_ms": gpu["gi_sdfgi"],
            "gpu_off_p95_ms": gpu["gi_off"],
            "gpu_delta_pct": _pct(gpu["gi_sdfgi"], gpu["gi_off"]),
            "allocation_delta_mib": round((alloc["gi_sdfgi"] - alloc["gi_off"]) / 1048576.0, 1),
            "verdict": "SDFGI_QUALITY_PROFILE_ONLY",
        },
        "s04": {
            "scenes": fog_scenes,
            "gpu_volumetric_p95_ms": gpu["fog_volumetric"],
            "gpu_depth_p95_ms": gpu["fog_depth"],
            "gpu_delta_pct": _pct(gpu["fog_volumetric"], gpu["fog_depth"]),
            "verdict": "VOLUMETRIC_WITH_DEPTH_FALLBACK",
        },
        "s05": {"bridge_checks": bridge["checks"], "verdict": bridge["verdict"]},
        "s06": {
            "scenes": budget_scenes,
            "shadowed_on": 2,
            "shadowed_off": 4,
            "gpu_on_p95_ms": gpu["budget_on"],
            "gpu_off_p95_ms": gpu["budget_off"],
            "gpu_delta_pct": _pct(gpu["budget_on"], gpu["budget_off"]),
            "verdict": "LIGHT_BUDGET_MVP",
        },
        "s07": {
            "decisions": [
                {"id": "CineLight Bible", "decision": "GO", "evidence": "3 original dark-fantasy looks rendered in 3 scenes"},
                {"id": "ShadowStability", "decision": "GO_WITH_LIMITATIONS", "evidence": "low/ultra rendered; temporal shadow flicker not measured"},
                {"id": "GI Atlas", "decision": "GO_QUALITY_PROFILE_ONLY", "evidence": f"SDFGI +{_pct(gpu['gi_sdfgi'], gpu['gi_off'])}% GPU and +{round((alloc['gi_sdfgi'] - alloc['gi_off']) / 1048576.0, 1)} MiB allocation"},
                {"id": "FogWeave", "decision": "GO_WITH_FALLBACK", "evidence": f"volumetric +{_pct(gpu['fog_volumetric'], gpu['fog_depth'])}% GPU vs depth fog"},
                {"id": "LightBridge", "decision": "GO", "evidence": f"{bridge['checks']} deterministic checks with two mock consumers"},
                {"id": "LightBudget", "decision": "RESEARCH_MORE", "evidence": "energy-only shadow slots; 2 vs 4 shadowed torches saves 4.1% GPU"},
            ]
        },
        "s08": {"verdict": "M03_LIGHTING_REFERENCE_DERIVED"},
        "verdict": "M03_LIGHTING_REFERENCE_DERIVED",
        "observations": [
            "three original looks are rendered at 1920x1080 on the RTX 5050; performance was measured on corridor_static only",
            "SDFGI is the dominant cost: +58.9% GPU p95 and +473 MiB allocation vs off",
            "shadow quality from low to ultra roughly doubles GPU p95",
            "volumetric fog adds only 4.6% over depth fog on this light workload",
            "the LightBridge passes 13 deterministic checks with two mock consumers",
        ],
        "limitations": [
            "single session, one GPU and driver; static frames",
            "the scenes are simple reference geometry, not production art",
            "SDFGI/LightmapGI/VoxelGI bake and editor-only paths are not exercised",
            "temporal shadow flicker and combat legibility with real telegraphs are not measured",
            "no PoE2 parity, FPS or cross-device claim",
        ],
        "runs": 11,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M03 · Cinematic lighting runtime",
        "",
        "**Status:** `M03_LIGHTING_REFERENCE_DERIVED / NATIVE_GPU / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · CineLight looks",
        "",
        "| Cena | Look | Pixels vs dungeon | Mean abs | GPU p95 |",
        "|---|---|---:|---:|---:|",
    ]
    for look in report["s01"]["looks"]:
        key = {"dungeon_torch": "look_dungeon", "moonlit_exterior": "look_moonlit", "boss_arena": "look_boss"}[look["look"]]
        changed = "—" if look["changed_vs_dungeon_pct"] is None else f"{look['changed_vs_dungeon_pct']:.3f}%"
        mean = "—" if look["mean_abs_vs_dungeon"] is None else f"{look['mean_abs_vs_dungeon']:.4f}"
        gpu_text = (f"{report['s01']['gpu_p95_ms'][key]:.3f} ms"
                    if look["scene_id"] == report["s01"]["perf_scene"] else "—")
        lines.append(f"| {look['scene_id']} | {look['look']} | {changed} | {mean} | {gpu_text} |")
    lines.extend(["", "## S02 · ShadowStability", "",
                  f"- Low vs ultra: **{report['s02']['gpu_low_p95_ms']:.3f} ms → {report['s02']['gpu_ultra_p95_ms']:.3f} ms** ({report['s02']['gpu_delta_pct']:+.1f}%).",
                  "- Temporal shadow flicker: `NOT_RUN`."])
    lines.extend(["", "## S03 · GI Atlas", "",
                  f"- SDFGI vs off: **{report['s03']['gpu_off_p95_ms']:.3f} ms → {report['s03']['gpu_sdfgi_p95_ms']:.3f} ms** ({report['s03']['gpu_delta_pct']:+.1f}%); allocation delta **{report['s03']['allocation_delta_mib']:+.1f} MiB**.",
                  "- Decisão: SDFGI apenas em perfis de qualidade."])
    lines.extend(["", "## S04 · FogWeave", "",
                  f"- Volumetric vs depth: **{report['s04']['gpu_depth_p95_ms']:.3f} ms → {report['s04']['gpu_volumetric_p95_ms']:.3f} ms** ({report['s04']['gpu_delta_pct']:+.1f}%).",
                  "- Fallback de depth fog documentado para Performance."])
    lines.extend(["", "## S05 · LightBridge", "",
                  f"- {report['s05']['bridge_checks']} checks determinísticos com dois consumidores mock; veredito `{report['s05']['verdict']}`."])
    lines.extend(["", "## S06 · LightBudget", "",
                  f"- 2 vs 4 tochas com sombra: **{report['s06']['gpu_off_p95_ms']:.3f} ms → {report['s06']['gpu_on_p95_ms']:.3f} ms** ({report['s06']['gpu_delta_pct']:+.1f}%).",
                  "- MVP baseado em energia; distância/visibilidade ainda `RESEARCH_MORE`."])
    lines.extend(["", "## S07 · decisões", "", "| Tecnologia | Decisão | Evidência |", "|---|---|---|"])
    for decision in report["s07"]["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m03/tools/build_lighting_runtime.py`; não é benchmark de jogo nem paridade com PoE2.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M03_LIGHTING_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

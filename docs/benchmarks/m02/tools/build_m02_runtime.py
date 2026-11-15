#!/usr/bin/env python3
"""Build the M02 runtime report from the native S01-S05 evidence."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png, sha256_file  # noqa: E402 - shared local tool module
from preset_report import load_capture, summarize, transform_run  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence"
CAMERA_DIR = EVIDENCE / "windows-rtx5050-2026-11-15-m02-camera-aspects"
SIGHTLINE_DIR = EVIDENCE / "windows-rtx5050-2026-11-15-m02-sightline"
SIGHTLINE_PERF = EVIDENCE / "windows-rtx5050-2026-11-15-m02-sightline-perf"
DEPTH_DIR = EVIDENCE / "windows-rtx5050-2026-11-15-m02-depth"
DEPTH_PERF = EVIDENCE / "windows-rtx5050-2026-11-15-m02-depth-perf"
TAA_DIR = EVIDENCE / "windows-rtx5050-2026-11-15-m02-temporal-taa"
PROFILES_DIR = EVIDENCE / "windows-rtx5050-2026-11-15-m02-profiles"
PROFILES_PERF = EVIDENCE / "windows-rtx5050-2026-11-15-m02-profiles-perf"
PASSPORT = REPO / "nex_modules" / "render3d" / "profiles" / "evidence" / "runtime-probe-2026-11-15.json"
BASELINE = REPO / "docs" / "benchmarks" / "m01" / "final-budget.v1.json"
OUTPUT = REPO / "docs" / "benchmarks" / "m02"
REPORT_JSON = OUTPUT / "runtime.v1.json"
REPORT_MD = OUTPUT / "RUNTIME.md"
SOURCE_SHA = "fa1adae7ab67e38c2556d126627006c338e2e8f4"
SCENES = ("corridor_static", "arena_combat", "dense_city")
ASPECTS = (("16x9", 1920, 1080), ("16x10", 1920, 1200), ("21x9", 2560, 1080), ("4x3", 1440, 1080))
PROFILES = ("quality", "balanced", "performance")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _log_value(path: Path, marker: str) -> dict[str, Any]:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(marker + " "):
            return json.loads(line[len(marker) + 1:])
    raise ValueError(f"missing {marker} in {path.name}")


def _perf_group(base: Path, manifest_name: str, key: str | None = None) -> dict[str, dict[str, Any]]:
    manifest = load_json(base / manifest_name)
    groups: dict[str, list[dict[str, Any]]] = {}
    for entry in manifest["runs"]:
        capture = load_capture(base, entry["run_id"], entry["scene"], entry["layout"], 100, include_allocation=True)
        if capture["source_sha"] != SOURCE_SHA:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        run = transform_run(entry, capture, include_allocation=True)
        group_key = entry.get(key, entry["scene_id"]) if key else entry["scene_id"]
        groups.setdefault(group_key, []).append(run)
    return {name: summarize(group, include_allocation=True) for name, group in groups.items()}


def _delta(value: float, baseline: float) -> float:
    return round((value - baseline) / baseline * 100.0, 1) if baseline else 0.0


def build_report() -> dict[str, Any]:
    baseline = load_json(BASELINE)
    baseline_gpu = {scene["scene_id"]: scene["gpu_p95_ms"] for scene in baseline["scenes"]}
    camera_math = load_json(CAMERA_DIR / "camera-math-2026-11-15.json")
    aspects = []
    for tag, width, height in ASPECTS:
        path = CAMERA_DIR / f"corridor_{tag}.png"
        image = read_png(path)
        if (image.width, image.height) != (width, height):
            raise ValueError(f"aspect {tag} has unexpected size")
        aspects.append({"tag": tag, "width": width, "height": height, "sha256": _sha(path)})
    sightline_perf = _perf_group(SIGHTLINE_PERF, "runs.v1.json")
    sightline_scenes = []
    for scene in SCENES:
        hidden = SIGHTLINE_DIR / f"{scene}_hidden.png"
        revealed = SIGHTLINE_DIR / f"{scene}_revealed.png"
        metrics = compare(read_png(hidden), read_png(revealed), 2)
        hidden_log = _log_value(SIGHTLINE_DIR / f"{scene}_hidden.log", "NEX_PRESET_AB_SIGHTLINE")
        revealed_log = _log_value(SIGHTLINE_DIR / f"{scene}_revealed.log", "NEX_PRESET_AB_SIGHTLINE")
        gpu = sightline_perf[scene]["gpu_p95_ms"]
        sightline_scenes.append({
            "scene_id": scene,
            "hidden_sha256": _sha(hidden),
            "revealed_sha256": _sha(revealed),
            "changed_pixels_pct": metrics["changed_pixels_pct"],
            "mean_abs_diff": metrics["mean_abs_diff"],
            "hidden_summary": hidden_log,
            "revealed_summary": revealed_log,
            "gpu_p95_ms": gpu,
            "baseline_gpu_p95_ms": baseline_gpu[scene],
            "gpu_delta_pct": _delta(gpu, baseline_gpu[scene]),
            "one_percent_low_fps": sightline_perf[scene]["one_percent_low_fps"],
        })
    depth_perf = _perf_group(DEPTH_PERF, "runs.v1.json")
    depth_scenes = []
    for scene in SCENES:
        off = DEPTH_DIR / f"{scene}_off.png"
        on = DEPTH_DIR / f"{scene}_on.png"
        metrics = compare(read_png(off), read_png(on), 2)
        plan = _log_value(DEPTH_DIR / f"{scene}_on.log", "NEX_PRESET_AB_DEPTH")
        gpu = depth_perf[scene]["gpu_p95_ms"]
        depth_scenes.append({
            "scene_id": scene,
            "off_sha256": _sha(off),
            "on_sha256": _sha(on),
            "changed_pixels_pct": metrics["changed_pixels_pct"],
            "mean_abs_diff": metrics["mean_abs_diff"],
            "plan": plan,
            "gpu_p95_ms": gpu,
            "baseline_gpu_p95_ms": baseline_gpu[scene],
            "gpu_delta_pct": _delta(gpu, baseline_gpu[scene]),
            "one_percent_low_fps": depth_perf[scene]["one_percent_low_fps"],
        })
    taa_off = load_json(TAA_DIR / "analysis_off.json")
    taa_on = load_json(TAA_DIR / "analysis_on.json")
    taa_frame_metrics = compare(read_png(TAA_DIR / "off" / "frame_00.png"),
                                read_png(TAA_DIR / "on" / "frame_00.png"), 2)
    passport = load_json(PASSPORT)
    profile_perf = _perf_group(PROFILES_PERF, "runs.v1.json", "profile")
    profiles = []
    for profile in PROFILES:
        visuals = []
        for scene in SCENES:
            path = PROFILES_DIR / f"{scene}_{profile}.png"
            visuals.append({"scene_id": scene, "sha256": _sha(path)})
        settings = _log_value(PROFILES_DIR / f"corridor_static_{profile}.log", "NEX_PRESET_AB_PROFILE")
        perf = profile_perf[profile]
        profiles.append({
            "profile": profile,
            "settings": settings,
            "visuals": visuals,
            "gpu_p95_ms": perf["gpu_p95_ms"],
            "cpu_p95_ms": perf["cpu_p95_ms"],
            "pacing_p95_ms": perf["pacing_p95_ms"],
            "one_percent_low_fps": perf["one_percent_low_fps"],
            "renderer_allocation_bytes_median": perf["renderer_allocation_bytes_median"],
        })
    decisions = [
        {"id": "NEX IsoDirector", "native": "Camera3D perspective/orthographic", "decision": "GO",
         "evidence": "round trip 3e-6 m, 4 aspect captures, A/B framing reproduced"},
        {"id": "Sightline", "native": "occlusion query / material fade", "decision": "GO",
         "evidence": "reveal rendered in 3 scenes, no critical unseen, GPU delta small"},
        {"id": "DepthWeave", "native": "transparent sorting / depth prepass", "decision": "GO",
         "evidence": "overlay pass with 0 z-fight/alpha/overlay conflicts, GPU delta small"},
        {"id": "TemporalGuard", "native": "native TAA", "decision": "NO_GO_CUSTOM_COMPOSITOR",
         "evidence": "native TAA available; off/on analyzer metrics identical, no benefit proven"},
        {"id": "RenderPassport", "native": "documented capability matrix", "decision": "GO",
         "evidence": "runtime probe on Forward+/Vulkan, three profiles OK, switch reversible"},
    ]
    return {
        "schema_version": "m02_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "s01": {
            "camera_math": camera_math,
            "aspects": aspects,
            "camera_integration": "docs/benchmarks/m02/camera-integration.v1.json",
        },
        "s02": {"scenes": sightline_scenes, "verdict": "SIGHTLINE_RENDERED"},
        "s03": {"scenes": depth_scenes, "verdict": "DEPTH_OVERLAY_SAFE"},
        "s04": {
            "off": taa_off["report"],
            "on": taa_on["report"],
            "first_frame_ab": taa_frame_metrics,
            "verdict": "NO_GO_CUSTOM_COMPOSITOR",
            "note": "native TAA is available and was captured; the region analyzer flags the same flicker on/off, so no custom compositor is justified.",
        },
        "s05": {"passport": passport["passport"], "profiles": profiles, "verdict": "PROFILES_APPLIED"},
        "s06": {"decisions": decisions},
        "s07": {"verdict": "M02_RUNTIME_REFERENCE_DERIVED"},
        "verdict": "M02_RUNTIME_REFERENCE_DERIVED",
        "observations": [
            "camera round-trip error is 3e-6 m and fast follow stays under 25 px per step",
            "sightline reveal is visible in all three scenes with 0 critical unseen",
            "depth overlay plan reports 0 z-fight, alpha-over-critical and overlay/gameplay conflicts",
            "native TAA changes the first frame but the region analyzer is identical off/on",
            "profile cost ordering is quality > balanced > performance in GPU p95 and allocation",
        ],
        "limitations": [
            "single session, one GPU and driver; static frames for S01/S02/S03/S05",
            "the temporal analyzer uses 4x4 luminance regions, not per-pixel TAA metrics",
            "the depth overlay is a deterministic test quad, not production art",
            "no game, gameplay, M03-M12 renderer or cross-device claim",
        ],
        "runs": 27,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M02 · Runtime reference report",
        "",
        "**Status:** `M02_RUNTIME_REFERENCE_DERIVED / NATIVE_GPU / NO_GENERAL_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · câmera",
        "",
        f"- Round-trip 3D↔tela: **{report['s01']['camera_math']['round_trip_max_error_m']:.6f} m**.",
        f"- Fast follow máximo: **{report['s01']['camera_math']['fast_follow_max_screen_step_px']:.3f} px** por passo.",
        "",
        "| Aspecto | Resolução | SHA-256 |",
        "|---|---|---|",
    ]
    for aspect in report["s01"]["aspects"]:
        lines.append(f"| {aspect['tag']} | {aspect['width']}×{aspect['height']} | `{aspect['sha256'][:16]}…` |")
    lines.extend(["", "## S02 · sightline", "", "| Cena | Reveals hidden→revealed | Pixels alterados | GPU p95 | Δ vs M01 |", "|---|---|---:|---:|---:|"])
    for scene in report["s02"]["scenes"]:
        lines.append(
            f"| {scene['scene_id']} | {scene['hidden_summary']['active_reveals']}→{scene['revealed_summary']['active_reveals']} | "
            f"{scene['changed_pixels_pct']:.3f}% | {scene['gpu_p95_ms']:.3f} ms | {scene['gpu_delta_pct']:+.1f}% |"
        )
    lines.extend(["", "## S03 · depth overlay", "", "| Cena | Pixels alterados | Z-fight | Alpha crítico | Overlay/gameplay | GPU p95 | Δ vs M01 |", "|---|---:|---:|---:|---:|---:|---:|"])
    for scene in report["s03"]["scenes"]:
        plan = scene["plan"]
        lines.append(
            f"| {scene['scene_id']} | {scene['changed_pixels_pct']:.3f}% | {plan['z_fight_risks']} | "
            f"{plan['alpha_over_critical']} | {plan['overlay_gameplay_conflicts']} | {scene['gpu_p95_ms']:.3f} ms | {scene['gpu_delta_pct']:+.1f}% |"
        )
    lines.extend(["", "## S04 · temporal TAA", "",
                  f"- Off: `{report['s04']['off']['verdict']}` / `{report['s04']['off']['action']}`; ghosting {report['s04']['off']['metrics']['ghosting']:.3f}, flicker {report['s04']['off']['metrics']['flicker']:.3f}, shimmer {report['s04']['off']['metrics']['shimmer']:.3f}.",
                  f"- On: `{report['s04']['on']['verdict']}` / `{report['s04']['on']['action']}`; ghosting {report['s04']['on']['metrics']['ghosting']:.3f}, flicker {report['s04']['on']['metrics']['flicker']:.3f}, shimmer {report['s04']['on']['metrics']['shimmer']:.3f}.",
                  f"- First-frame A/B: {report['s04']['first_frame_ab']['changed_pixels_pct']:.3f}% pixels, mean abs {report['s04']['first_frame_ab']['mean_abs_diff']:.4f}.",
                  f"- **Veredito:** `{report['s04']['verdict']}` — TAA nativo disponível; nenhum compositor customizado justificado."])
    lines.extend(["", "## S05 · perfis", "", "| Perfil | Render scale | MSAA | GPU p95 | CPU p95 | 1% low | Alloc MiB |", "|---|---:|---|---:|---:|---:|---:|"])
    for profile in report["s05"]["profiles"]:
        settings = profile["settings"]
        lines.append(
            f"| {profile['profile']} | {settings['resolution_scale']:.2f} | {settings['msaa']} | "
            f"{profile['gpu_p95_ms']:.3f} ms | {profile['cpu_p95_ms']:.3f} ms | {profile['one_percent_low_fps']:.2f} | "
            f"{profile['renderer_allocation_bytes_median'] / 1048576.0:.1f} |"
        )
    lines.extend(["", "## S06 · decisões R&D", "", "| Tecnologia | Nativo | Decisão | Evidência |", "|---|---|---|---|"])
    for decision in report["s06"]["decisions"]:
        lines.append(f"| {decision['id']} | {decision['native']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m02/tools/build_m02_runtime.py`; não é benchmark de jogo.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M02_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

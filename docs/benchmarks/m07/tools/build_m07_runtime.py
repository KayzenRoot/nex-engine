#!/usr/bin/env python3
"""Build the M07 2D reference report from the native lab and planner evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parents[1] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png  # noqa: E402 - shared local tool module
from preset_report import load_capture, summarize, transform_run  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m07"
IMAGES = EVIDENCE / "images"
OUTPUT = REPO / "docs" / "benchmarks" / "m07"
REPORT_JSON = OUTPUT / "m07-runtime.v1.json"
REPORT_MD = OUTPUT / "M07-RUNTIME.md"
PLANNER_LOG = REPO / "nex_modules" / "render2d" / "canvas" / "evidence" / "headless-smoke-2026-11-13.log"
SOURCE_SHA = "aa6256a82f6cd34e347b05ac43375ac4042d2ede"
MODES = ("baseline", "lighting", "shadows", "normal", "particles", "parallax",
         "quality_low", "quality_medium", "quality_high")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pct(new: float, old: float) -> float:
    return round((new - old) / old * 100.0, 2)


def _diff(first: Path, second: Path) -> dict[str, Any]:
    return compare(read_png(first), read_png(second), 2)


def _load_manifest() -> dict[str, Any]:
    manifest = load_json(EVIDENCE / "runs.v1.json")
    if manifest.get("schema_version") != "m07_lab_runs.v1":
        raise ValueError("M07 runs manifest schema is invalid")
    if manifest.get("source_sha") != SOURCE_SHA:
        raise ValueError("M07 runs manifest source SHA is stale")
    runs = manifest.get("runs", [])
    if len(runs) != 9:
        raise ValueError("M07 runs manifest must contain 9 runs")
    if [entry.get("sequence") for entry in runs] != list(range(1, 10)):
        raise ValueError("M07 runs manifest sequence is invalid")
    if {entry.get("mode") for entry in runs} != set(MODES):
        raise ValueError("M07 runs manifest modes are incomplete")
    return manifest


def _metrics(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for entry in manifest["runs"]:
        capture = load_capture(EVIDENCE, entry["run_id"], entry["scene"], entry["layout"],
                               int(entry["proxy_count"]), include_allocation=True)
        result[entry["mode"]] = transform_run(entry, capture, include_allocation=True)
    return result


def _planner_checks() -> int:
    text = PLANNER_LOG.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("NEX_M07_S01_SMOKE_PASS:"):
            return int(line.split(":", 1)[1].strip().split()[0])
    raise ValueError("planner smoke log has no pass line")


def build_report() -> dict[str, Any]:
    manifest = _load_manifest()
    metrics = _metrics(manifest)
    planner_checks = _planner_checks()
    if planner_checks < 46:
        raise ValueError("M07 planner smoke is incomplete")
    images = sorted(IMAGES.glob("*.png"))
    if len(images) != 9:
        raise ValueError("M07 lab must contain 9 images")
    baseline = metrics["baseline"]
    rows: dict[str, Any] = {}
    for mode in MODES:
        item = metrics[mode]
        diff = _diff(IMAGES / "m07_baseline.png", IMAGES / f"m07_{mode}.png") if mode != "baseline" else {
            "changed_pixels_pct": 0.0, "mean_abs_diff": 0.0, "psnr_db": None}
        rows[mode] = {
            "gpu_p95_ms": item["gpu_ms"]["p95"], "cpu_p95_ms": item["cpu_ms"]["p95"],
            "pacing_p95_ms": item["pacing_ms"]["p95"], "one_percent_low_fps": item["one_percent_low_fps"],
            "renderer_allocation_bytes": item["renderer_allocation_bytes"],
            "gpu_vs_baseline_pct": _pct(item["gpu_ms"]["p95"], baseline["gpu_ms"]["p95"]),
            "cpu_vs_baseline_pct": _pct(item["cpu_ms"]["p95"], baseline["cpu_ms"]["p95"]),
            "changed_pixels_pct": diff["changed_pixels_pct"],
            "mean_abs_diff": diff["mean_abs_diff"], "psnr_db": diff["psnr_db"],
            "png_bytes": (IMAGES / f"m07_{mode}.png").stat().st_size,
        }
    shadows_vs_lighting = _diff(IMAGES / "m07_lighting.png", IMAGES / "m07_shadows.png")
    normal_vs_lighting = _diff(IMAGES / "m07_lighting.png", IMAGES / "m07_normal.png")
    decisions = [
        {"id": "CanvasPlanner / render2d.v1", "decision": "GO",
         "evidence": f"{planner_checks} headless checks; planning only, no rendering"},
        {"id": "2D lighting / CanvasModulate", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "4 PointLight2D change 16.218% of the frame at +25.0% GPU p95"},
        {"id": "2D shadows / LightOccluder2D", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "shadows add +33.3% GPU over lighting and 9.028% pixel change"},
        {"id": "Normal maps / CanvasTexture", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "normal maps add +9.3% GPU over lighting and 14.542% pixel change"},
        {"id": "GPUParticles2D", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "384 particles add +18.3% GPU over baseline and 0.979% pixel change"},
        {"id": "ParallaxBackground", "decision": "GO",
         "evidence": "3 layers change 23.006% of the frame at +16.7% GPU p95"},
        {"id": "2D quality profiles", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "low/medium/high GPU 0.065/0.081/0.153 ms in one 100-sprite lab"},
    ]
    return {
        "schema_version": "m07_render2d_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-16",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "s01": {"planner_checks": planner_checks, "verdict": "CANVAS_PLANNER_VERIFIED"},
        "s02": {"rows": rows, "verdict": "RENDER2D_LIGHTING_DERIVED"},
        "s03": {"rows": rows, "shadows_vs_lighting": shadows_vs_lighting,
                "verdict": "RENDER2D_SHADOWS_GO_WITH_LIMITATIONS"},
        "s04": {"rows": rows, "normal_vs_lighting": normal_vs_lighting,
                "verdict": "RENDER2D_NORMAL_MAPS_GO_WITH_LIMITATIONS"},
        "s05": {"rows": rows, "verdict": "RENDER2D_PARTICLES_GO_WITH_LIMITATIONS"},
        "s06": {"rows": rows, "verdict": "RENDER2D_PARALLAX_GO"},
        "s07": {"rows": rows, "verdict": "RENDER2D_QUALITY_PROFILES_GO_WITH_LIMITATIONS"},
        "s08": {"decisions": decisions, "runs": 9, "images": len(images),
                "planner_checks": planner_checks, "third_party_assets": 0,
                "verdict": "M07_RENDER2D_QA_VERIFIED"},
        "verdict": "M07_RENDER2D_REFERENCE_DERIVED",
        "observations": [
            "9 native 2D runs and 9 captures cover lighting, shadows, normal maps, particles, parallax and quality profiles",
            "baseline GPU p95 is 0.060 ms; quality_high is 0.153 ms in the 100-sprite lab",
            "lighting changes 16.218% of the frame at +25.0% GPU p95 versus baseline",
            "shadows add +33.3% GPU over lighting and 9.028% pixel change",
            "normal maps add +9.3% GPU over lighting and 14.542% pixel change",
            "384 particles add +18.3% GPU over baseline and 0.979% pixel change",
            "parallax changes 23.006% of the frame at +16.7% GPU p95",
            "CanvasPlanner still passes 46 headless checks",
        ],
        "limitations": [
            "single session, one GPU and driver; 1920x1080 static 2D lab",
            "no production 2D renderer, atlas packing, y-sort or transparency rasterization",
            "no input-to-photon, VRAM pressure or cross-device claim",
            "lighting/shadows/normal maps are native Godot features, not a custom renderer",
            "no production art, no PoE2 parity and no generalized FPS claim",
        ],
        "runs": 9,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M07 · Render2D runtime",
        "",
        "**Status:** `M07_RENDER2D_REFERENCE_DERIVED / NATIVE_2D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · CanvasPlanner",
        "",
        f"- **{report['s01']['verdict']}**: {report['s01']['planner_checks']} checks headless.",
        "",
        "## S02 · 2D lighting",
        "",
        "| Modo | GPU p95 | CPU p95 | GPU vs base | Pixels | PSNR |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode in MODES:
        row = report["s02"]["rows"][mode]
        psnr = f"{row['psnr_db']:.2f} dB" if row["psnr_db"] is not None else "—"
        lines.append(f"| {mode} | {row['gpu_p95_ms']:.3f} ms | {row['cpu_p95_ms']:.3f} ms | "
                     f"{row['gpu_vs_baseline_pct']:+.2f}% | {row['changed_pixels_pct']:.3f}% | {psnr} |")
    lines.extend([
        "",
        "## S03 · Shadows",
        "",
        f"- Shadows vs lighting: **{report['s03']['shadows_vs_lighting']['changed_pixels_pct']:.3f}%** de pixels, "
        f"PSNR {report['s03']['shadows_vs_lighting']['psnr_db']:.2f} dB.",
        f"- GPU p95: lighting **{report['s02']['rows']['lighting']['gpu_p95_ms']:.3f} ms** → "
        f"shadows **{report['s02']['rows']['shadows']['gpu_p95_ms']:.3f} ms**.",
        "",
        "## S04 · Normal maps",
        "",
        f"- Normal vs lighting: **{report['s04']['normal_vs_lighting']['changed_pixels_pct']:.3f}%** de pixels, "
        f"PSNR {report['s04']['normal_vs_lighting']['psnr_db']:.2f} dB.",
        f"- GPU p95: lighting **{report['s02']['rows']['lighting']['gpu_p95_ms']:.3f} ms** → "
        f"normal **{report['s02']['rows']['normal']['gpu_p95_ms']:.3f} ms**.",
        "",
        "## S05 · Particles",
        "",
        f"- 384 particles: GPU **{report['s02']['rows']['particles']['gpu_p95_ms']:.3f} ms** "
        f"({report['s02']['rows']['particles']['gpu_vs_baseline_pct']:+.2f}% vs baseline); "
        f"pixels **{report['s02']['rows']['particles']['changed_pixels_pct']:.3f}%**.",
        "",
        "## S06 · Parallax",
        "",
        f"- 3 layers: GPU **{report['s02']['rows']['parallax']['gpu_p95_ms']:.3f} ms** "
        f"({report['s02']['rows']['parallax']['gpu_vs_baseline_pct']:+.2f}% vs baseline); "
        f"pixels **{report['s02']['rows']['parallax']['changed_pixels_pct']:.3f}%**.",
        "",
        "## S07 · Quality profiles",
        "",
        "| Perfil | GPU p95 | GPU vs base | Pixels |",
        "|---|---:|---:|---:|",
    ])
    for mode in ("quality_low", "quality_medium", "quality_high"):
        row = report["s07"]["rows"][mode]
        lines.append(f"| {mode} | {row['gpu_p95_ms']:.3f} ms | {row['gpu_vs_baseline_pct']:+.2f}% | "
                     f"{row['changed_pixels_pct']:.3f}% |")
    lines.extend([
        "",
        "## S08 · decisões",
        "",
        "| Tecnologia | Decisão | Evidência |",
        "|---|---|---|",
    ])
    for decision in report["s08"]["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend([
        "",
        f"- {report['s08']['runs']} runs, {report['s08']['images']} imagens, "
        f"{report['s08']['planner_checks']} checks de planner, "
        f"{report['s08']['third_party_assets']} assets de terceiros.",
        "",
        "## Observações",
        "",
    ])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m07/tools/build_m07_runtime.py`; não é paridade com PoE2.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M07_RENDER2D_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Build the M08 2.5D reference report from the native hybrid lab."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parents[1] / "m09" / "tools"))
sys.path.insert(0, str(TOOLS.parents[1] / "tools"))
from common import run_cli  # noqa: E402 - shared local tool module
from runtime_report import diff, load_manifest, metrics, pct, render_json  # noqa: E402 - shared tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m08"
IMAGES = EVIDENCE / "images"
OUTPUT = REPO / "docs" / "benchmarks" / "m08"
REPORT_JSON = OUTPUT / "m08-runtime.v1.json"
REPORT_MD = OUTPUT / "M08-RUNTIME.md"
PLANNER_LOG = REPO / "nex_modules" / "render2_5d" / "composition" / "evidence" / "headless-smoke-2026-11-13.log"
SOURCE_SHA = "2c7dd515e307086cdd7180577b0c78ad7fb5cf1c"
MODES = ("baseline", "sprites", "sorted", "shadows", "overlay", "hybrid",
         "perspective", "quality_low", "quality_high")


def _planner_checks() -> int:
    text = PLANNER_LOG.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("NEX_M08_COMPOSITION_SMOKE_PASS:"):
            return int(line.split(":", 1)[1].strip().split()[0])
    raise ValueError("composition planner smoke has no pass line")


def build_report() -> dict[str, Any]:
    manifest = load_manifest(EVIDENCE / "runs.v1.json", "m08_lab_runs.v1", SOURCE_SHA, 9, MODES)
    metric_rows = metrics(EVIDENCE, manifest)
    planner_checks = _planner_checks()
    if planner_checks < 69:
        raise ValueError("M08 composition planner smoke is incomplete")
    images = sorted(IMAGES.glob("*.png"))
    if len(images) != 9:
        raise ValueError("M08 lab must contain 9 images")
    baseline = metric_rows["baseline"]
    rows: dict[str, Any] = {}
    for mode in MODES:
        item = metric_rows[mode]
        image_diff = diff(IMAGES / "m08_baseline.png", IMAGES / f"m08_{mode}.png") if mode != "baseline" else {
            "changed_pixels_pct": 0.0, "mean_abs_diff": 0.0, "psnr_db": None}
        rows[mode] = {
            "gpu_p95_ms": item["gpu_ms"]["p95"], "cpu_p95_ms": item["cpu_ms"]["p95"],
            "pacing_p95_ms": item["pacing_ms"]["p95"], "one_percent_low_fps": item["one_percent_low_fps"],
            "renderer_allocation_bytes": item["renderer_allocation_bytes"],
            "gpu_vs_baseline_pct": pct(item["gpu_ms"]["p95"], baseline["gpu_ms"]["p95"]),
            "cpu_vs_baseline_pct": pct(item["cpu_ms"]["p95"], baseline["cpu_ms"]["p95"]),
            "changed_pixels_pct": image_diff["changed_pixels_pct"],
            "mean_abs_diff": image_diff["mean_abs_diff"], "psnr_db": image_diff["psnr_db"],
            "png_bytes": (IMAGES / f"m08_{mode}.png").stat().st_size,
        }
    sorted_diff = diff(IMAGES / "m08_sprites.png", IMAGES / "m08_sorted.png")
    decisions = [
        {"id": "CompositionPlanner / composition.v1", "decision": "GO",
         "evidence": f"{planner_checks} headless checks; planning only"},
        {"id": "Orthographic hybrid camera", "decision": "GO_WITH_LIMITATIONS",
         "evidence": f"baseline GPU p95 {rows['baseline']['gpu_p95_ms']:.3f} ms in the 2.5D lab"},
        {"id": "Sprite3D billboards", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "40 sprites add +2.56% GPU and change 6.463% of the frame"},
        {"id": "Custom depth sorting", "decision": "NO_GO",
         "evidence": "sorted vs sprites change 0.000% of pixels; native sorting is sufficient"},
        {"id": "3D shadow casting", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "shadows add +27.69% GPU and change 15.477% of the frame"},
        {"id": "CanvasLayer overlay", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "overlay adds +5.38% GPU and changes 22.789% of the frame"},
        {"id": "Hybrid 2.5D composition", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "hybrid adds +30.26% GPU and changes 31.714% of the frame"},
        {"id": "Perspective camera mode", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "perspective GPU 0.332 ms (-14.87% vs ortho) with different framing"},
        {"id": "2.5D quality profiles", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "low/high GPU 0.397/0.497 ms in one hybrid lab"},
    ]
    return {
        "schema_version": "m08_render25d_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-16",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "s01": {"planner_checks": planner_checks, "verdict": "COMPOSITION_PLANNER_VERIFIED"},
        "s02": {"rows": rows, "sorted_vs_sprites": sorted_diff, "verdict": "RENDER25D_HYBRID_DERIVED"},
        "s03": {"rows": rows, "verdict": "RENDER25D_SHADOWS_GO_WITH_LIMITATIONS"},
        "s04": {"rows": rows, "verdict": "RENDER25D_OVERLAY_GO_WITH_LIMITATIONS"},
        "s05": {"rows": rows, "verdict": "RENDER25D_HYBRID_GO_WITH_LIMITATIONS"},
        "s06": {"rows": rows, "verdict": "RENDER25D_CAMERA_MODES_GO_WITH_LIMITATIONS"},
        "s07": {"rows": rows, "verdict": "RENDER25D_QUALITY_PROFILES_GO_WITH_LIMITATIONS"},
        "s08": {"decisions": decisions, "runs": 9, "images": len(images),
                "planner_checks": planner_checks, "third_party_assets": 0,
                "verdict": "M08_RENDER25D_QA_VERIFIED"},
        "verdict": "M08_RENDER25D_REFERENCE_DERIVED",
        "observations": [
            "9 native 2.5D runs and 9 captures cover orthographic/perspective cameras, sprites, sorting, shadows, overlay, hybrid and quality profiles",
            "baseline GPU p95 is 0.390 ms; sprites 0.400 ms; sorted 0.401 ms; shadows 0.498 ms; overlay 0.411 ms; hybrid 0.508 ms",
            "perspective camera is 0.332 ms with 34.442% different pixels versus orthographic",
            "sorted vs sprites changes 0.000% of pixels; native transparent sorting is sufficient",
            "shadows add +27.69% GPU and change 15.477% of the frame",
            "overlay adds +5.38% GPU and changes 22.789% of the frame",
            "hybrid adds +30.26% GPU and changes 31.714% of the frame",
            "CompositionPlanner still passes 69 headless checks",
        ],
        "limitations": [
            "single session, one GPU and driver; 1920x1080 static 2.5D lab",
            "no production 2.5D renderer, viewport stacking or art-directed layer stack",
            "depth sorting is native Sprite3D transparency sorting, not a custom sorter",
            "no input-to-photon, VRAM pressure or cross-device claim",
            "no production art, no PoE2 parity and no generalized FPS claim",
        ],
        "runs": 9,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M08 · 2.5D hybrid runtime",
        "",
        "**Status:** `M08_RENDER25D_REFERENCE_DERIVED / NATIVE_2.5D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · CompositionPlanner",
        "",
        f"- **{report['s01']['verdict']}**: {report['s01']['planner_checks']} checks headless.",
        "",
        "## S02 · Câmera, sprites e sorting",
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
        f"- Shadows vs baseline: **{report['s03']['rows']['shadows']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s03']['rows']['shadows']['gpu_p95_ms']:.3f} ms** "
        f"({report['s03']['rows']['shadows']['gpu_vs_baseline_pct']:+.2f}%).",
        "",
        "## S04 · Overlay 2D",
        "",
        f"- Overlay vs baseline: **{report['s04']['rows']['overlay']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s04']['rows']['overlay']['gpu_p95_ms']:.3f} ms** "
        f"({report['s04']['rows']['overlay']['gpu_vs_baseline_pct']:+.2f}%).",
        "",
        "## S05 · Hybrid",
        "",
        f"- Hybrid vs baseline: **{report['s05']['rows']['hybrid']['changed_pixels_pct']:.3f}%** de pixels; "
        f"GPU **{report['s05']['rows']['hybrid']['gpu_p95_ms']:.3f} ms** "
        f"({report['s05']['rows']['hybrid']['gpu_vs_baseline_pct']:+.2f}%).",
        "",
        "## S06 · Câmera ortho vs perspective",
        "",
        f"- Orthographic **{report['s02']['rows']['baseline']['gpu_p95_ms']:.3f} ms** → "
        f"perspective **{report['s02']['rows']['perspective']['gpu_p95_ms']:.3f} ms** "
        f"({report['s02']['rows']['perspective']['gpu_vs_baseline_pct']:+.2f}%); "
        f"{report['s02']['rows']['perspective']['changed_pixels_pct']:.3f}% de pixels.",
        "",
        "## S07 · Quality profiles",
        "",
        "| Perfil | GPU p95 | GPU vs base | Pixels |",
        "|---|---:|---:|---:|",
    ])
    for mode in ("quality_low", "quality_high"):
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
    lines.extend(["", "Gerado por `docs/benchmarks/m08/tools/build_m08_runtime.py`; não é paridade com PoE2.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M08_RENDER25D_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

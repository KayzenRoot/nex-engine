#!/usr/bin/env python3
"""Build the approved M01 1080p performance budget from the 9 native runs."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from preset_report import load_capture, summarize, transform_run  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-perf-1080")
EVIDENCE = REPO / EVIDENCE_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m01"
REPORT_JSON = OUTPUT / "final-budget.v1.json"
REPORT_MD = OUTPUT / "FINAL-BUDGET.md"
SOURCE_SHA = "900d2b2d031a87048702625a1e98bc50905bc663"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A", "M01 corridor_static + deterministic fillers"),
    ("arena_combat", "M01 Arena A/B/A", "M01 arena_combat + deterministic fillers"),
    ("dense_city", "M01 City A/B/A", "M01 dense_city + deterministic fillers"),
)
PROXY_COUNT = 100
RUNS = 9
BUDGET = {
    "gpu_p95_ms": 1.0,
    "cpu_p95_ms": 2.0,
    "pacing_p95_ms": 16.67,
    "one_percent_low_fps": 60.0,
    "experimental_120_pacing_p95_ms": 8.33,
    "experimental_120_one_percent_low_fps": 120.0,
}


def build_report() -> dict[str, Any]:
    manifest = load_json(EVIDENCE / "runs.v1.json")
    if manifest.get("schema_version") != "m01_performance_runs.v1":
        raise ValueError("performance manifest schema is invalid")
    entries = manifest.get("runs")
    if not isinstance(entries, list) or len(entries) != RUNS:
        raise ValueError("performance manifest must contain 9 runs")
    if manifest.get("source_sha") != SOURCE_SHA:
        raise ValueError("performance manifest source SHA mismatch")
    runs = []
    for entry in entries:
        capture = load_capture(EVIDENCE, entry["run_id"], entry["scene"], entry["layout"],
                               PROXY_COUNT, include_allocation=True)
        if capture["source_sha"] != SOURCE_SHA:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        run = transform_run(entry, capture, include_allocation=True)
        run["scene_id"] = entry["scene_id"]
        run["scene"] = entry["scene"]
        run["layout"] = entry["layout"]
        run["seed"] = entry["seed"]
        runs.append(run)
    scenes = []
    for scene_id, scene, layout in SCENES:
        group = [run for run in runs if run["scene_id"] == scene_id]
        if len(group) != 3:
            raise ValueError(f"expected 3 runs for {scene_id}")
        summary = summarize(group, include_allocation=True)
        summary.update({
            "scene_id": scene_id,
            "scene": scene,
            "layout": layout,
            "seed": group[0]["seed"],
            "viewport_px": [1920, 1080],
            "runs": 3,
            "budget": {
                "gpu_p95_ms": BUDGET["gpu_p95_ms"],
                "cpu_p95_ms": BUDGET["cpu_p95_ms"],
                "pacing_p95_ms": BUDGET["pacing_p95_ms"],
                "one_percent_low_fps": BUDGET["one_percent_low_fps"],
            },
            "checks": {
                "gpu_p95": summary["gpu_p95_ms"] <= BUDGET["gpu_p95_ms"],
                "cpu_p95": summary["cpu_p95_ms"] <= BUDGET["cpu_p95_ms"],
                "pacing_p95": summary["pacing_p95_ms"] <= BUDGET["pacing_p95_ms"],
                "one_percent_low": summary["one_percent_low_fps"] >= BUDGET["one_percent_low_fps"],
            },
        })
        scenes.append(summary)
    return {
        "schema_version": "m01_final_performance_budget.v1",
        "source_sha": SOURCE_SHA,
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1920, 1080],
        "settings": {"max_fps": 240, "vsync": 0, "warmup_seconds": 2.0, "observation_seconds": 30.0},
        "workload": {"proxy_count": PROXY_COUNT, "effect_mode": "lights", "preset_id": "ab-low"},
        "budget": BUDGET,
        "scenes": scenes,
        "targets": [
            {"id": "quality-1080p60", "frame_budget_ms": 16.67, "status": "MET_ON_REFERENCE_WORKLOAD"},
            {"id": "performance-120", "frame_budget_ms": 8.33, "status": "MET_ON_REFERENCE_WORKLOAD"},
        ],
        "ownerDecision": {
            "status": "OWNER_APPROVED",
            "date": "2026-11-15",
            "record": "Owner authorized finalizing the base modules starting with M01 and explicitly approved closing the M01 budget decision.",
            "audit": "ADMIN_SOLO_NOT_INDEPENDENT",
        },
        "verdict": "M01_BUDGET_APPROVED_AND_MEASURED",
        "observations": [
            "all 9 runs are 1920x1080 native Forward+/Vulkan on the RTX 5050",
            "GPU p95 medians are 0.121-0.151 ms and CPU p95 medians are 0.361-0.476 ms",
            "pacing p95 medians are 4.246-4.296 ms and 1% low medians are 223.26-225.98 FPS",
            "the 60 FPS and experimental 120 FPS pacing budgets are met on this light workload",
            "the 240 FPS cap and VSync-off settings mean this is not a display-presentation claim",
        ],
        "limitations": [
            "single session, one GPU and driver",
            "100-mesh light workload; no dense-game or cross-device generalization",
            "callback pacing is not input-to-photon or display presentation",
            "allocation is renderer-side and session-history, not device VRAM",
        ],
        "runs": RUNS,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M01 · Orçamento de performance 1080p (aprovado)",
        "",
        "**Status:** `OWNER_APPROVED / MEASURED_ON_REFERENCE_LAB / NO_GENERAL_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · VSync {report['settings']['vsync']} · max_fps {report['settings']['max_fps']}",
        "",
        "| Cena | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | Alloc MiB | Checks |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for scene in report["scenes"]:
        checks = "PASS" if all(scene["checks"].values()) else "FAIL"
        lines.append(
            f"| {scene['scene_id']} | {scene['gpu_p50_ms']:.3f} | {scene['gpu_p95_ms']:.3f} | "
            f"{scene['gpu_p99_ms']:.3f} | {scene['cpu_p95_ms']:.3f} | {scene['pacing_p95_ms']:.3f} | "
            f"{scene['one_percent_low_fps']:.2f} | {scene['renderer_allocation_bytes_median'] / 1048576.0:.1f} | {checks} |"
        )
    lines.extend([
        "",
        "## Orçamento aprovado",
        "",
        "| Métrica | Teto |",
        "|---|---:|",
        f"| GPU p95 | {report['budget']['gpu_p95_ms']:.2f} ms |",
        f"| CPU p95 | {report['budget']['cpu_p95_ms']:.2f} ms |",
        f"| Pacing p95 (60 FPS) | {report['budget']['pacing_p95_ms']:.2f} ms |",
        f"| 1% low (60 FPS) | {report['budget']['one_percent_low_fps']:.0f} FPS |",
        f"| Pacing p95 (120 FPS experimental) | {report['budget']['experimental_120_pacing_p95_ms']:.2f} ms |",
        f"| 1% low (120 FPS experimental) | {report['budget']['experimental_120_one_percent_low_fps']:.0f} FPS |",
        "",
        "## Observações", "",
    ])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend([
        "",
        f"**Decisão do Owner:** `{report['ownerDecision']['status']}` em {report['ownerDecision']['date']} — {report['ownerDecision']['record']}",
        "",
        "Gerado por `docs/benchmarks/m01/tools/build_performance_budget.py`; não é benchmark de jogo ou de hardware arbitrário.",
        "",
    ])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M01_FINAL_BUDGET")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

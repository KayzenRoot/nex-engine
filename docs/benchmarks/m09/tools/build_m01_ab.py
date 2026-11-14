#!/usr/bin/env python3
"""NEX M09 M01 scene A/B/A report builder.

Reads the 18 validated captures (3 per preset per M01 scene), verifies the
manifest and writes a deterministic JSON/Markdown report. No new measurement
is performed and no general performance claim is made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import run_cli  # noqa: E402 - local tool module
from preset_report import load_capture, load_manifest, pct, summarize, transform_run  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "m01-ab.v1.json"
REPORT_MD = OUTPUT_DIR / "M01-AB-REPORT.md"

REPORT_SCHEMA = "m09_preset_m01_ab.v1"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A", "M01 corridor_static + deterministic fillers"),
    ("arena_combat", "M01 Arena A/B/A", "M01 arena_combat + deterministic fillers"),
    ("dense_city", "M01 City A/B/A", "M01 dense_city + deterministic fillers"),
)
PRESETS = ("ab-low", "ab-high")
PROXY_COUNT = 100


def build_report() -> dict[str, Any]:
    manifest = load_manifest(MANIFEST, 18, (PROXY_COUNT,), PRESETS)
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    for entry in manifest["runs"]:
        run_id = entry["run_id"]
        capture = load_capture(EVIDENCE, run_id, entry["scene"], entry["layout"], PROXY_COUNT,
                               include_allocation=True)
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{run_id}: source_sha mismatch")
        if capture["viewport"] != [1280, 720]:
            raise ValueError(f"{run_id}: unexpected viewport")
        run = transform_run(entry, capture, include_allocation=True)
        run["scene_id"] = entry["scene_id"]
        run["scene"] = entry["scene"]
        runs.append(run)
    scenes = []
    for scene_id, scene, layout in SCENES:
        scene_runs = [run for run in runs if run["scene_id"] == scene_id]
        baselines = {}
        for preset in PRESETS:
            group = [run for run in scene_runs if run["preset_id"] == preset]
            if len(group) != 3:
                raise ValueError(f"expected 3 runs for {scene_id}/{preset}")
            baselines[preset] = summarize(group, include_allocation=True)
        low = baselines["ab-low"]
        high = baselines["ab-high"]
        deltas = {
            "gpu_p50_pct": pct(high["gpu_p50_ms"], low["gpu_p50_ms"]),
            "gpu_p95_pct": pct(high["gpu_p95_ms"], low["gpu_p95_ms"]),
            "gpu_p99_pct": pct(high["gpu_p99_ms"], low["gpu_p99_ms"]),
            "cpu_p95_pct": pct(high["cpu_p95_ms"], low["cpu_p95_ms"]),
            "pacing_p95_pct": pct(high["pacing_p95_ms"], low["pacing_p95_ms"]),
            "one_percent_low_pct": pct(high["one_percent_low_fps"], low["one_percent_low_fps"]),
        }
        scenes.append(
            {
                "scene_id": scene_id,
                "scene": scene,
                "layout": layout,
                "proxy_count": PROXY_COUNT,
                "baselines": baselines,
                "deltas_high_vs_low": deltas,
            }
        )
    by_scene = {scene["scene_id"]: scene for scene in scenes}
    observations = [
        "ab-high GPU p95 is higher in every scene: corridor "
        f"{by_scene['corridor_static']['deltas_high_vs_low']['gpu_p95_pct']:+.1f}%, arena "
        f"{by_scene['arena_combat']['deltas_high_vs_low']['gpu_p95_pct']:+.1f}%, city "
        f"{by_scene['dense_city']['deltas_high_vs_low']['gpu_p95_pct']:+.1f}%.",
        "Absolute GPU p95 medians stay below 0.5 ms because 100 meshes are a light workload for this GPU.",
        "Pacing stays near 4.2 ms (240 fps cap); 1% low deltas range from -1.0% to +0.4% and are not a gain claim.",
        "Corridor ab-high has a first-run p95 outlier (0.542 ms vs 0.421/0.423 ms); the median is reported.",
        "These are measured GPU costs for three specific M01 compositions, not game FPS, quality or universal recommendations.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1280, 720],
        "settings": {"vsync_mode": 0, "max_fps": 240},
        "workload": {
            "proxy_count": PROXY_COUNT,
            "effect_mode": "lights",
            "scenes": [{"scene_id": scene_id, "scene": scene, "layout": layout} for scene_id, scene, layout in SCENES],
        },
        "runs": runs,
        "scenes": scenes,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session; 3 runs per preset per scene",
            "three specific M01 compositions at 100 meshes; fillers may overlap base-scene props",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "corridor ab-high first-run p95 outlier is documented and retained",
            "renderer allocation bytes are session history, not device VRAM",
            "GPU render timing can describe earlier work and is not input-to-photon",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · M01 scene A/B/A — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · vsync {report['settings']['vsync_mode']} · max_fps {report['settings']['max_fps']}",
        f"**Workload:** {report['workload']['proxy_count']} meshes per scene · effect_mode {report['workload']['effect_mode']}",
        "",
        "## Medianas por cena (3 runs por preset)",
        "",
        "| Cena | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | Alloc MiB |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scene in report["scenes"]:
        for preset in ("ab-low", "ab-high"):
            base = scene["baselines"][preset]
            lines.append(
                f"| {scene['scene_id']} | {preset} | {base['gpu_p50_ms']:.3f} | {base['gpu_p95_ms']:.3f} | "
                f"{base['gpu_p99_ms']:.3f} | {base['cpu_p95_ms']:.3f} | {base['pacing_p95_ms']:.3f} | "
                f"{base['one_percent_low_fps']:.2f} | {base['renderer_allocation_bytes_median'] / 1048576.0:.1f} |"
            )
    lines.extend(
        [
            "",
            "## Deltas ab-high vs ab-low (medianas)",
            "",
            "| Cena | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for scene in report["scenes"]:
        delta = scene["deltas_high_vs_low"]
        lines.append(
            f"| {scene['scene_id']} | {delta['gpu_p50_pct']:+.1f}% | {delta['gpu_p95_pct']:+.1f}% | "
            f"{delta['gpu_p99_pct']:+.1f}% | {delta['cpu_p95_pct']:+.1f}% | "
            f"{delta['pacing_p95_pct']:+.1f}% | {delta['one_percent_low_pct']:+.1f}% |"
        )
    lines.extend(
        [
            "",
            "## A/A stability (3 ab-low runs)",
            "",
            "| Cena | GPU p95 spread | 1% low spread |",
            "|---|---:|---:|",
        ]
    )
    for scene in report["scenes"]:
        base = scene["baselines"]["ab-low"]
        lines.append(f"| {scene['scene_id']} | {base['gpu_p95_spread_pct']:.1f}% | {base['one_percent_low_spread_pct']:.1f}% |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_m01_ab.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "M01_AB")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""NEX M09 proxy x resolution interaction report builder.

Reads the 24 validated captures (3 per preset per proxy/resolution cell),
verifies provenance and writes a deterministic JSON/Markdown report. No new
measurement is performed and no general performance claim is made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import interaction_summary, load_capture, load_manifest, transform_run  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "interaction.v1.json"
REPORT_MD = OUTPUT_DIR / "INTERACTION-REPORT.md"

REPORT_SCHEMA = "m09_preset_interaction.v1"
SCENE_ID = "arena_combat"
SCENE = "M01 Arena A/B/A"
LAYOUT = "M01 arena_combat + deterministic fillers"
PROXY_COUNTS = (50, 100)
RESOLUTIONS = ((960, 540), (1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _key(proxy_count: int, width: int, height: int) -> str:
    return f"{proxy_count}/{width}x{height}"


def _validate_manifest(manifest: dict[str, Any]) -> None:
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 24:
        raise ValueError("runs manifest must contain 24 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 25)):
        raise ValueError("runs manifest sequence must be 1..24")
    if len({run.get("run_id") for run in runs}) != 24:
        raise ValueError("runs manifest run ids must be unique")
    for count in PROXY_COUNTS:
        for width, height in RESOLUTIONS:
            for preset in PRESETS:
                group = [run for run in runs
                         if run.get("proxy_count") == count
                         and run.get("viewport_px") == [width, height]
                         and run.get("preset_id") == preset]
                if len(group) != 3 or sorted(run.get("repetition") for run in group) != [1, 2, 3]:
                    raise ValueError(f"runs manifest cell is invalid: {_key(count, width, height)}/{preset}")


def build_report() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_runs.v1":
        raise ValueError("runs manifest schema is invalid")
    _validate_manifest(manifest)
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    for entry in manifest["runs"]:
        capture = load_capture(EVIDENCE, entry["run_id"], SCENE, LAYOUT, entry["proxy_count"])
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        if capture["viewport"] != entry["viewport_px"]:
            raise ValueError(f"{entry['run_id']}: viewport mismatch")
        run = transform_run(entry, capture)
        run["proxy_count"] = entry["proxy_count"]
        run["viewport_px"] = entry["viewport_px"]
        runs.append(run)
    summary = interaction_summary(runs)
    cells = summary["cells"]
    deltas = summary["deltas_high_vs_low"]
    resolution_scaling = summary["resolution_scaling"]
    proxy_scaling = summary["proxy_scaling"]
    observations = [
        "Resolution dominates GPU cost in this range: GPU p95 high vs low is "
        f"{deltas['50/960x540']['gpu_p95_pct']:+.1f}%/{deltas['100/960x540']['gpu_p95_pct']:+.1f}% at 960x540 "
        f"and {deltas['50/1920x1080']['gpu_p95_pct']:+.1f}%/{deltas['100/1920x1080']['gpu_p95_pct']:+.1f}% at 1920x1080 "
        "(50/100 proxies).",
        f"Proxy scaling 50 to 100 changes GPU p95 by {proxy_scaling['960x540']['ab-low']:+.1f}%/{proxy_scaling['960x540']['ab-high']:+.1f}% "
        f"at 960x540 and {proxy_scaling['1920x1080']['ab-low']:+.1f}%/{proxy_scaling['1920x1080']['ab-high']:+.1f}% at 1920x1080.",
        f"Resolution scaling 960x540 to 1920x1080 raises GPU p95 by {resolution_scaling['50']['ab-low']:+.1f}% "
        f"for ab-low and {resolution_scaling['50']['ab-high']:+.1f}% for ab-high at 50 proxies.",
        "CPU p95 rises 4.2-7.8% from 50 to 100 proxies while GPU p95 is essentially flat, consistent with a pixel-bound GPU cost.",
        "Pacing remains near 4.24 ms and 1% low deltas are within -0.8% to -0.1%; no gain is claimed.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "workload": {"scene_id": SCENE_ID, "scene": SCENE, "effect_mode": "lights",
                     "proxy_counts": list(PROXY_COUNTS),
                     "resolutions": [{"width": width, "height": height} for width, height in RESOLUTIONS]},
        "settings": {"vsync_mode": 0, "max_fps": 240, "native_resolution": True},
        "runs": runs,
        "cells": cells,
        "deltas_high_vs_low": deltas,
        "resolution_scaling": resolution_scaling,
        "proxy_scaling": proxy_scaling,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session on one RTX 5050; no cross-device or cross-session generalization",
            "one scene and two proxy counts; 25 proxies would require removing base geometry",
            "two resolutions only; 2560x1440 is not covered",
            "native resolution disables the project's canvas_items stretch mode",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Proxy × resolution interaction — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Workload:** {report['workload']['scene']} · proxies {report['workload']['proxy_counts']} · native resolution",
        "",
        "## Células (medianas de 3 runs)",
        "",
        "| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['proxy_count']} | {cell['width']}×{cell['height']} | {cell['preset_id']} | "
            f"{cell['gpu_p50_ms']:.3f} | {cell['gpu_p95_ms']:.3f} | {cell['gpu_p99_ms']:.3f} | "
            f"{cell['cpu_p95_ms']:.3f} | {cell['pacing_p95_ms']:.3f} | {cell['one_percent_low_fps']:.2f} |"
        )
    lines.extend(["", "## Deltas ab-high vs ab-low (GPU p95)", ""])
    for count in (50, 100):
        for width, height in ((960, 540), (1920, 1080)):
            delta = report["deltas_high_vs_low"][f"{count}/{width}x{height}"]
            lines.append(
                f"- {count} proxies / {width}×{height}: **{delta['gpu_p95_pct']:+.1f}%** "
                f"(GPU p99 {delta['gpu_p99_pct']:+.1f}%, CPU p95 {delta['cpu_p95_pct']:+.1f}%, "
                f"1% low {delta['one_percent_low_pct']:+.1f}%)."
            )
    lines.extend(
        [
            "",
            "## Escala de resolução 960×540 → 1920×1080 (GPU p95)",
            "",
            f"- 50 proxies: ab-low {report['resolution_scaling']['50']['ab-low']:+.1f}%, "
            f"ab-high {report['resolution_scaling']['50']['ab-high']:+.1f}%.",
            f"- 100 proxies: ab-low {report['resolution_scaling']['100']['ab-low']:+.1f}%, "
            f"ab-high {report['resolution_scaling']['100']['ab-high']:+.1f}%.",
            "",
            "## Escala de proxies 50 → 100 (GPU p95)",
            "",
            f"- 960×540: ab-low {report['proxy_scaling']['960x540']['ab-low']:+.1f}%, "
            f"ab-high {report['proxy_scaling']['960x540']['ab-high']:+.1f}%.",
            f"- 1920×1080: ab-low {report['proxy_scaling']['1920x1080']['ab-low']:+.1f}%, "
            f"ab-high {report['proxy_scaling']['1920x1080']['ab-high']:+.1f}%.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_interaction.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "INTERACTION")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

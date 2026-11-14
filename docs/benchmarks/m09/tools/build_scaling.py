#!/usr/bin/env python3
"""NEX M09 preset scaling report builder.

Reads the 18 validated captures (3 per preset per proxy count), verifies the
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
from preset_report import load_capture, load_manifest, median, pct, summarize, transform_run  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "scaling.v1.json"
REPORT_MD = OUTPUT_DIR / "SCALING-REPORT.md"

REPORT_SCHEMA = "m09_preset_scaling.v1"
COUNTS = (25, 100, 200)
PRESETS = ("ab-low", "ab-high")


def build_report() -> dict[str, Any]:
    manifest = load_manifest(MANIFEST, 18, COUNTS, PRESETS)
    source_sha = manifest.get("source_sha")
    runs = []
    for entry in manifest["runs"]:
        capture = load_capture(EVIDENCE, entry["run_id"], "Preset A/B/A", "built-in deterministic grid",
                               entry["proxy_count"])
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        run = transform_run(entry, capture)
        run["proxy_count"] = entry["proxy_count"]
        runs.append(run)
    cells = []
    for count in COUNTS:
        for preset in PRESETS:
            group = [run for run in runs if run["proxy_count"] == count and run["preset_id"] == preset]
            if len(group) != 3:
                raise ValueError(f"expected 3 runs for {count}/{preset}")
            summary = summarize(group)
            cells.append(
                {
                    "proxy_count": count,
                    "preset_id": preset,
                    "runs": summary["runs"],
                    "gpu_p95_median_ms": summary["gpu_p95_ms"],
                    "cpu_p95_median_ms": summary["cpu_p95_ms"],
                    "pacing_p95_median_ms": summary["pacing_p95_ms"],
                    "one_percent_low_median_fps": summary["one_percent_low_fps"],
                    "gpu_p95_spread_pct": summary["gpu_p95_spread_pct"],
                    "one_percent_low_spread_pct": summary["one_percent_low_spread_pct"],
                }
            )
    by_cell = {(cell["proxy_count"], cell["preset_id"]): cell for cell in cells}
    deltas = {}
    for count in COUNTS:
        low = by_cell[(count, "ab-low")]
        high = by_cell[(count, "ab-high")]
        deltas[str(count)] = {
            "gpu_p95_pct": pct(high["gpu_p95_median_ms"], low["gpu_p95_median_ms"]),
            "cpu_p95_pct": pct(high["cpu_p95_median_ms"], low["cpu_p95_median_ms"]),
            "pacing_p95_pct": pct(high["pacing_p95_median_ms"], low["pacing_p95_median_ms"]),
            "one_percent_low_pct": pct(high["one_percent_low_median_fps"], low["one_percent_low_median_fps"]),
        }
    scaling = {
        preset: {
            "gpu_p95_25_to_200_pct": pct(
                by_cell[(200, preset)]["gpu_p95_median_ms"], by_cell[(25, preset)]["gpu_p95_median_ms"]
            )
        }
        for preset in PRESETS
    }
    observations = [
        f"GPU p95 high vs low: 25 proxies {deltas['25']['gpu_p95_pct']:+.1f}%, 100 proxies {deltas['100']['gpu_p95_pct']:+.1f}%, 200 proxies {deltas['200']['gpu_p95_pct']:+.1f}%.",
        f"GPU p95 scaling 25→200: ab-low {scaling['ab-low']['gpu_p95_25_to_200_pct']:+.1f}%, ab-high {scaling['ab-high']['gpu_p95_25_to_200_pct']:+.1f}%.",
        f"Pacing remains ~{median([cell['pacing_p95_median_ms'] for cell in cells]):.3f} ms across all cells (240 fps cap).",
        "One 200/low run has an isolated 1% low outlier (157.39); medians are used.",
        "These are measured GPU costs on a synthetic workload, not game FPS, quality or universal recommendations.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "Vulkan 1.4.351"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1280, 720],
        "settings": {"vsync_mode": 0, "max_fps": 240},
        "runs": runs,
        "cells": cells,
        "deltas_high_vs_low": deltas,
        "scaling_25_to_200": scaling,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session; 3 runs per preset per proxy count",
            "synthetic scene at 1280x720; no cross-scene generalization",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "one isolated 1% low outlier in the 200/low cell; medians reported",
            "renderer allocation bytes are session history, not device VRAM",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Preset scaling 25/100/200 — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · vsync {report['settings']['vsync_mode']} · max_fps {report['settings']['max_fps']}",
        "",
        "## Células (medianas de 3 runs)",
        "",
        "| Count | Preset | GPU p95 | CPU p95 | Pacing p95 | 1% low | GPU spread |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for cell in report["cells"]:
        lines.append(
            f"| {cell['proxy_count']} | {cell['preset_id']} | {cell['gpu_p95_median_ms']:.3f} | "
            f"{cell['cpu_p95_median_ms']:.3f} | {cell['pacing_p95_median_ms']:.3f} | "
            f"{cell['one_percent_low_median_fps']:.2f} | {cell['gpu_p95_spread_pct']:.1f}% |"
        )
    lines.extend(["", "## Deltas high vs low", ""])
    for count in ("25", "100", "200"):
        delta = report["deltas_high_vs_low"][count]
        lines.append(
            f"- {count} proxies: GPU p95 **{delta['gpu_p95_pct']:+.1f}%**, CPU p95 {delta['cpu_p95_pct']:+.1f}%, "
            f"pacing {delta['pacing_p95_pct']:+.1f}%, 1% low {delta['one_percent_low_pct']:+.1f}%."
        )
    lines.extend(
        [
            "",
            "## Escala 25→200",
            "",
            f"- ab-low GPU p95: {report['scaling_25_to_200']['ab-low']['gpu_p95_25_to_200_pct']:+.1f}%.",
            f"- ab-high GPU p95: {report['scaling_25_to_200']['ab-high']['gpu_p95_25_to_200_pct']:+.1f}%.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_scaling.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "SCALING")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

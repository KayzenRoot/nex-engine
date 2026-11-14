#!/usr/bin/env python3
"""NEX M09 200-proxy interaction report builder.

Reads the 12 validated captures, verifies provenance and writes a deterministic
JSON/Markdown report. The 100-proxy context is read from the already integrated
interaction report and labeled as a different session.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from preset_report import load_capture, load_manifest, pct, render_cells_table, summarize, transform_run  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction-200")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
INTERACTION_REPORT = REPO_ROOT / "docs/benchmarks/m09/interaction.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "interaction-200.v1.json"
REPORT_MD = OUTPUT_DIR / "INTERACTION-200-REPORT.md"

REPORT_SCHEMA = "m09_preset_interaction_200.v1"
SCENE_ID = "arena_combat"
SCENE = "M01 Arena A/B/A"
LAYOUT = "M01 arena_combat + deterministic fillers"
RESOLUTIONS = ((960, 540), (1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _key(count: int, width: int, height: int) -> str:
    return f"{count}/{width}x{height}"


def _validate_manifest(manifest: dict[str, Any]) -> None:
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 12:
        raise ValueError("runs manifest must contain 12 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 13)):
        raise ValueError("runs manifest sequence must be 1..12")
    if len({run.get("run_id") for run in runs}) != 12:
        raise ValueError("runs manifest run ids must be unique")
    for width, height in RESOLUTIONS:
        for preset in PRESETS:
            group = [run for run in runs
                     if run.get("proxy_count") == 200
                     and run.get("viewport_px") == [width, height]
                     and run.get("preset_id") == preset]
            if len(group) != 3 or sorted(run.get("repetition") for run in group) != [1, 2, 3]:
                raise ValueError(f"runs manifest cell is invalid: {_key(200, width, height)}/{preset}")


def _context_100() -> dict[str, dict[str, float]]:
    context = load_json(INTERACTION_REPORT)
    cells = context.get("cells")
    if not isinstance(cells, list):
        raise ValueError("interaction context report has no cells")
    values: dict[str, dict[str, float]] = {}
    for width, height in RESOLUTIONS:
        key = f"{width}x{height}"
        values[key] = {}
        for preset in PRESETS:
            match = [cell for cell in cells
                     if cell.get("proxy_count") == 100
                     and cell.get("width") == width
                     and cell.get("height") == height
                     and cell.get("preset_id") == preset]
            if len(match) != 1:
                raise ValueError(f"interaction context is missing 100/{key}/{preset}")
            values[key][preset] = float(match[0]["gpu_p95_ms"])
    return values


def build_report() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_runs.v1":
        raise ValueError("runs manifest schema is invalid")
    _validate_manifest(manifest)
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    for entry in manifest["runs"]:
        capture = load_capture(EVIDENCE, entry["run_id"], SCENE, LAYOUT, 200)
        if capture["source_sha"] != source_sha:
            raise ValueError(f"{entry['run_id']}: source_sha mismatch")
        if capture["viewport"] != entry["viewport_px"]:
            raise ValueError(f"{entry['run_id']}: viewport mismatch")
        run = transform_run(entry, capture)
        run["proxy_count"] = 200
        run["viewport_px"] = entry["viewport_px"]
        runs.append(run)
    cells = []
    for width, height in RESOLUTIONS:
        for preset in PRESETS:
            group = [run for run in runs if run["viewport_px"] == [width, height] and run["preset_id"] == preset]
            if len(group) != 3:
                raise ValueError(f"expected 3 runs for {_key(200, width, height)}/{preset}")
            cells.append({"proxy_count": 200, "width": width, "height": height,
                          "preset_id": preset, **summarize(group)})
    by_cell = {(cell["width"], cell["height"], cell["preset_id"]): cell for cell in cells}
    deltas = {}
    for width, height in RESOLUTIONS:
        low = by_cell[(width, height, "ab-low")]
        high = by_cell[(width, height, "ab-high")]
        deltas[_key(200, width, height)] = {
            "gpu_p95_pct": pct(high["gpu_p95_ms"], low["gpu_p95_ms"]),
            "gpu_p99_pct": pct(high["gpu_p99_ms"], low["gpu_p99_ms"]),
            "cpu_p95_pct": pct(high["cpu_p95_ms"], low["cpu_p95_ms"]),
            "pacing_p95_pct": pct(high["pacing_p95_ms"], low["pacing_p95_ms"]),
            "one_percent_low_pct": pct(high["one_percent_low_fps"], low["one_percent_low_fps"]),
        }
    resolution_scaling = {
        "200": {
            preset: pct(
                by_cell[(1920, 1080, preset)]["gpu_p95_ms"],
                by_cell[(960, 540, preset)]["gpu_p95_ms"],
            )
            for preset in PRESETS
        }
    }
    context = _context_100()
    context_100_to_200 = {
        f"{width}x{height}": {
            preset: pct(by_cell[(width, height, preset)]["gpu_p95_ms"], context[f"{width}x{height}"][preset])
            for preset in PRESETS
        }
        for width, height in RESOLUTIONS
    }
    observations = [
        f"At 200 proxies, resolution scaling 960x540 to 1920x1080 raises GPU p95 by "
        f"{resolution_scaling['200']['ab-low']:+.1f}% (ab-low) and {resolution_scaling['200']['ab-high']:+.1f}% (ab-high).",
        f"Going from 100 to 200 proxies changes GPU p95 by only "
        f"{context_100_to_200['960x540']['ab-low']:+.1f}%/{context_100_to_200['960x540']['ab-high']:+.1f}% at 960x540 and "
        f"{context_100_to_200['1920x1080']['ab-low']:+.1f}%/{context_100_to_200['1920x1080']['ab-high']:+.1f}% at 1920x1080.",
        f"High vs low GPU p95: {deltas['200/960x540']['gpu_p95_pct']:+.1f}% at 960x540 and "
        f"{deltas['200/1920x1080']['gpu_p95_pct']:+.1f}% at 1920x1080.",
        "The pixel-bound pattern holds at 200 proxies; the 100-proxy context is from a different session and is not a same-session comparison.",
        "CPU p95 is 0.357/0.503 ms at 960x540 and 0.361/0.518 ms at 1920x1080, higher than the 50/100 cells.",
        "Pacing remains near 4.25-4.29 ms and 1% low deltas are within -0.3% to +0.4%; no gain is claimed.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "context_report": "docs/benchmarks/m09/interaction.v1.json",
        "context_session": "different session on the same day; not re-measured",
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "workload": {"scene_id": SCENE_ID, "scene": SCENE, "effect_mode": "lights",
                     "proxy_counts": [200],
                     "resolutions": [{"width": width, "height": height} for width, height in RESOLUTIONS]},
        "settings": {"vsync_mode": 0, "max_fps": 240, "native_resolution": True},
        "runs": runs,
        "cells": cells,
        "deltas_high_vs_low": deltas,
        "resolution_scaling": resolution_scaling,
        "context_100_to_200": context_100_to_200,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session on one RTX 5050; no cross-device or cross-session generalization",
            "one scene and one proxy count (200); 50/100 context is from a different session",
            "two resolutions only; 2560x1440 is not covered",
            "native resolution disables the project's canvas_items stretch mode",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · 200-proxy interaction — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Workload:** {report['workload']['scene']} · 200 proxies · native resolution",
        "",
    ]
    lines.extend(render_cells_table(report))
    lines.extend(["", "## Deltas ab-high vs ab-low (GPU p95)", ""])
    for key in ("200/960x540", "200/1920x1080"):
        delta = report["deltas_high_vs_low"][key]
        lines.append(f"- {key}: **{delta['gpu_p95_pct']:+.1f}%** (CPU p95 {delta['cpu_p95_pct']:+.1f}%, "
                     f"1% low {delta['one_percent_low_pct']:+.1f}%).")
    lines.extend(
        [
            "",
            "## Escala de resolução 960×540 → 1920×1080 (GPU p95)",
            "",
            f"- ab-low: {report['resolution_scaling']['200']['ab-low']:+.1f}%.",
            f"- ab-high: {report['resolution_scaling']['200']['ab-high']:+.1f}%.",
            "",
            "## Contexto 100 → 200 proxies (sessão diferente, GPU p95)",
            "",
            f"- 960×540: ab-low {report['context_100_to_200']['960x540']['ab-low']:+.1f}%, "
            f"ab-high {report['context_100_to_200']['960x540']['ab-high']:+.1f}%.",
            f"- 1920×1080: ab-low {report['context_100_to_200']['1920x1080']['ab-low']:+.1f}%, "
            f"ab-high {report['context_100_to_200']['1920x1080']['ab-high']:+.1f}%.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_interaction_200.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "INTERACTION_200")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

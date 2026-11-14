#!/usr/bin/env python3
"""Build the M06 M09 performance atlas from the full performance.v1 bundle.

Aggregates the 144 observations by bundle and by workload cell. No new
measurement is performed and no FPS or quality claim is made.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SOURCE = REPO_ROOT / "docs/benchmarks/m06/observations/m09-observations-full.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m06"
OUTPUT_JSON = OUTPUT_DIR / "m09-performance-atlas.v1.json"
OUTPUT_MD = OUTPUT_DIR / "M09-PERFORMANCE-ATLAS.md"

SCHEMA_VERSION = "m06_m09_performance_atlas.v1"
BUNDLES = (
    ("windows-rtx5050-2026-11-14-preset-ab", "preset-ab"),
    ("windows-rtx5050-2026-11-14-preset-scaling", "proxy-scaling"),
    ("windows-rtx5050-2026-11-14-m01-ab", "m01-ab"),
    ("windows-rtx5050-2026-11-14-res-scaling", "res-scaling"),
    ("windows-rtx5050-2026-11-14-interaction", "interaction"),
    ("windows-rtx5050-2026-11-14-cross-scene", "cross-scene"),
    ("windows-rtx5050-2026-11-14-interaction-200", "interaction-200"),
    ("windows-rtx5050-2026-11-14-arena-200-720", "interaction-200-720"),
    ("windows-rtx5050-2026-11-14-res-scaling-1440", "res-scaling-1440"),
)


def _load(path: Path) -> Any:
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)

    def constant(token):
        raise ValueError("non-finite JSON: " + token)

    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def _value(observation: dict[str, Any], key: str) -> float:
    entry = observation["timings"][key]
    if entry.get("status") != "MEASURED":
        raise ValueError(f"{observation['observation_id']}: {key} is not MEASURED")
    return float(entry["value"])


def _median(values: list[float]) -> float:
    return round(statistics.median(values), 3)


def _bundle_cells(observations: list[dict[str, Any]], sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for observation in observations:
        source = sources[observation["observation_id"]]
        workload = observation["workload"]
        key = (
            workload["scene_id"],
            source["preset_id"],
            workload["resolution"]["width_px"],
            workload["resolution"]["height_px"],
            workload["proxy_count"],
        )
        groups.setdefault(key, []).append(observation)
    cells = []
    for key, group in groups.items():
        gpu = [_value(item, "gpu_render_ms") for item in group]
        cpu = [_value(item, "cpu_render_ms") for item in group]
        pacing = [_value(item, "frame_pacing_ms") for item in group]
        cells.append(
            {
                "scene_id": key[0],
                "preset_id": key[1],
                "width_px": key[2],
                "height_px": key[3],
                "proxy_count": key[4],
                "runs": len(group),
                "gpu_p95_ms": _median(gpu),
                "cpu_p95_ms": _median(cpu),
                "pacing_p95_ms": _median(pacing),
                "max_gpu_share_pct": round(max(g / p * 100.0 for g, p in zip(gpu, pacing)), 2),
                "bottleneck": group[0]["bottleneck"]["classification"],
            }
        )
    return sorted(cells, key=lambda cell: (cell["scene_id"], cell["preset_id"], cell["proxy_count"], cell["width_px"]))


def build_report() -> dict[str, Any]:
    bundle = _load(SOURCE)
    observations = bundle.get("observations")
    sources_list = bundle.get("sources")
    if not isinstance(observations, list) or len(observations) != 156:
        raise ValueError("full observation bundle must contain 156 observations")
    if not isinstance(sources_list, list) or len(sources_list) != 156:
        raise ValueError("full observation bundle must contain 156 sources")
    sources = {entry["observation_id"]: entry for entry in sources_list}
    by_bundle: dict[str, list[dict[str, Any]]] = {name: [] for _, name in BUNDLES}
    for observation in observations:
        source = sources.get(observation["observation_id"])
        if source is None:
            raise ValueError("source mapping is missing: " + observation["observation_id"])
        short = dict((name, short) for name, short in BUNDLES).get(source["bundle"])
        if short is None:
            raise ValueError("source bundle is not recognized: " + source["bundle"])
        by_bundle[short].append(observation)
    expected = {"preset-ab": 6, "proxy-scaling": 18, "m01-ab": 18, "res-scaling": 18,
                "interaction": 24, "cross-scene": 48, "interaction-200": 12,
                "interaction-200-720": 6, "res-scaling-1440": 6}
    bundles = []
    for _, short in BUNDLES:
        group = by_bundle[short]
        if len(group) != expected[short]:
            raise ValueError(f"{short}: expected {expected[short]} observations")
        gpu = [_value(item, "gpu_render_ms") for item in group]
        cpu = [_value(item, "cpu_render_ms") for item in group]
        pacing = [_value(item, "frame_pacing_ms") for item in group]
        cells = _bundle_cells(group, sources)
        for cell in cells:
            cell["bundle"] = short
        bundles.append(
            {
                "bundle": short,
                "runs": len(group),
                "scenes": sorted({item["workload"]["scene_id"] for item in group}),
                "presets": sorted({sources[item["observation_id"]]["preset_id"] for item in group}),
                "resolutions": [
                    [width, height]
                    for width, height in sorted({
                        (item["workload"]["resolution"]["width_px"], item["workload"]["resolution"]["height_px"])
                        for item in group
                    })
                ],
                "proxy_counts": sorted({item["workload"]["proxy_count"] for item in group}),
                "bottleneck_counts": {
                    classification: sum(1 for item in group if item["bottleneck"]["classification"] == classification)
                    for classification in {item["bottleneck"]["classification"] for item in group}
                },
                "gpu_p95_ms": {"median": _median(gpu), "min": round(min(gpu), 3), "max": round(max(gpu), 3)},
                "cpu_p95_ms": {"median": _median(cpu), "min": round(min(cpu), 3), "max": round(max(cpu), 3)},
                "pacing_p95_ms": {"median": _median(pacing), "min": round(min(pacing), 3), "max": round(max(pacing), 3)},
                "max_gpu_share_pct": round(max(g / p * 100.0 for g, p in zip(gpu, pacing)), 2),
                "cells": cells,
            }
        )
    all_gpu = [_value(item, "gpu_render_ms") for item in observations]
    all_pacing = [_value(item, "frame_pacing_ms") for item in observations]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_bundle": "docs/benchmarks/m06/observations/m09-observations-full.v1.json",
        "observation_count": len(observations),
        "bundle_count": len(bundles),
        "bundles": bundles,
        "summary": {
            "bottleneck_counts": {"pacing": sum(1 for item in observations if item["bottleneck"]["classification"] == "pacing")},
            "gpu_p95_ms": {"median": _median(all_gpu), "min": round(min(all_gpu), 3), "max": round(max(all_gpu), 3)},
            "pacing_p95_ms": {"median": _median(all_pacing), "min": round(min(all_pacing), 3), "max": round(max(all_pacing), 3)},
            "max_gpu_share_pct": round(max(g / p * 100.0 for g, p in zip(all_gpu, all_pacing)), 2),
        },
        "verdict": "M09_PERFORMANCE_ATLAS_DERIVED",
        "observations": [
            "All 156 observations classify as pacing at the 240 fps cap.",
            "The atlas aggregates seven M09 performance bundles by bundle and workload cell.",
            "GPU p95 varies with scene, preset, resolution and proxy count; the per-bundle cells retain that detail.",
            "The atlas is a derived index of measured observations, not a new benchmark or a quality claim.",
        ],
        "limitations": [
            "single session on one RTX 5050 across all bundles",
            "no cross-device, cross-driver or cross-session generalization",
            "GPU render timing can describe earlier work and is not frame-aligned",
            "renderer allocation is session history, not device VRAM",
            "no FPS gain, quality or universal recommendation is claimed",
            "M06 bounded admission covers evidence/analysis only",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M06 · M09 performance atlas — RTX 5050",
        "",
        "**Status:** `M09_PERFORMANCE_ATLAS_DERIVED / SINGLE_SESSION / NO_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['source_bundle']}` · **Observações:** {report['observation_count']} · **Bundles:** {report['bundle_count']}",
        "",
        "## Bundles",
        "",
        "| Bundle | Runs | Scenes | Presets | GPU p95 median | CPU p95 median | Pacing p95 median | Max GPU share | Bottleneck |",
        "|---|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for bundle in report["bundles"]:
        lines.append(
            f"| {bundle['bundle']} | {bundle['runs']} | {len(bundle['scenes'])} | {len(bundle['presets'])} | "
            f"{bundle['gpu_p95_ms']['median']:.3f} | {bundle['cpu_p95_ms']['median']:.3f} | "
            f"{bundle['pacing_p95_ms']['median']:.3f} | {bundle['max_gpu_share_pct']:.2f}% | "
            f"{bundle['bottleneck_counts']} |"
        )
    top_cells = sorted(
        (cell for bundle in report["bundles"] for cell in bundle["cells"]),
        key=lambda cell: cell["gpu_p95_ms"],
        reverse=True,
    )[:10]
    lines.extend(
        [
            "",
            "## Top 10 células por GPU p95",
            "",
            "| Bundle | Cena | Preset | Resolução | Proxies | Runs | GPU p95 | CPU p95 | Pacing p95 | GPU share |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for cell in top_cells:
        lines.append(
            f"| {cell['bundle']} | {cell['scene_id']} | "
            f"{cell['preset_id']} | {cell['width_px']}×{cell['height_px']} | {cell['proxy_count']} | "
            f"{cell['runs']} | {cell['gpu_p95_ms']:.3f} | {cell['cpu_p95_ms']:.3f} | "
            f"{cell['pacing_p95_ms']:.3f} | {cell['max_gpu_share_pct']:.2f}% |"
        )
    lines.extend(
        [
            "",
            "## Resumo",
            "",
            f"- Bottlenecks: {report['summary']['bottleneck_counts']}.",
            f"- GPU p95 global: {report['summary']['gpu_p95_ms']['min']:.3f}–{report['summary']['gpu_p95_ms']['max']:.3f} ms "
            f"(mediana {report['summary']['gpu_p95_ms']['median']:.3f}).",
            f"- Pacing p95: {report['summary']['pacing_p95_ms']['min']:.3f}–{report['summary']['pacing_p95_ms']['max']:.3f} ms.",
            f"- Maior GPU share: {report['summary']['max_gpu_share_pct']:.2f}%.",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Atlas gerado por `docs/benchmarks/m06/tools/build_m09_atlas.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    report = build_report()
    rendered_json = render_json(report)
    rendered_md = render_markdown(report)
    if argv == ["--check"]:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            print("M06_M09_ATLAS_CHECK_FAIL: outputs missing")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered_json:
            print("M06_M09_ATLAS_CHECK_FAIL: JSON is stale")
            return 1
        if OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            print("M06_M09_ATLAS_CHECK_FAIL: Markdown is stale")
            return 1
        print(f"M06_M09_ATLAS_CHECK_PASS: {report['observation_count']} observations")
        return 0
    if argv:
        print("usage: build_m09_atlas.py [--check]")
        return 2
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_json)
    with open(OUTPUT_MD, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_md)
    print(f"M06_M09_ATLAS_WRITE_PASS: {report['observation_count']} observations")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

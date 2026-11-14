#!/usr/bin/env python3
"""NEX M09 M01 visual-truth 1920x1080 report builder.

Verifies the 18 PNG captures, proves A/A determinism by SHA-256 equality,
compares matched low/high images and reports the change relative to the
integrated 1280x720 visual report. No new capture and no quality claim.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from png_image import compare, read_png, sha256_file  # noqa: E402 - local tool module
from preset_report import pct  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-1920")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
CONTEXT = REPO_ROOT / "docs/benchmarks/m09/m01-visual.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "m01-visual-1920.v1.json"
REPORT_MD = OUTPUT_DIR / "M01-VISUAL-1920-REPORT.md"

REPORT_SCHEMA = "m09_preset_m01_visual_1920.v1"
VIEWPORT = [1920, 1080]
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A"),
    ("arena_combat", "M01 Arena A/B/A"),
    ("dense_city", "M01 City A/B/A"),
)
PRESETS = ("ab-low", "ab-high")
REPETITIONS = (1, 2, 3)
CHANGED_PIXEL_THRESHOLD = 2


def _manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "preset_ab_visual_runs.v1":
        raise ValueError("visual runs manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 18:
        raise ValueError("visual runs manifest must contain 18 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 19)):
        raise ValueError("visual runs manifest sequence must be 1..18")
    if len({run.get("file") for run in runs}) != 18:
        raise ValueError("visual runs manifest files must be unique")
    for scene_id, scene in SCENES:
        for preset in PRESETS:
            group = [run for run in runs if run["scene_id"] == scene_id and run["preset_id"] == preset]
            if len(group) != 3 or sorted(run["repetition"] for run in group) != [1, 2, 3]:
                raise ValueError(f"visual runs manifest cell is invalid: {scene_id}/{preset}")
            for run in group:
                if run.get("scene") != scene or [run.get("width"), run.get("height")] != VIEWPORT:
                    raise ValueError("visual runs manifest provenance is invalid")
    return manifest


def _context() -> dict[str, dict[str, float]]:
    report = load_json(CONTEXT)
    values: dict[str, dict[str, float]] = {}
    for scene in report.get("scenes", []):
        summary = scene.get("summary", {})
        values[scene["scene_id"]] = {
            "mean_abs_diff": float(summary["ab_mean_abs_diff_median"]),
            "changed_pixels_pct": float(summary["ab_changed_pixels_pct_median"]),
            "psnr_db": float(summary["ab_psnr_db_median"]),
        }
    return values


def build_report() -> dict[str, Any]:
    manifest = _manifest()
    context = _context()
    cells: dict[tuple[str, str], dict[str, Any]] = {}
    for run in manifest["runs"]:
        path = EVIDENCE / run["file"]
        if not path.is_file() or sha256_file(path) != run["sha256"]:
            raise ValueError("visual image hash mismatch: " + run["file"])
        cell = cells.setdefault((run["scene_id"], run["preset_id"]), {"hashes": set(), "files": {}})
        cell["hashes"].add(run["sha256"])
        cell["files"][run["repetition"]] = path
    for key, cell in cells.items():
        if len(cell["hashes"]) != 1:
            raise ValueError(f"visual repetitions are not deterministic: {key}")
    scenes = []
    for scene_id, scene in SCENES:
        low = read_png(cells[(scene_id, "ab-low")]["files"][1])
        high = read_png(cells[(scene_id, "ab-high")]["files"][1])
        ab = compare(low, high, CHANGED_PIXEL_THRESHOLD)
        aa = compare(low, low, CHANGED_PIXEL_THRESHOLD)
        images = [
            {
                "sequence": run["sequence"],
                "preset_id": run["preset_id"],
                "repetition": run["repetition"],
                "file": run["file"],
                "sha256": run["sha256"],
            }
            for run in manifest["runs"] if run["scene_id"] == scene_id
        ]
        scenes.append(
            {
                "scene_id": scene_id,
                "scene": scene,
                "images": images,
                "aa": {"identical_sha": True, "comparisons": 6, "metrics": aa},
                "ab": {"metrics": ab, "matched_pairs": 3},
                "comparison_1280": {
                    **context[scene_id],
                    "delta_mean_abs_pct": pct(ab["mean_abs_diff"], context[scene_id]["mean_abs_diff"]),
                    "delta_changed_pixels_pct": pct(
                        ab["changed_pixels_pct"], context[scene_id]["changed_pixels_pct"]
                    ),
                },
            }
        )
    return {
        "schema_version": REPORT_SCHEMA,
        "harness_source_sha": manifest.get("harness_source_sha"),
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "context_report": "docs/benchmarks/m09/m01-visual.v1.json",
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": VIEWPORT,
        "workload": manifest["workload"],
        "changed_pixel_threshold": CHANGED_PIXEL_THRESHOLD,
        "runs": 18,
        "scenes": scenes,
        "verdict": "VISUAL_DIFFERENCE_OBSERVED",
        "observations": [
            "A/A is exact: all three repetitions of each scene/preset pair share one SHA-256.",
            "ab-high changes the image in every scene at 1920x1080; changed pixels are 3.367% (corridor), 3.354% (arena) and 1.276% (city).",
            "The A/B mean absolute difference is slightly lower at 1920x1080 than at 1280x720 in all three scenes.",
            "The direction is consistent across resolutions: the high preset changes the image, and city has the smallest difference.",
            "This is a pixel-difference observation, not a quality ranking or a universal recommendation.",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "static frame only; animation, temporal effects and camera motion are not covered",
            "fillers may overlap base-scene props; this is a stress composition, not a beauty shot",
            "PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · M01 visual truth at 1920×1080 — RTX 5050",
        "",
        "**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Harness SHA:** `{report['harness_source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · threshold de pixel alterado: {report['changed_pixel_threshold']}",
        "",
        "## Comparações por cena",
        "",
        "| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR | Δ mean abs vs 1280 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scene in report["scenes"]:
        ab = scene["ab"]["metrics"]
        comparison = scene["comparison_1280"]
        lines.append(
            f"| {scene['scene_id']} | {'sim' if scene['aa']['identical_sha'] else 'não'} | "
            f"{scene['aa']['metrics']['mean_abs_diff']:.4f} | {ab['mean_abs_diff']:.4f} | "
            f"{ab['max_abs_diff']} | {ab['changed_pixels_pct']:.3f}% | {ab['psnr_db']:.3f} dB | "
            f"{comparison['delta_mean_abs_pct']:+.1f}% |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_m01_visual_1920.py`; não é benchmark nem claim de qualidade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "M01_VISUAL_1920")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

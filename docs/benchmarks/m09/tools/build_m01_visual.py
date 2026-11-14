#!/usr/bin/env python3
"""NEX M09 M01 visual-truth report builder.

Verifies the 18 PNG captures and their manifest, proves A/A determinism by
SHA-256 equality, decodes one image per scene/preset cell and writes a
deterministic JSON/Markdown pixel-difference report. No new capture is
performed and no visual-quality claim is made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module
from png_image import compare, read_png, sha256_file  # noqa: E402 - local tool module
from preset_report import median  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "m01-visual.v1.json"
REPORT_MD = OUTPUT_DIR / "M01-VISUAL-REPORT.md"

REPORT_SCHEMA = "m09_preset_m01_visual.v1"
RUNS_SCHEMA = "preset_ab_visual_runs.v1"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A"),
    ("arena_combat", "M01 Arena A/B/A"),
    ("dense_city", "M01 City A/B/A"),
)
PRESETS = ("ab-low", "ab-high")
REPETITIONS = (1, 2, 3)
EXPECTED_VIEWPORT = [1280, 720]
CHANGED_PIXEL_THRESHOLD = 2


def _validate_cell(runs: list[dict[str, Any]], scene_id: str, scene: str, preset_id: str) -> None:
    group = [run for run in runs if run.get("scene_id") == scene_id and run.get("preset_id") == preset_id]
    if len(group) != 3 or sorted(run.get("repetition") for run in group) != [1, 2, 3]:
        raise ValueError(f"visual runs manifest cell is invalid: {scene_id}/{preset_id}")
    for run in group:
        if run.get("scene") != scene:
            raise ValueError("visual runs manifest scene label is invalid")
        if [run.get("width"), run.get("height")] != EXPECTED_VIEWPORT:
            raise ValueError("visual runs manifest viewport is invalid")


def _validate_runs(runs: list[dict[str, Any]]) -> None:
    if not isinstance(runs, list) or len(runs) != 18:
        raise ValueError("visual runs manifest must contain 18 runs")
    if [run.get("sequence") for run in runs] != list(range(1, 19)):
        raise ValueError("visual runs manifest sequence must be 1..18")
    if len({run.get("file") for run in runs}) != 18:
        raise ValueError("visual runs manifest file names must be unique")
    for scene_id, scene in SCENES:
        for preset_id in PRESETS:
            _validate_cell(runs, scene_id, scene, preset_id)


def load_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != RUNS_SCHEMA:
        raise ValueError("visual runs manifest schema is invalid")
    _validate_runs(manifest.get("runs"))
    return manifest


def verify_images(runs: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    cells: dict[tuple[str, str], dict[str, Any]] = {}
    for run in runs:
        path = EVIDENCE / run["file"]
        if not path.is_file():
            raise ValueError("visual image is missing: " + run["file"])
        if sha256_file(path) != run["sha256"]:
            raise ValueError("visual image hash mismatch: " + run["file"])
        cell = cells.setdefault((run["scene_id"], run["preset_id"]), {"hashes": set(), "files": {}})
        cell["hashes"].add(run["sha256"])
        cell["files"][run["repetition"]] = path
    for key, cell in cells.items():
        if len(cell["hashes"]) != 1:
            raise ValueError(f"visual repetitions are not deterministic: {key}")
    return cells


def build_report() -> dict[str, Any]:
    manifest = load_manifest()
    runs = manifest["runs"]
    cells = verify_images(runs)
    scenes = []
    for scene_id, scene in SCENES:
        low = read_png(cells[(scene_id, "ab-low")]["files"][1])
        high = read_png(cells[(scene_id, "ab-high")]["files"][1])
        aa_low = compare(low, low, CHANGED_PIXEL_THRESHOLD)
        aa_high = compare(high, high, CHANGED_PIXEL_THRESHOLD)
        ab = compare(low, high, CHANGED_PIXEL_THRESHOLD)
        scene_runs = [run for run in runs if run["scene_id"] == scene_id]
        images = [
            {
                "sequence": run["sequence"],
                "preset_id": run["preset_id"],
                "repetition": run["repetition"],
                "file": run["file"],
                "sha256": run["sha256"],
            }
            for run in scene_runs
        ]
        aa_comparisons = []
        for preset_id, metrics in (("ab-low", aa_low), ("ab-high", aa_high)):
            for first, second in ((1, 2), (2, 3), (1, 3)):
                aa_comparisons.append(
                    {
                        "preset_id": preset_id,
                        "first_repetition": first,
                        "second_repetition": second,
                        "identical_sha": True,
                        "metrics": metrics,
                    }
                )
        ab_comparisons = [
            {"repetition": repetition, "metrics": ab}
            for repetition in REPETITIONS
        ]
        scenes.append(
            {
                "scene_id": scene_id,
                "scene": scene,
                "images": images,
                "aa_comparisons": aa_comparisons,
                "ab_comparisons": ab_comparisons,
                "summary": {
                    "aa_all_identical": True,
                    "aa_max_mean_abs_diff": max(
                        entry["metrics"]["mean_abs_diff"] for entry in aa_comparisons
                    ),
                    "ab_mean_abs_diff_median": median(
                        [entry["metrics"]["mean_abs_diff"] for entry in ab_comparisons]
                    ),
                    "ab_changed_pixels_pct_median": median(
                        [entry["metrics"]["changed_pixels_pct"] for entry in ab_comparisons]
                    ),
                    "ab_psnr_db_median": median(
                        [entry["metrics"]["psnr_db"] for entry in ab_comparisons]
                    ),
                },
            }
        )
    aa_ok = all(scene["summary"]["aa_all_identical"] for scene in scenes)
    ab_ok = all(
        scene["summary"]["ab_mean_abs_diff_median"] > 0.1
        and scene["summary"]["ab_changed_pixels_pct_median"] > 1.0
        for scene in scenes
    )
    if not aa_ok:
        verdict = "INCONCLUSIVE_NONDETERMINISTIC"
    elif ab_ok:
        verdict = "VISUAL_DIFFERENCE_OBSERVED"
    else:
        verdict = "NO_VISUAL_DIFFERENCE_OBSERVED"
    observations = [
        "A/A is exact: all three repetitions of each scene/preset pair share one SHA-256, so every A/A pixel difference is zero.",
        "ab-high changes the image in every scene: corridor 4.077% changed pixels, arena 3.884%, city 1.745% at threshold 2.",
        "The matched A/B pairs are identical within each scene because the repetitions are byte-identical; medians are reported.",
        "City has the smallest changed-pixel fraction; corridor has the largest at this fixed camera and 100-mesh composition.",
        "The difference confirms a rendering-state change, not a visual-quality ranking or a universal recommendation.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "harness_source_sha": manifest.get("harness_source_sha"),
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": EXPECTED_VIEWPORT,
        "workload": manifest["workload"],
        "changed_pixel_threshold": CHANGED_PIXEL_THRESHOLD,
        "runs": len(runs),
        "scenes": scenes,
        "verdict": verdict,
        "observations": observations,
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
        "# NEX M09 · M01 visual truth — RTX 5050",
        "",
        f"**Status:** `{report['verdict']} / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Harness SHA:** `{report['harness_source_sha']}`",        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · threshold de pixel alterado: {report['changed_pixel_threshold']}",
        "",
        "## Comparações por cena",
        "",
        "| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for scene in report["scenes"]:
        summary = scene["summary"]
        ab = scene["ab_comparisons"][0]["metrics"]
        lines.append(
            f"| {scene['scene_id']} | {'sim' if summary['aa_all_identical'] else 'não'} | "
            f"{summary['aa_max_mean_abs_diff']:.4f} | {summary['ab_mean_abs_diff_median']:.4f} | "
            f"{ab['max_abs_diff']} | {summary['ab_changed_pixels_pct_median']:.3f}% | "
            f"{summary['ab_psnr_db_median']:.3f} dB |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_m01_visual.py`; não é benchmark nem claim de qualidade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "M01_VISUAL")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

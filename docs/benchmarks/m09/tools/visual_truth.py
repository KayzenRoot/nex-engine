"""Shared core for M01 visual-truth reports."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from common import load_json
from png_image import compare, read_png, sha256_file

REPO_ROOT = Path(__file__).resolve().parents[4]
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A"),
    ("arena_combat", "M01 Arena A/B/A"),
    ("dense_city", "M01 City A/B/A"),
)
PRESETS = ("ab-low", "ab-high")
REPETITIONS = (1, 2, 3)
CHANGED_PIXEL_THRESHOLD = 2
RUNS = 18


def load_manifest(evidence: Path, viewport: list[int]) -> dict[str, Any]:
    manifest = load_json(evidence / "runs.v1.json")
    if manifest.get("schema_version") != "preset_ab_visual_runs.v1":
        raise ValueError("visual runs manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != RUNS:
        raise ValueError("visual runs manifest must contain 18 runs")
    if [run.get("sequence") for run in runs] != list(range(1, RUNS + 1)):
        raise ValueError("visual runs manifest sequence must be 1..18")
    if len({run.get("file") for run in runs}) != RUNS:
        raise ValueError("visual runs manifest files must be unique")
    for scene_id, scene in SCENES:
        for preset in PRESETS:
            group = [run for run in runs if run["scene_id"] == scene_id and run["preset_id"] == preset]
            if len(group) != 3 or sorted(run["repetition"] for run in group) != [1, 2, 3]:
                raise ValueError(f"visual runs manifest cell is invalid: {scene_id}/{preset}")
            for run in group:
                if run.get("scene") != scene or [run.get("width"), run.get("height")] != viewport:
                    raise ValueError("visual runs manifest provenance is invalid")
    return manifest


def build_visual_core(evidence_rel: Path, viewport: list[int]) -> dict[str, Any]:
    evidence = REPO_ROOT / evidence_rel
    manifest = load_manifest(evidence, viewport)
    cells: dict[tuple[str, str], dict[str, Any]] = {}
    for run in manifest["runs"]:
        path = evidence / run["file"]
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
            }
        )
    return {
        "harness_source_sha": manifest.get("harness_source_sha"),
        "evidence_bundle": evidence_rel.as_posix(),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": viewport,
        "workload": manifest["workload"],
        "changed_pixel_threshold": CHANGED_PIXEL_THRESHOLD,
        "runs": RUNS,
        "scenes": scenes,
    }


def render_visual_markdown(report: dict[str, Any], title: str, context_key: str,
                           context_label: str, footer: str) -> str:
    lines = [
        f"# {title}",
        "",
        "**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Harness SHA:** `{report['harness_source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · threshold de pixel alterado: {report['changed_pixel_threshold']}",
        "",
        "## Comparações por cena",
        "",
        f"| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR | Δ mean abs vs {context_label} |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scene in report["scenes"]:
        ab = scene["ab"]["metrics"]
        comparison = scene[context_key]
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
    lines.extend(["", footer, ""])
    return "\n".join(lines)

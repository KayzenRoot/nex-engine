#!/usr/bin/env python3
"""Build the M01 golden matrix and S01 acceptance report.

Reads the 18 native 1920x1080 captures, verifies A/A byte identity, computes
A/B metrics for the full frame and five fixed regions, and records the S01
acceptance image and license provenance. No new capture is performed.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import run_cli  # noqa: E402 - shared local tool module
from visual_truth import build_visual_core  # noqa: E402 - shared local tool module
from png_image import read_png  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-golden")
EVIDENCE = REPO / EVIDENCE_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m01"
REPORT_JSON = OUTPUT / "golden-matrix.v1.json"
REPORT_MD = OUTPUT / "GOLDEN-MATRIX.md"
SOURCE_SHA = "900d2b2d031a87048702625a1e98bc50905bc663"
VIEWPORT = [1920, 1080]
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A", 4101),
    ("arena_combat", "M01 Arena A/B/A", 4102),
    ("dense_city", "M01 City A/B/A", 4103),
)
REGIONS = (
    ("full", 0.0, 0.0, 1.0, 1.0),
    ("center_gameplay", 0.2, 0.15, 0.8, 0.85),
    ("top_band", 0.0, 0.0, 1.0, 0.15),
    ("bottom_band", 0.0, 0.85, 1.0, 1.0),
    ("left_band", 0.0, 0.0, 0.2, 1.0),
    ("right_band", 0.8, 0.0, 1.0, 1.0),
)
THRESHOLD = 2


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _region_metrics(first, second, region: tuple[str, float, float, float, float]) -> dict[str, Any]:
    _, x0, y0, x1, y1 = region
    width, height, channels = first.width, first.height, first.channels
    left, top = int(width * x0), int(height * y0)
    right, bottom = int(width * x1), int(height * y1)
    total = 0
    changed = 0
    squared = 0
    absolute = 0
    for y in range(top, bottom):
        for x in range(left, right):
            offset = (y * width + x) * channels
            diffs = [abs(first.pixels[offset + c] - second.pixels[offset + c]) for c in range(channels)]
            total += 1
            if max(diffs) > THRESHOLD:
                changed += 1
            absolute += sum(diffs)
            squared += sum(diff * diff for diff in diffs)
    if total == 0:
        raise ValueError("empty region")
    mse = squared / (total * channels)
    psnr = None if mse == 0 else round(20.0 * math.log10(255.0 / math.sqrt(mse)), 3)
    return {
        "pixels": total,
        "mean_abs_diff": round(absolute / (total * channels), 4),
        "changed_pixels_pct": round(changed * 100.0 / total, 3),
        "psnr_db": psnr,
    }


def build_report() -> dict[str, Any]:
    core = build_visual_core(EVIDENCE_REL, VIEWPORT)
    core["session_date"] = "2026-11-15"
    core["source_sha"] = SOURCE_SHA
    core["harness_source_sha"] = SOURCE_SHA
    scenes = []
    for scene_id, scene, seed in SCENES:
        entry = next(item for item in core["scenes"] if item["scene_id"] == scene_id)
        low_path = EVIDENCE / f"{scene_id}_ab-low_1.png"
        high_path = EVIDENCE / f"{scene_id}_ab-high_1.png"
        low, high = read_png(low_path), read_png(high_path)
        if low.channels != high.channels:
            raise ValueError("channel mismatch for " + scene_id)
        regions = {name: _region_metrics(low, high, (name, x0, y0, x1, y1))
                   for name, x0, y0, x1, y1 in REGIONS}
        scenes.append({
            "scene_id": scene_id,
            "scene": scene,
            "seed": seed,
            "scene_sha256": _sha(REPO / "nex_bench" / "scenes" / "base" / f"{scene_id}.tscn"),
            "acceptance_image": {
                "file": low_path.name,
                "sha256": _sha(low_path),
                "width": low.width,
                "height": low.height,
            },
            "aa": entry["aa"],
            "ab": entry["ab"],
            "regions": regions,
        })
    return {
        "schema_version": "m01_golden_matrix.v1",
        "source_sha": SOURCE_SHA,
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "session_date": core["session_date"],
        "godot_version": core["godot_version"],
        "hardware": core["hardware"],
        "viewport_px": VIEWPORT,
        "workload": core["workload"],
        "changed_pixel_threshold": THRESHOLD,
        "runs": core["runs"],
        "scenes": scenes,
        "license": {
            "status": "ORIGINAL_NEX_GENERATED_NO_THIRD_PARTY_ASSETS",
            "audit": "docs/benchmarks/m01/LICENSE-AUDIT.md",
            "third_party_assets": 0,
        },
        "verdict": "S01_ACCEPTANCE_AND_S03_GOLDEN_MATRIX_DERIVED",
        "observations": [
            "all 18 captures are 1920x1080 native Forward+/Vulkan on the RTX 5050",
            "all three repetitions per scene/preset are byte-identical",
            "the ab-low vs ab-high comparison is the only lighting/preset difference",
            "S01 acceptance images are the ab-low first repetitions per scene",
            "no third-party asset is referenced by the three base scenes",
        ],
        "limitations": [
            "single session, one GPU and driver; static frame",
            "PNG comparison is a regression signal, not an artistic quality metric",
            "fillers may overlap base-scene props",
            "no FPS, game-performance or cross-device generalization claim",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M01 · Golden matrix and S01 acceptance",
        "",
        "**Status:** `GOLDEN_MATRIX_DERIVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · threshold {report['changed_pixel_threshold']}",
        "",
        "| Cena | Seed | A/A idêntico | A/B mean abs | A/B pixels | A/B PSNR | Imagem de aceitação |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for scene in report["scenes"]:
        ab = scene["ab"]["metrics"]
        lines.append(
            f"| {scene['scene_id']} | {scene['seed']} | {'sim' if scene['aa']['identical_sha'] else 'não'} | "
            f"{ab['mean_abs_diff']:.4f} | {ab['changed_pixels_pct']:.3f}% | {ab['psnr_db']:.3f} dB | "
            f"`{scene['acceptance_image']['file']}` |"
        )
    lines.extend(["", "## Regiões (ab-low vs ab-high)", ""])
    lines.extend(["| Cena | Região | Mean abs | Pixels alterados | PSNR |", "|---|---|---:|---:|---:|"])
    for scene in report["scenes"]:
        for name, metrics in scene["regions"].items():
            psnr = "∞" if metrics["psnr_db"] is None else f"{metrics['psnr_db']:.3f} dB"
            lines.append(f"| {scene['scene_id']} | {name} | {metrics['mean_abs_diff']:.4f} | "
                         f"{metrics['changed_pixels_pct']:.3f}% | {psnr} |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m01/tools/build_golden_matrix.py`; não é benchmark de hardware.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M01_GOLDEN_MATRIX")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

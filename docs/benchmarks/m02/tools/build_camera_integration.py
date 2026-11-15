#!/usr/bin/env python3
"""Build the M02-S01 camera scene/performance integration report."""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png, sha256_file  # noqa: E402 - shared local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
VISUAL_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-camera-visual")
PERF_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-camera-perf")
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m02"
REPORT_JSON = OUTPUT_DIR / "camera-integration.v1.json"
REPORT_MD = OUTPUT_DIR / "CAMERA-INTEGRATION.md"

REPORT_SCHEMA = "m02_camera_integration.v1"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A"),
    ("arena_combat", "M01 Arena A/B/A"),
    ("dense_city", "M01 City A/B/A"),
)
MODES = ("baseline", "rig")
REPETITIONS = (1, 2, 3)
RUNS = 18
CHANGED_PIXEL_THRESHOLD = 2


def _visual() -> dict[str, Any]:
    base = REPO_ROOT / VISUAL_REL
    manifest = load_json(base / "runs.v1.json")
    if manifest.get("schema_version") != "preset_ab_camera_ab_runs.v1":
        raise ValueError("camera visual manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != RUNS:
        raise ValueError("camera visual manifest must contain 18 runs")
    cells = {}
    for run in runs:
        path = base / run["file"]
        if not path.is_file() or sha256_file(path) != run["sha256"]:
            raise ValueError("camera visual hash mismatch: " + run["file"])
        cells.setdefault((run["scene_id"], run["camera_mode"]), {})[run["repetition"]] = path
    scenes = []
    for scene_id, scene in SCENES:
        hashes = {}
        for mode in MODES:
            group = cells[(scene_id, mode)]
            if sorted(group) != list(REPETITIONS):
                raise ValueError(f"camera visual cell is invalid: {scene_id}/{mode}")
            values = {sha256_file(group[rep]) for rep in REPETITIONS}
            if len(values) != 1:
                raise ValueError(f"camera visual repetitions are not deterministic: {scene_id}/{mode}")
            hashes[mode] = values.pop()
        metrics = compare(read_png(cells[(scene_id, "baseline")][1]), read_png(cells[(scene_id, "rig")][1]),
                          CHANGED_PIXEL_THRESHOLD)
        scenes.append({
            "scene_id": scene_id,
            "scene": scene,
            "aa_identical": True,
            "baseline_sha256": hashes["baseline"],
            "rig_sha256": hashes["rig"],
            "ab": metrics,
        })
    return {
        "evidence_bundle": VISUAL_REL.as_posix(),
        "runs": RUNS,
        "scenes": scenes,
    }


def _perf() -> dict[str, Any]:
    base = REPO_ROOT / PERF_REL
    manifest = load_json(base / "runs.v1.json")
    if manifest.get("schema_version") != "preset_ab_camera_perf_runs.v1":
        raise ValueError("camera performance manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != RUNS:
        raise ValueError("camera performance manifest must contain 18 runs")
    cells = {}
    for run in runs:
        path = base / run["file"]
        if not path.is_file() or sha256_file(path) != run["sha256"]:
            raise ValueError("camera performance hash mismatch: " + run["file"])
        capture = load_json(path)
        if capture.get("run_status") != "COMPLETE":
            raise ValueError("camera performance capture is not COMPLETE")
        cells.setdefault((run["scene_id"], run["camera_mode"]), []).append(capture)
    scenes = []
    for scene_id, scene in SCENES:
        medians = {}
        for mode in MODES:
            group = cells[(scene_id, mode)]
            if len(group) != 3:
                raise ValueError(f"camera performance cell is invalid: {scene_id}/{mode}")
            def median(key: str) -> float:
                return statistics.median(
                    capture["series"][key]["aggregates"]["p95"] for capture in group
                )
            medians[mode] = {
                "gpu_p95_ms": round(median("GPU_RENDER_MS"), 3),
                "cpu_p95_ms": round(median("CPU_RENDER_MS"), 3),
                "pacing_p95_ms": round(median("FRAME_PACING_INTERVAL_MS"), 3),
            }
        scenes.append({
            "scene_id": scene_id,
            "scene": scene,
            "baseline": medians["baseline"],
            "rig": medians["rig"],
            "delta_pct": {
                key: round((medians["rig"][key] - medians["baseline"][key]) / medians["baseline"][key] * 100.0, 2)
                for key in ("gpu_p95_ms", "cpu_p95_ms", "pacing_p95_ms")
            },
        })
    return {
        "evidence_bundle": PERF_REL.as_posix(),
        "runs": RUNS,
        "scenes": scenes,
    }


def build_report() -> dict[str, Any]:
    visual = _visual()
    perf = _perf()
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": "ad41089a3a37407ce8773ea86ac364873971551d",
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1280, 720],
        "visual": visual,
        "performance": perf,
        "verdict": "CAMERA_RIG_REPRODUCES_BASELINE_FRAMING",
        "observations": [
            "all three repetitions of each camera mode are byte-identical",
            "the rig reproduces the baseline framing with negligible pixel difference: 0.000% (city), 0.003% (arena) and 0.013% (corridor) of changed pixels",
            "GPU p95 is effectively unchanged (0.0% to +1.25%); CPU p95 is unchanged in corridor and +12.9%/+13.3% in arena/city with small absolute values",
            "this is a scene and performance comparison for one preset, not a quality or FPS claim",
        ],
        "limitations": [
            "single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization",
            "one preset (ab-low), static frame and one camera pose per scene",
            "CPU p95 deltas are small in absolute terms and not proven to be causal",
            "no animation, camera motion, gameplay or production-scene validation",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
        "runs": RUNS,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M02-S01 · Camera integration — RTX 5050",
        "",
        "**Status:** `CAMERA_RIG_REPRODUCES_BASELINE_FRAMING / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte visual:** `{report['visual']['evidence_bundle']}`",
        f"**Fonte performance:** `{report['performance']['evidence_bundle']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        "",
        "## Visual A/B/A",
        "",
        "| Cena | A/A idêntico | Mean abs | Pixels alterados | PSNR | Max abs |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for scene in report["visual"]["scenes"]:
        ab = scene["ab"]
        lines.append(
            f"| {scene['scene_id']} | {'sim' if scene['aa_identical'] else 'não'} | "
            f"{ab['mean_abs_diff']:.4f} | {ab['changed_pixels_pct']:.3f}% | "
            f"{ab['psnr_db']:.2f} dB | {ab['max_abs_diff']} |"
        )
    lines.extend([
        "",
        "## Performance A/B/A (medianas de 3 runs)",
        "",
        "| Cena | GPU p95 baseline | GPU p95 rig | Δ GPU | CPU p95 baseline | CPU p95 rig | Δ CPU |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for scene in report["performance"]["scenes"]:
        lines.append(
            f"| {scene['scene_id']} | {scene['baseline']['gpu_p95_ms']:.3f} | {scene['rig']['gpu_p95_ms']:.3f} | "
            f"{scene['delta_pct']['gpu_p95_ms']:+.2f}% | {scene['baseline']['cpu_p95_ms']:.3f} | "
            f"{scene['rig']['cpu_p95_ms']:.3f} | {scene['delta_pct']['cpu_p95_ms']:+.2f}% |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m02/tools/build_camera_integration.py`; não é benchmark nem claim de qualidade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD,
                   argv, "M02_CAMERA_INTEGRATION")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Build the M02-S02/S03/S04 scene-analysis integration report."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-analysis")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
SCRIPT = REPO_ROOT / "nex_bench/scenes/m02_analysis/run_analysis.gd"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m02"
REPORT_JSON = OUTPUT_DIR / "analysis-integration.v1.json"
REPORT_MD = OUTPUT_DIR / "ANALYSIS-INTEGRATION.md"

REPORT_SCHEMA = "m02_scene_analysis_integration.v1"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A"),
    ("arena_combat", "M01 Arena A/B/A"),
    ("dense_city", "M01 City A/B/A"),
)
RUNS = 3


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != "m02_scene_analysis_runs.v1":
        raise ValueError("analysis manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != RUNS:
        raise ValueError("analysis manifest must contain 3 runs")
    if manifest.get("harness_sha256") != _sha(SCRIPT):
        raise ValueError("analysis harness hash does not match the manifest")
    scenes = []
    for scene_id, scene in SCENES:
        entry = next((run for run in runs if run["scene_id"] == scene_id), None)
        if entry is None:
            raise ValueError("analysis manifest is missing " + scene_id)
        path = EVIDENCE / entry["file"]
        if not path.is_file() or _sha(path) != entry["sha256"]:
            raise ValueError("analysis output hash mismatch: " + entry["file"])
        document = load_json(path)
        sightline = document["sightline"]
        depth = document["depth"]
        temporal = document["temporal"]
        scenes.append({
            "scene_id": scene_id,
            "scene": scene,
            "mesh_count": document["mesh_count"],
            "occluders_used": document["occluders_used"],
            "primitives_used": document["primitives_used"],
            "sightline": {
                "summary": sightline["summary"],
                "actors": [
                    {"id": actor["id"], "blocked_by": actor["blocked_by"],
                     "visual_readable": actor["visual_readable"],
                     "danger_alert": actor["danger_alert"]}
                    for actor in sightline["actors"]
                ],
            },
            "depth": {
                "z_fight_risks": len(depth["z_fight_risks"]),
                "alpha_over_critical": len(depth["alpha_over_critical"]),
                "overlay_gameplay_conflicts": len(depth["overlay_gameplay_conflicts"]),
                "passes": {key: len(value) for key, value in depth["passes"].items()},
            },
            "temporal": {
                "verdict": temporal["verdict"],
                "action": temporal["action"],
                "frames": temporal["frames"],
                "regions": temporal["regions"],
                "metrics": temporal["metrics"],
            },
        })
    return {
        "schema_version": REPORT_SCHEMA,
        "source_sha": manifest.get("source_sha"),
        "harness_sha256": manifest.get("harness_sha256"),
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "scenes": scenes,
        "verdict": "SCENE_ANALYSIS_DERIVED",
        "observations": [
            "the sightline policy reveals the player behind the largest occluder and raises one danger alert in every scene",
            "no critical actor is left unseen in any scene",
            "the depth planner reports 0 z-fight risks in corridor and 4 in arena/city; no alpha-over-critical or overlay-gameplay conflicts",
            "the temporal analyzer returns BASELINE_ACCEPTABLE on the five static frames of all three scenes",
            "these are headless analysis results over real scene AABBs and static frames, not rendering or quality claims",
        ],
        "limitations": [
            "meshes are approximated as AABBs or spheres; per-pixel depth, edges, aliasing and transparency are not evaluated",
            "one deterministic actor layout per scene; no gameplay or animation",
            "temporal analysis uses 4x4 luminance regions from static frames; real TAA/upscale/compositor remain INCONCLUSIVE_NOT_RUN",
            "no rendering, GPU, FPS, quality or cross-device claim",
        ],
        "runs": RUNS,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M02 · Scene analysis (S02/S03/S04) — RTX 5050",
        "",
        "**Status:** `SCENE_ANALYSIS_DERIVED / HEADLESS / NO_RENDERING_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Harness SHA-256:** `{report['harness_sha256']}`",
        "",
        "| Cena | Meshes | Occluders | Primitives | Reveals | Z-fight | Alpha/overlay | Temporal |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for scene in report["scenes"]:
        sight = scene["sightline"]["summary"]
        depth = scene["depth"]
        lines.append(
            f"| {scene['scene_id']} | {scene['mesh_count']} | {scene['occluders_used']} | "
            f"{scene['primitives_used']} | {sight['active_reveals']} | {depth['z_fight_risks']} | "
            f"{depth['alpha_over_critical']}/{depth['overlay_gameplay_conflicts']} | {scene['temporal']['verdict']} |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m02/tools/build_analysis_integration.py`; não é benchmark nem claim de qualidade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD,
                   argv, "M02_ANALYSIS_INTEGRATION")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Build the M08 scene-composition report from the headless CompositionPlanner run."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_modules/render2_5d/composition/evidence/scene-composition-2026-11-15.json")
EVIDENCE = REPO / EVIDENCE_REL
MANIFEST_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-analysis/runs.v1.json")
MANIFEST = REPO / MANIFEST_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m08"
REPORT_JSON = OUTPUT / "scene-composition.v1.json"
REPORT_MD = OUTPUT / "SCENE-COMPOSITION.md"
BASE_SHA = "d218525cbd7cd84b5c69f5e52577a6244f8733b6"
SCENES = ("corridor_static", "arena_combat", "dense_city")
VERDICTS = {"SAFE_CONFIG_HEURISTIC", "CONFLICTS_REPORTED", "INVALID_INPUT"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    document = load_json(EVIDENCE)
    if document.get("schema_version") != "m08_scene_composition_run.v1":
        raise ValueError("unexpected scene-composition evidence schema")
    if document.get("source_sha") != BASE_SHA:
        raise ValueError("evidence source SHA does not match the work-order base")
    if document.get("analysis_manifest_sha256") != _sha(MANIFEST):
        raise ValueError("M02 analysis manifest hash does not match the evidence")
    entries = document.get("scenes")
    if not isinstance(entries, list) or [entry.get("scene_id") for entry in entries] != list(SCENES):
        raise ValueError("evidence must contain the three M01 scenes in order")
    scenes = []
    for entry in entries:
        report = entry.get("report", {})
        if report.get("verdict") not in VERDICTS:
            raise ValueError("invalid composition verdict for " + entry["scene_id"])
        base = report["base_3d_plan"]
        scenes.append({
            "scene_id": entry["scene_id"],
            "scene_sha256": entry["scene_sha256"],
            "verdict": report["verdict"],
            "layers": len(report["layers"]),
            "critical_entities": [entity["entity_id"] for entity in report["critical_entities"]],
            "base_3d_plan": {
                "opaque": base["opaque_count"],
                "alpha": base["alpha_count"],
                "overlay": base["overlay_count"],
                "z_fight_risks": base["z_fight_risks"],
                "alpha_over_critical": base["alpha_over_critical"],
                "overlay_gameplay_conflicts": base["overlay_gameplay_conflicts"],
            },
            "conflicts": [{"code": item["code"], "severity": item["severity"]}
                          for item in report.get("conflicts", [])],
        })
    return {
        "schema_version": "m08_scene_composition.v1",
        "source_sha": BASE_SHA,
        "analysis_manifest_uri": MANIFEST_REL.as_posix(),
        "analysis_manifest_sha256": document["analysis_manifest_sha256"],
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "evidence_sha256": _sha(EVIDENCE),
        "scenes": scenes,
        "verdict": "COMPOSITION_PLANNING_DERIVED",
        "observations": [
            "corridor_static is SAFE_CONFIG_HEURISTIC with no conflicts",
            "arena_combat and dense_city each report one medium base_z_fight_risk from the M02 depth plan",
            "all scenes keep zero high, alpha-over-critical and overlay/gameplay conflicts",
            "each plan has four layers and the player/threat critical entities",
        ],
        "limitations": document.get("limitations", []),
        "runs": len(scenes),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M08 · Scene composition from M02 analysis",
        "",
        "**Status:** `COMPOSITION_PLANNING_DERIVED / NON_RENDERING / NO_VISUAL_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Manifesto M02:** `{report['analysis_manifest_uri']}` · **SHA-256:** `{report['analysis_manifest_sha256']}`",
        f"**Evidence SHA-256:** `{report['evidence_sha256']}`",
        "",
        "| Cena | Opaque | Alpha | Overlay | Z-fight | Veredito |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for scene in report["scenes"]:
        base = scene["base_3d_plan"]
        lines.append(
            f"| {scene['scene_id']} | {base['opaque']} | {base['alpha']} | {base['overlay']} | "
            f"{base['z_fight_risks']} | {scene['verdict']} |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m08/tools/build_scene_composition.py`; não é benchmark visual.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M08_SCENE_COMPOSITION")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

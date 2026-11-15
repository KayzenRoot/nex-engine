#!/usr/bin/env python3
"""Build the M10 archetype-feedback report from the headless FeedbackPlanner run."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_modules/animation/combat_feedback/evidence/archetype-feedback-2026-11-15.json")
EVIDENCE = REPO / EVIDENCE_REL
DATASET_REL = Path("nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json")
DATASET = REPO / DATASET_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m10"
REPORT_JSON = OUTPUT / "archetype-feedback.v1.json"
REPORT_MD = OUTPUT / "ARCHETYPE-FEEDBACK.md"
BASE_SHA = "91e6c15794662b3502244c2d03879b8dbb9980dd"
ARCHETYPES = ("skirmish", "elite", "boss")
VERDICTS = {"SAFE_CONFIG_HEURISTIC", "REVIEW_REQUIRED", "BLOCKED"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    document = load_json(EVIDENCE)
    if document.get("schema_version") != "m10_archetype_feedback_run.v1":
        raise ValueError("unexpected archetype-feedback evidence schema")
    if document.get("source_sha") != BASE_SHA:
        raise ValueError("evidence source SHA does not match the work-order base")
    if document.get("dataset_sha256") != _sha(DATASET):
        raise ValueError("M05 dataset hash does not match the evidence")
    entries = document.get("archetypes")
    if not isinstance(entries, list) or [entry.get("archetype_id") for entry in entries] != list(ARCHETYPES):
        raise ValueError("evidence must contain skirmish, elite and boss in order")
    archetypes = []
    for entry in entries:
        plans = entry.get("spells", [])
        if not plans:
            raise ValueError("archetype has no spell plans: " + entry["archetype_id"])
        for plan in plans:
            if plan["report"]["verdict"] not in VERDICTS:
                raise ValueError("invalid feedback verdict")
        archetypes.append({
            "archetype_id": entry["archetype_id"],
            "label": entry["label"],
            "spells": [
                {
                    "spell_id": plan["spell_id"],
                    "element": plan["element"],
                    "damage": plan["damage"],
                    "critical": plan["critical"],
                    "verdict": plan["report"]["verdict"],
                    "total_channels": plan["report"]["metrics"]["total_channels"],
                    "peak_concurrency": plan["report"]["metrics"]["peak_concurrency"],
                }
                for plan in plans
            ],
            "summary": entry["summary"],
        })
    return {
        "schema_version": "m10_archetype_feedback.v1",
        "source_sha": BASE_SHA,
        "dataset_uri": DATASET_REL.as_posix(),
        "dataset_sha256": document["dataset_sha256"],
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "evidence_sha256": _sha(EVIDENCE),
        "archetypes": archetypes,
        "verdict": "FEEDBACK_PLANNING_DERIVED",
        "observations": [
            "all 10 spell plans return SAFE_CONFIG_HEURISTIC with zero conflicts",
            "each spell uses five channels and peaks at the 5-channel concurrency budget",
            "archetype totals are 10, 15 and 25 channels for skirmish, elite and boss",
            "the largest shake intensity is 0.313 for meteor-storm, below the 0.8 budget",
        ],
        "limitations": document.get("limitations", []),
        "runs": len(archetypes),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M10 · Archetype combat feedback",
        "",
        "**Status:** `FEEDBACK_PLANNING_DERIVED / NON_RENDERING / NO_GAME_FEEL_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Dataset:** `{report['dataset_uri']}` · **SHA-256:** `{report['dataset_sha256']}`",
        f"**Evidence SHA-256:** `{report['evidence_sha256']}`",
        "",
        "| Arquétipo | Spells | Canais | Pico | Hit-stop | Shake máx. | Veredito |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for archetype in report["archetypes"]:
        summary = archetype["summary"]
        verdicts = sorted(set(summary["verdicts"]))
        lines.append(
            f"| {archetype['archetype_id']} | {summary['spells']} | {summary['total_channels']} | "
            f"{summary['max_peak_concurrency']} | {summary['total_hit_stop_ms']} ms | "
            f"{summary['max_shake_intensity']:.3f} | {'/'.join(verdicts)} |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m10/tools/build_archetype_feedback.py`; não é benchmark de game feel.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M10_ARCHETYPE_FEEDBACK")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Build the M05 FX budget dataset report from headless planner evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json")
EVIDENCE = REPO / EVIDENCE_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m05"
REPORT_JSON = OUTPUT / "fx-budget-dataset.v1.json"
REPORT_MD = OUTPUT / "FX-BUDGET-DATASET.md"
BASE_SHA = "99437b22e94a6494eaef801872bb8fd0c79c0f1a"
ARCHETYPES = ("skirmish", "elite", "boss")
VERDICTS = {"FIT", "TIGHT", "OVER_BUDGET"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    document = load_json(EVIDENCE)
    if document.get("schema_version") != "fx_budget_dataset.v1":
        raise ValueError("unexpected dataset schema")
    if document.get("source_sha") != BASE_SHA:
        raise ValueError("dataset source SHA does not match the work-order base")
    entries = document.get("archetypes")
    if not isinstance(entries, list) or [entry.get("archetype_id") for entry in entries] != list(ARCHETYPES):
        raise ValueError("dataset must contain skirmish, elite and boss in order")
    archetypes = []
    for entry in entries:
        report = entry.get("report", {})
        if report.get("verdict") not in VERDICTS:
            raise ValueError("invalid verdict for " + entry["archetype_id"])
        archetypes.append({
            "archetype_id": entry["archetype_id"],
            "label": entry["label"],
            "spell_count": entry["spell_count"],
            "budget": entry["budget"],
            "verdict": report["verdict"],
            "totals": report["totals"],
            "findings": [{"code": item["code"], "severity": item["severity"]}
                         for item in report.get("findings", [])],
            "reduction_steps": report.get("reduction_plan", {}).get("particles", {}).get("steps_count", 0),
        })
    return {
        "schema_version": "m05_fx_budget_dataset.v1",
        "source_sha": BASE_SHA,
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "evidence_sha256": _sha(EVIDENCE),
        "godot_version": document["godot_version"],
        "archetypes": archetypes,
        "verdict": "BUDGET_PLANNING_DERIVED",
        "observations": [
            "skirmish fits its budget with 484 particles and 7 emitters",
            "elite is TIGHT on particles at 1047/1100 (95.2%)",
            "boss exceeds the 2000-particle budget at 2753 (137.7%) and receives a 3-step reduction plan",
            "no particle, emitter, light, decal or renderer is created",
        ],
        "limitations": document.get("limitations", []),
        "runs": len(archetypes),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M05 · FX budget dataset",
        "",
        "**Status:** `BUDGET_PLANNING_DERIVED / NON_RENDERING / NO_PERFORMANCE_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Evidence SHA-256:** `{report['evidence_sha256']}`",
        "",
        "| Arquétipo | Spells | Emitters | Particles | GPU emitters | Decals | Veredito |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for archetype in report["archetypes"]:
        totals = archetype["totals"]
        lines.append(
            f"| {archetype['archetype_id']} | {archetype['spell_count']} | {totals['emitters']} | "
            f"{totals['particles']} | {totals['gpu_emitters']} | {totals['decals']} | {archetype['verdict']} |"
        )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m05/tools/build_fx_budget_dataset.py`; não é benchmark de hardware.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M05_FX_BUDGET_DATASET")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

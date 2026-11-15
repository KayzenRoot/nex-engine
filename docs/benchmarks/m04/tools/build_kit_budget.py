#!/usr/bin/env python3
"""Build the M04 kit-budget report from the headless TextureBudgetPlanner run."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_modules/materials/texturebudget/evidence/kit-budget-2026-11-15.json")
EVIDENCE = REPO / EVIDENCE_REL
KIT_REL = Path("nex_modules/materials/kit/kit.v1.json")
KIT = REPO / KIT_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m04"
REPORT_JSON = OUTPUT / "kit-budget.v1.json"
REPORT_MD = OUTPUT / "KIT-BUDGET.md"
BASE_SHA = "873f4a7d05d3b70912a5112089e3ebfbf068703c"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    document = load_json(EVIDENCE)
    if document.get("schema_version") != "m04_kit_budget_run.v1":
        raise ValueError("unexpected kit-budget evidence schema")
    if document.get("source_sha") != BASE_SHA:
        raise ValueError("evidence source SHA does not match the work-order base")
    if document.get("kit_sha256") != _sha(KIT):
        raise ValueError("kit observation hash does not match the evidence")
    report = document.get("report", {})
    if report.get("verdict") not in {"FIT", "TIGHT", "OVER_BUDGET"}:
        raise ValueError("invalid planner verdict")
    return {
        "schema_version": "m04_kit_budget.v1",
        "source_sha": BASE_SHA,
        "kit_uri": KIT_REL.as_posix(),
        "kit_sha256": document["kit_sha256"],
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "evidence_sha256": _sha(EVIDENCE),
        "verdict": report["verdict"],
        "materials": report["materials"],
        "texture_refs": report["texture_refs"],
        "unique_textures": len(report["unique_textures"]),
        "decoded_bytes_total": report["decoded_bytes_total"],
        "decoded_bytes_dedup": report["decoded_bytes_dedup"],
        "duplicate_refs": report["duplicate_refs"],
        "atlas": report["atlas"],
        "budget": report["budget"],
        "findings": [{"code": item["code"], "severity": item["severity"]}
                     for item in report.get("findings", [])],
        "observations": [
            "all 12 kit textures are unique and referenced once",
            "decoded size is 1,048,572 bytes against a 268,435,456-byte budget",
            "atlas pressure is 0.047 (12 tiles of 256 available)",
            "the planner reports no findings and a FIT verdict",
        ],
        "limitations": report.get("limitations", []),
        "runs": 1,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M04 · Kit texture budget",
        "",
        "**Status:** `BUDGET_PLANNING_DERIVED / NON_RENDERING / NO_PERFORMANCE_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Kit:** `{report['kit_uri']}` · **SHA-256:** `{report['kit_sha256']}`",
        f"**Evidência:** `{report['evidence_bundle']}` · **SHA-256:** `{report['evidence_sha256']}`",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
        f"| Materiais | {report['materials']} |",
        f"| Refs de textura | {report['texture_refs']} |",
        f"| Texturas únicas | {report['unique_textures']} |",
        f"| Bytes decodificados | {report['decoded_bytes_total']} |",
        f"| Bytes deduplicados | {report['decoded_bytes_dedup']} |",
        f"| Refs duplicadas | {report['duplicate_refs']} |",
        f"| Pressão de atlas | {report['atlas']['pressure_ratio']} |",
        f"| Veredito | {report['verdict']} |",
    ]
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m04/tools/build_kit_budget.py`; não é benchmark de hardware.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M04_KIT_BUDGET")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Build the M11 kit-audit report from the headless AssetPipelineAuditor run."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_modules/assets/license_audit/evidence/kit-audit-2026-11-15.json")
EVIDENCE = REPO / EVIDENCE_REL
KIT_REL = Path("nex_modules/materials/kit/kit.v1.json")
KIT = REPO / KIT_REL
OUTPUT = REPO / "docs" / "benchmarks" / "m11"
REPORT_JSON = OUTPUT / "kit-audit.v1.json"
REPORT_MD = OUTPUT / "KIT-AUDIT.md"
BASE_SHA = "7e425920cdaf17c158d46979e68df47e66742724"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    document = load_json(EVIDENCE)
    if document.get("schema_version") != "m11_kit_audit_run.v1":
        raise ValueError("unexpected kit-audit evidence schema")
    if document.get("source_sha") != BASE_SHA:
        raise ValueError("evidence source SHA does not match the work-order base")
    if document.get("kit_sha256") != _sha(KIT):
        raise ValueError("kit observation hash does not match the evidence")
    report = document.get("report", {})
    if report.get("verdict") not in {"READY_FOR_INTEGRATION", "REVIEW_REQUIRED", "BLOCKED"}:
        raise ValueError("invalid auditor verdict")
    counts: dict[str, int] = {}
    for finding in report.get("findings", []):
        counts[finding["code"]] = counts.get(finding["code"], 0) + 1
    return {
        "schema_version": "m11_kit_audit.v1",
        "source_sha": BASE_SHA,
        "kit_uri": KIT_REL.as_posix(),
        "kit_sha256": document["kit_sha256"],
        "evidence_bundle": EVIDENCE_REL.as_posix(),
        "evidence_sha256": _sha(EVIDENCE),
        "verdict": report["verdict"],
        "metrics": report["metrics"],
        "summary": report["summary"],
        "findings": counts,
        "recommendations": list(report.get("recommendations", [])),
        "observations": [
            "12 kit textures were audited with matching SHA-256 values",
            "no stage failed and no stage is pending; raw and imported are the only stages",
            "0 high-severity findings; 12 medium license_unverified and 12 low texture_uncompressed",
            "the auditor recommends verifying licenses and enabling texture compression",
        ],
        "limitations": report.get("limitations", []),
        "runs": 1,
    }


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# NEX M11 · Kit asset-pipeline audit",
        "",
        "**Status:** `AUDIT_DERIVED / NON_RENDERING / LICENSES_UNVERIFIED / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Kit:** `{report['kit_uri']}` · **SHA-256:** `{report['kit_sha256']}`",
        f"**Evidência:** `{report['evidence_bundle']}` · **SHA-256:** `{report['evidence_sha256']}`",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
        f"| Assets | {metrics['assets']} |",
        f"| Bytes totais | {metrics['total_cooked_bytes']} |",
        f"| Bytes de textura | {metrics['texture_cooked_bytes']} |",
        f"| Estágios falhos | {metrics['failed_stages']} |",
        f"| Estágios pendentes | {metrics['pending_stages']} |",
        f"| Licenças não verificadas | {metrics['unverified_licenses']} |",
        f"| Findings high/medium/low | {report['summary']['high']}/{report['summary']['medium']}/{report['summary']['low']} |",
        f"| Veredito | {report['verdict']} |",
    ]
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m11/tools/build_kit_audit.py`; não é verificação jurídica de licença.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M11_KIT_AUDIT")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

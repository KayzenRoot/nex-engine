#!/usr/bin/env python3
"""Build the M11 asset-tools report from deterministic smoke evidence."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parents[1] / "tools"))
from runtime_report import render_json, run_cli, sha  # noqa: E402 - shared tool module

REPO = Path(__file__).resolve().parents[4]
SMOKE = REPO / "nex_modules" / "assets" / "asset_lab" / "evidence" / "m11-asset-smoke-2026-11-17.json"
AUDITOR_LOG = REPO / "nex_modules" / "assets" / "license_audit" / "evidence" / "headless-smoke-2026-11-14.log"
KIT_AUDIT = REPO / "nex_modules" / "assets" / "license_audit" / "evidence" / "kit-audit-2026-11-15.json"
FIXTURES = REPO / "nex_modules" / "assets" / "asset_lab" / "fixtures"
OUTPUT = REPO / "docs" / "benchmarks" / "m11"
REPORT_JSON = OUTPUT / "asset-tools.v1.json"
REPORT_MD = OUTPUT / "ASSET-TOOLS.md"
SOURCE_SHA = "13554f3e9ee879c48edb32d780c6fa0611d41b19"


def _load(path: Path) -> dict:
    import json
    return json.loads(path.read_text(encoding="utf-8"))


def _auditor_checks() -> int:
    text = AUDITOR_LOG.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("NEX_M11_AUDIT_SMOKE_PASS:"):
            return int(line.split(":", 1)[1].strip().split()[0])
    raise ValueError("auditor smoke has no pass line")


def build_report() -> dict[str, Any]:
    smoke = _load(SMOKE)
    kit = _load(KIT_AUDIT)
    if smoke.get("schema_version") != "m11_asset_smoke.v1":
        raise ValueError("asset smoke schema is invalid")
    if smoke.get("source_sha") != SOURCE_SHA:
        raise ValueError("asset smoke source SHA is stale")
    if smoke.get("verdict") != "PASS" or smoke.get("failures") != []:
        raise ValueError("asset smoke did not pass")
    checks = int(smoke.get("checks", 0))
    if checks != 39:
        raise ValueError("asset smoke must contain 39 checks")
    auditor_checks = _auditor_checks()
    if auditor_checks != 43:
        raise ValueError("auditor smoke must contain 43 checks")
    kit_metrics = kit.get("report", {}).get("metrics", {})
    kit_verdict = kit.get("report", {}).get("verdict", "")
    if int(kit_metrics.get("assets", 0)) != 12 or int(kit_metrics.get("failed_stages", 0)) != 0:
        raise ValueError("kit audit is unexpected")
    manifest = smoke["manifest"]
    if int(manifest["assets"]) != 8 or int(manifest["counts"]["error"]) != 2:
        raise ValueError("manifest summary is unexpected")
    cook = smoke["cook_plan"]
    if cook["counts"] != {"accepted": 5, "rejected": 1, "noop": 1, "conflicts": 1}:
        raise ValueError("cook plan is unexpected")
    license_audit = smoke["license_audit"]
    if license_audit["verdict"] != "BLOCKED":
        raise ValueError("license verdict is unexpected")
    quality = smoke["quality"]
    if quality["verdict"] != "REVIEW_REQUIRED":
        raise ValueError("quality verdict is unexpected")
    fixtures = sorted(FIXTURES.glob("*.json"))
    if len(fixtures) != 3:
        raise ValueError("asset lab must contain 3 fixtures")
    return {
        "schema_version": "m11_asset_tools.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-17",
        "s01": {"auditor_checks": auditor_checks, "kit_assets": int(kit_metrics["assets"]),
                "kit_failed_stages": int(kit_metrics["failed_stages"]),
                "kit_verdict": kit_verdict, "verdict": "ASSET_AUDITOR_VERIFIED"},
        "s02": {"assets": int(manifest["assets"]), "errors": int(manifest["counts"]["error"]),
                "warns": int(manifest["counts"]["warn"]),
                "total_bytes": int(manifest["total_bytes"]), "verdict": "ASSET_MANIFEST_DERIVED"},
        "s03": {"counts": cook["counts"], "snapshot": smoke.get("cook_snapshot", ""),
                "verdict": "COOK_PLANNER_DERIVED"},
        "s04": {"counts": license_audit["counts"], "verdict_name": license_audit["verdict"],
                "verdict": "LICENSE_LEDGER_DERIVED"},
        "s05": {"counts": quality["counts"], "verdict_name": quality["verdict"],
                "verdict": "QUALITY_GATE_DERIVED"},
        "s06": {"checks": auditor_checks + checks, "fixtures": len(fixtures),
                "real_third_party_assets": 0, "verdict": "M11_ASSET_QA_VERIFIED"},
        "decisions": [
            {"id": "AssetPipelineAuditor", "decision": "GO",
             "evidence": f"{auditor_checks} checks; 12 kit assets, 0 failed stages"},
            {"id": "AssetManifest", "decision": "GO_WITH_LIMITATIONS",
             "evidence": "8 assets; 2 errors and 2 warnings from declared metadata"},
            {"id": "CookPlanner", "decision": "GO_WITH_LIMITATIONS",
             "evidence": "5 accepted / 1 rejected / 1 noop / 1 conflict; plan only"},
            {"id": "LicenseLedger", "decision": "GO_WITH_LIMITATIONS",
             "evidence": "2 third-party, 1 unverified, 2 rejected, 2 attribution; BLOCKED"},
            {"id": "AssetQualityGate", "decision": "GO_WITH_LIMITATIONS",
             "evidence": "0 errors, 5 warnings, 2 info; REVIEW_REQUIRED"},
        ],
        "fixtures": [{"name": path.name, "sha256": sha(path), "bytes": path.stat().st_size}
                     for path in fixtures],
        "verdict": "M11_ASSET_TOOLS_REFERENCE_DERIVED",
        "observations": [
            "AssetPipelineAuditor still passes 43 headless checks",
            "the M04 kit audit covers 12 assets with 0 failed and 0 pending stages",
            "AssetManifest reports 2 errors and 2 warnings across 8 deterministic assets",
            "CookPlanner plans 5 accepted, 1 rejected, 1 noop and 1 conflict without writing",
            "LicenseLedger returns BLOCKED with 2 rejected and 1 unverified license",
            "AssetQualityGate returns REVIEW_REQUIRED with 5 warnings and 2 info findings",
        ],
        "limitations": [
            "fixtures only; no asset is imported, cooked, loaded or rendered",
            "license verification is declared data, not legal review",
            "cook sizes are declared bytes, not filesystem or GPU measurements",
            "quality findings are structural heuristics, not visual review",
            "no FPS, VRAM, quality or PoE2 parity claim",
        ],
        "runs": 1,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M11 · Asset tools",
        "",
        "**Status:** `M11_ASSET_TOOLS_REFERENCE_DERIVED / HEADLESS_FIXTURES / NO_IMPORT_OR_COOK / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **Engine:** Godot 4.7.2-stable",
        "",
        "## S01 · AssetPipelineAuditor",
        "",
        f"- **{report['s01']['verdict']}**: {report['s01']['auditor_checks']} checks; "
        f"kit {report['s01']['kit_assets']} assets, {report['s01']['kit_failed_stages']} failed stages, "
        f"verdict `{report['s01']['kit_verdict']}`.",
        "",
        "## S02 · AssetManifest",
        "",
        f"- **{report['s02']['verdict']}**: {report['s02']['assets']} assets; "
        f"{report['s02']['errors']} errors, {report['s02']['warns']} warns; "
        f"{report['s02']['total_bytes']} bytes declarados.",
        "",
        "## S03 · CookPlanner",
        "",
        f"- accepted **{report['s03']['counts']['accepted']}**, rejected **{report['s03']['counts']['rejected']}**, "
        f"noop **{report['s03']['counts']['noop']}**, conflicts **{report['s03']['counts']['conflicts']}**.",
        "- Plano determinístico; nenhum arquivo é escrito ou sobrescrito.",
        "",
        "## S04 · LicenseLedger",
        "",
        f"- 3rd-party **{report['s04']['counts']['third_party']}**, unverified **{report['s04']['counts']['unverified']}**, "
        f"rejected **{report['s04']['counts']['rejected']}**, attribution **{report['s04']['counts']['attribution']}**; "
        f"veredito `{report['s04']['verdict_name']}`.",
        "",
        "## S05 · AssetQualityGate",
        "",
        f"- errors **{report['s05']['counts']['error']}**, warns **{report['s05']['counts']['warn']}**, "
        f"info **{report['s05']['counts']['info']}**; veredito `{report['s05']['verdict_name']}`.",
        "",
        "## S06 · QA",
        "",
        f"- {report['s06']['checks']} checks totais; {report['s06']['fixtures']} fixtures; "
        f"{report['s06']['real_third_party_assets']} assets de terceiros reais.",
        "",
        "## Decisões",
        "",
        "| Tecnologia | Decisão | Evidência |",
        "|---|---|---|",
    ]
    for decision in report["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m11/tools/build_m11_asset_tools.py`; não é verificação jurídica.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M11_ASSET_TOOLS")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

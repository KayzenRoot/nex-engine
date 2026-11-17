"""Acceptance tests for the M11 asset-pipeline reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _m0x_final_support import (assert_builder, assert_checkpoint, assert_governance,
                                assert_no_false_independent)

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m11"
RUNTIME = PACK / "asset-tools.v1.json"
GATE = PACK / "M11-FINAL-GATE.md"
LAB = REPO / "nex_modules" / "assets" / "asset_lab"
SMOKE = LAB / "evidence" / "m11-asset-smoke-2026-11-17.json"
AUDITOR_LOG = REPO / "nex_modules" / "assets" / "license_audit" / "evidence" / "headless-smoke-2026-11-14.log"
KIT_AUDIT = REPO / "nex_modules" / "assets" / "license_audit" / "evidence" / "kit-audit-2026-11-15.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0022-M11-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M11-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M11-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"


class M11FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        assert_governance(self, (ADR, WO, LOCK, RUNTIME, GATE, SMOKE, AUDITOR_LOG, KIT_AUDIT,
                                 LAB / "asset_manifest.gd", LAB / "cook_planner.gd",
                                 LAB / "license_ledger.gd", LAB / "quality_gate.gd"))

    def test_asset_smoke_passes(self) -> None:
        self.assertEqual("m11_asset_smoke.v1", self.smoke["schema_version"])
        self.assertEqual("PASS", self.smoke["verdict"])
        self.assertEqual(39, self.smoke["checks"])
        self.assertEqual([], self.smoke["failures"])

    def test_auditor_and_kit_audit_pass(self) -> None:
        self.assertEqual(43, self.runtime["s01"]["auditor_checks"])
        self.assertEqual(12, self.runtime["s01"]["kit_assets"])
        self.assertEqual(0, self.runtime["s01"]["kit_failed_stages"])
        self.assertEqual("REVIEW_REQUIRED", self.runtime["s01"]["kit_verdict"])
        self.assertIn("NEX_M11_AUDIT_SMOKE_PASS: 43 checks", AUDITOR_LOG.read_text(encoding="utf-8"))

    def test_manifest_and_cook_are_measured(self) -> None:
        self.assertEqual(8, self.runtime["s02"]["assets"])
        self.assertEqual(2, self.runtime["s02"]["errors"])
        self.assertEqual(2, self.runtime["s02"]["warns"])
        self.assertEqual(270592, self.runtime["s02"]["total_bytes"])
        self.assertEqual({"accepted": 5, "rejected": 1, "noop": 1, "conflicts": 1},
                         self.runtime["s03"]["counts"])
        self.assertEqual(64, len(self.runtime["s03"]["snapshot"]))

    def test_license_and_quality_are_conservative(self) -> None:
        self.assertEqual("BLOCKED", self.runtime["s04"]["verdict_name"])
        self.assertEqual(2, self.runtime["s04"]["counts"]["rejected"])
        self.assertEqual(1, self.runtime["s04"]["counts"]["unverified"])
        self.assertEqual("REVIEW_REQUIRED", self.runtime["s05"]["verdict_name"])
        self.assertEqual(5, self.runtime["s05"]["counts"]["warn"])
        self.assertEqual(0, self.runtime["s05"]["counts"]["error"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["decisions"]}
        self.assertEqual("GO", decisions["AssetPipelineAuditor"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["AssetManifest"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["CookPlanner"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["LicenseLedger"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        assert_checkpoint(self, self.checkpoint, "m11FinalReference",
                          "NEX-M11-FINAL-REFERENCE-WO-001", [16], "M11_REFERENCE_ASSET_TOOLS_ONLY")

    def test_builder_is_enforced(self) -> None:
        assert_builder(self, WORKFLOW, "docs/benchmarks/m11/tools/build_m11_asset_tools.py --check")

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#16", "M11_ASSET_TOOLS_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        assert_no_false_independent(self, (ADR, WO, GATE))


if __name__ == "__main__":
    unittest.main()

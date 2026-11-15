"""Consistency tests for the NEX-ADR-0011 M04/M05 non-rendering asset-kit scope."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0011-M04-M05-ASSET-KIT-BOUNDED-ADMISSION.md"
LEDGER = REPO / ".engineering" / "DECISIONS-LEDGER.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
AGENTS = REPO / "AGENTS.md"
SCOPE = REPO / ".engineering" / "SCOPE.md"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
WO = REPO / ".engineering" / "work-orders" / "NEX-M04-M05-ASSET-KIT-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M04-M05-ASSET-KIT-WO-001-EXECUTION.json"


class M04M05AssetKitAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.block = cls.checkpoint["m04M05AssetKit"]
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, LEDGER, CHECKPOINT, AGENTS, SCOPE, WORKFLOW, WO, LOCK):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_adr_and_ledger_record_the_decision(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        ledger = LEDGER.read_text(encoding="utf-8")
        for phrase in ("BOUNDED_ADMITTED_MATERIALS_PIPELINE", "BOUNDED_ADMITTED_VFX_PIPELINE",
                       "kit PBR procedural", "dataset de orçamento", "runtime", "renderer", "ADMIN_SOLO"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, adr)
        self.assertIn("NEX-D-021", ledger)
        self.assertIn("NEX-ADR-0011-M04-M05-ASSET-KIT-BOUNDED-ADMISSION.md", ledger)

    def test_checkpoint_block_and_scope(self) -> None:
        self.assertEqual("NEX-M04-M05-ASSET-KIT-WO-001", self.block["id"])
        self.assertEqual([9, 10], self.block["issues"])
        self.assertEqual(12, self.block["kit"]["textures"])
        self.assertEqual(4, self.block["kit"]["materials"])
        self.assertEqual({"skirmish": "FIT", "elite": "TIGHT", "boss": "OVER_BUDGET"},
                         self.block["dataset"]["verdicts"])
        excluded = " ".join(self.block["excludedScope"]).lower()
        for phrase in ("shader", "renderer", "runtime", "particle", "texture decoding", "fps"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, excluded)
        self.assertFalse(self.block["ciRelaxation"])
        self.assertFalse(self.block["runtimeAdmission"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.block["audit"])

    def test_agents_and_scope_point_to_the_extension(self) -> None:
        for path in (AGENTS, SCOPE):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("NEX-ADR-0011", text)
                self.assertIn("nex_modules/materials/kit", text)
                self.assertIn("nex_modules/vfx/fxbudget/dataset.gd", text)

    def test_lock_binds_base_scope_and_writer(self) -> None:
        self.assertEqual("99437b22e94a6494eaef801872bb8fd0c79c0f1a", self.lock["authorityBaseSha"])
        self.assertEqual(9, self.lock["issue"])
        self.assertEqual([10], self.lock["secondaryIssues"])
        self.assertEqual(27, len(self.lock["authorityBaseFingerprints"]))
        self.assertEqual("ADMIN_SOLO_SINGLE_WRITER", self.lock["executionMode"])
        allowed = " ".join(self.lock["scope"]["writeAllowedExact"])
        for phrase in ("NEX-ADR-0011", "DECISIONS-LEDGER.md", "AGENTS.md", "SCOPE.md", "CHECKPOINT.json"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, allowed)

    def test_builders_are_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m04/tools/build_material_kit.py --check", workflow)
        self.assertIn("docs/benchmarks/m05/tools/build_fx_budget_dataset.py --check", workflow)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, SCOPE, WO))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

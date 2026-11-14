"""Consistency tests for the M03 bounded analysis admission."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0007-M03-BOUNDED-ADMISSION.md"
LEDGER = REPO / ".engineering" / "DECISIONS-LEDGER.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
AGENTS = REPO / "AGENTS.md"
SCOPE = REPO / ".engineering" / "SCOPE.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-ADMISSION-M03-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-ADMISSION-M03-WO-001-EXECUTION.json"


class M03AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.admission = cls.checkpoint["m03BoundedAdmission"]
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, LEDGER, CHECKPOINT, AGENTS, SCOPE, WO, LOCK):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_adr_and_ledger_record_the_decision(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        ledger = LEDGER.read_text(encoding="utf-8")
        for phrase in ("BOUNDED_ADMITTED_ANALYSIS_PIPELINE", "M03", "runtime", "renderer", "NOT_ADMITTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, adr)
        self.assertIn("NEX-D-017", ledger)
        self.assertIn("BOUNDED_ADMITTED_ANALYSIS_PIPELINE", ledger)

    def test_checkpoint_status_and_scope(self) -> None:
        self.assertIn("M03_M06_M09_BOUNDED_ADMITTED", self.checkpoint["status"])
        self.assertEqual(8, self.admission["issue"])
        self.assertEqual("BOUNDED_ADMITTED_ANALYSIS_PIPELINE", self.admission["status"])
        self.assertEqual(
            ["M01", "M02", "M04", "M05", "M07", "M08", "M10", "M11", "M12"],
            self.admission["notAdmitted"],
        )
        excluded = " ".join(self.admission["excludedScope"]).lower()
        for phrase in ("runtime", "renderer", "shaders", "scenes", "fps"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, excluded)
        self.assertFalse(self.admission["ciRelaxation"])
        self.assertFalse(self.admission["runtimeAdmission"])

    def test_m03_blocks_reflect_the_admission(self) -> None:
        for key in ("m03Contract", "m03LightrigPrototype", "m03ShadowstabPrototype",
                    "m03LightbudgetPrototype", "m03BudgetValidation"):
            with self.subTest(key=key):
                self.assertEqual("BOUNDED_ADMITTED_ANALYSIS_PIPELINE", self.checkpoint[key]["parentM03"])

    def test_agents_and_scope_point_to_current_admission(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        scope = SCOPE.read_text(encoding="utf-8")
        self.assertIn("Current work status | M03/M06/M09 bounded admission", agents)
        self.assertIn("BOUNDED_ADMITTED_ANALYSIS_PIPELINE", agents)
        self.assertIn("Current bounded admission | M03/M06/M09 pipelines", scope)
        self.assertIn("BOUNDED_ADMITTED_ANALYSIS_PIPELINE", scope)
        self.assertIn("NOT_ADMITTED", scope)

    def test_lock_binds_base_scope_and_writer(self) -> None:
        self.assertEqual("51110ff02eb2c542832b6290a98fdc5f979b58a9", self.lock["authorityBaseSha"])
        self.assertEqual(8, self.lock["issue"])
        self.assertEqual(22, len(self.lock["authorityBaseFingerprints"]))
        self.assertEqual("ADMIN_SOLO_SINGLE_WRITER", self.lock["executionMode"])
        allowed = " ".join(self.lock["scope"]["writeAllowedExact"])
        for phrase in ("NEX-ADR-0007", "DECISIONS-LEDGER.md", "AGENTS.md", "SCOPE.md", "CHECKPOINT.json"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, allowed)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, SCOPE, WO))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.admission["audit"])


if __name__ == "__main__":
    unittest.main()

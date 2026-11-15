"""Consistency tests for the M06/M09 bounded admission governance package."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0006-M06-M09-BOUNDED-ADMISSION.md"
LEDGER = REPO / ".engineering" / "DECISIONS-LEDGER.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
AGENTS = REPO / "AGENTS.md"
SCOPE = REPO / ".engineering" / "SCOPE.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-ADMISSION-M06-M09-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-ADMISSION-M06-M09-WO-001-EXECUTION.json"


class M06M09AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.admission = cls.checkpoint["m06M09BoundedAdmission"]
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, LEDGER, CHECKPOINT, AGENTS, SCOPE, WO, LOCK):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_adr_and_ledger_record_the_decision(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        ledger = LEDGER.read_text(encoding="utf-8")
        for phrase in ("BOUNDED_ADMITTED_EVIDENCE_PIPELINE", "M06", "M09", "runtime", "renderer", "NOT_ADMITTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, adr)
        self.assertIn("NEX-D-016", ledger)
        self.assertIn("BOUNDED_ADMITTED_EVIDENCE_PIPELINE", ledger)

    def test_checkpoint_status_and_scope(self) -> None:
        self.assertIn("M06_", self.checkpoint["status"])
        self.assertIn("BOUNDED_ADMITTED", self.checkpoint["status"])
        self.assertEqual(11, self.admission["m06Issue"])
        self.assertEqual(14, self.admission["m09Issue"])
        self.assertEqual("BOUNDED_ADMITTED_EVIDENCE_PIPELINE", self.admission["m06Status"])
        self.assertEqual("BOUNDED_ADMITTED_EVIDENCE_PIPELINE", self.admission["m09Status"])
        self.assertEqual([], self.admission["notAdmitted"])
        excluded = " ".join(self.admission["excludedScope"]).lower()
        for phrase in ("runtime", "hub", "engine", "renderer", "preset application", "fps"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, excluded)
        self.assertFalse(self.admission["ciRelaxation"])
        self.assertFalse(self.admission["runtimeAdmission"])

    def test_agents_and_scope_point_to_current_admission(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        scope = SCOPE.read_text(encoding="utf-8")
        self.assertIn("Current work status |", agents)
        self.assertIn("bounded admission", agents)
        self.assertIn("BOUNDED_ADMITTED_EVIDENCE_PIPELINE", agents)
        self.assertIn("NOT_ADMITTED", agents)
        self.assertIn("Current bounded admission |", scope)
        self.assertIn("BOUNDED_ADMITTED_EVIDENCE_PIPELINE", scope)
        self.assertIn("NOT_ADMITTED", scope)

    def test_lock_binds_base_scope_and_writer(self) -> None:
        self.assertEqual("8ed41bafaf19cff52da9250784f78c3d608ac504", self.lock["authorityBaseSha"])
        self.assertEqual(11, self.lock["issue"])
        self.assertEqual(14, self.lock["secondaryIssue"])
        self.assertEqual(22, len(self.lock["authorityBaseFingerprints"]))
        self.assertEqual("ADMIN_SOLO_SINGLE_WRITER", self.lock["executionMode"])
        allowed = " ".join(self.lock["scope"]["writeAllowedExact"])
        for phrase in ("NEX-ADR-0006", "DECISIONS-LEDGER.md", "AGENTS.md", "SCOPE.md", "CHECKPOINT.json"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, allowed)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in (ADR, SCOPE, WO)
        )
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.admission["audit"])


if __name__ == "__main__":
    unittest.main()

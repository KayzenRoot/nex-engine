"""Consistency tests for the M04/M05 bounded materials/VFX admission."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0009-M04-M05-BOUNDED-ADMISSION.md"
LEDGER = REPO / ".engineering" / "DECISIONS-LEDGER.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
AGENTS = REPO / "AGENTS.md"
SCOPE = REPO / ".engineering" / "SCOPE.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-ADMISSION-M04-M05-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-ADMISSION-M04-M05-WO-001-EXECUTION.json"


class M04M05AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.admission = cls.checkpoint["m04M05BoundedAdmission"]
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, LEDGER, CHECKPOINT, AGENTS, SCOPE, WO, LOCK):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_adr_and_ledger_record_the_decision(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        ledger = LEDGER.read_text(encoding="utf-8")
        for phrase in ("BOUNDED_ADMITTED_MATERIALS_PIPELINE", "BOUNDED_ADMITTED_VFX_PIPELINE",
                       "M04", "M05", "runtime", "renderer", "NOT_ADMITTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, adr)
        self.assertIn("NEX-D-019", ledger)
        self.assertIn("BOUNDED_ADMITTED_MATERIALS_PIPELINE", ledger)
        self.assertIn("BOUNDED_ADMITTED_VFX_PIPELINE", ledger)

    def test_checkpoint_status_and_scope(self) -> None:
        self.assertIn("M04_M05_", self.checkpoint["status"])
        self.assertIn("BOUNDED_ADMITTED", self.checkpoint["status"])
        self.assertEqual(9, self.admission["m04Issue"])
        self.assertEqual(10, self.admission["m05Issue"])
        self.assertEqual("BOUNDED_ADMITTED_MATERIALS_PIPELINE", self.admission["m04Status"])
        self.assertEqual("BOUNDED_ADMITTED_VFX_PIPELINE", self.admission["m05Status"])
        self.assertEqual([], self.admission["notAdmitted"])
        excluded = " ".join(self.admission["excludedScope"]).lower()
        for phrase in ("material", "shader", "texture", "particle", "rendering", "fps"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, excluded)
        self.assertFalse(self.admission["ciRelaxation"])
        self.assertFalse(self.admission["runtimeAdmission"])

    def test_m04_m05_blocks_reflect_the_admission(self) -> None:
        self.assertEqual("BOUNDED_ADMITTED_MATERIALS_PIPELINE",
                         self.checkpoint["m04M05Contracts"]["parentM04"])
        self.assertEqual("BOUNDED_ADMITTED_VFX_PIPELINE",
                         self.checkpoint["m04M05Contracts"]["parentM05"])
        self.assertEqual("BOUNDED_ADMITTED_MATERIALS_PIPELINE",
                         self.checkpoint["m04TexturebudgetPrototype"]["parentM04"])
        self.assertEqual("BOUNDED_ADMITTED_VFX_PIPELINE",
                         self.checkpoint["m05FxbudgetPrototype"]["parentM05"])

    def test_agents_and_scope_point_to_current_admission(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        scope = SCOPE.read_text(encoding="utf-8")
        self.assertIn("Current work status |", agents)
        self.assertIn("BOUNDED_ADMITTED_MATERIALS_PIPELINE", agents)
        self.assertIn("BOUNDED_ADMITTED_VFX_PIPELINE", agents)
        self.assertIn("NOT_ADMITTED", agents)
        self.assertIn("Current bounded admission |", scope)
        self.assertIn("BOUNDED_ADMITTED_MATERIALS_PIPELINE", scope)
        self.assertIn("BOUNDED_ADMITTED_VFX_PIPELINE", scope)
        self.assertIn("NOT_ADMITTED", scope)

    def test_lock_binds_base_scope_and_writer(self) -> None:
        self.assertEqual("5f801c09ca4148fb9712f84cfd638bd80f3a4372", self.lock["authorityBaseSha"])
        self.assertEqual(9, self.lock["issue"])
        self.assertEqual(10, self.lock["secondaryIssue"])
        self.assertEqual(29, len(self.lock["authorityBaseFingerprints"]))
        self.assertEqual("ADMIN_SOLO_SINGLE_WRITER", self.lock["executionMode"])
        allowed = " ".join(self.lock["scope"]["writeAllowedExact"])
        for phrase in ("NEX-ADR-0009", "DECISIONS-LEDGER.md", "AGENTS.md", "SCOPE.md", "CHECKPOINT.json"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, allowed)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, SCOPE, WO))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.admission["audit"])


if __name__ == "__main__":
    unittest.main()

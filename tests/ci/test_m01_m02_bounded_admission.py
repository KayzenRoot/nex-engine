"""Consistency tests for the M01/M02 bounded reference admission."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0008-M01-M02-BOUNDED-ADMISSION.md"
LEDGER = REPO / ".engineering" / "DECISIONS-LEDGER.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
AGENTS = REPO / "AGENTS.md"
SCOPE = REPO / ".engineering" / "SCOPE.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-ADMISSION-M01-M02-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-ADMISSION-M01-M02-WO-001-EXECUTION.json"


class M01M02AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.admission = cls.checkpoint["m01M02BoundedAdmission"]
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, LEDGER, CHECKPOINT, AGENTS, SCOPE, WO, LOCK):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_adr_and_ledger_record_the_decision(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        ledger = LEDGER.read_text(encoding="utf-8")
        for phrase in ("BOUNDED_ADMITTED_REFERENCE_PIPELINE", "M01", "M02", "runtime", "renderer", "NOT_ADMITTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, adr)
        self.assertIn("NEX-D-018", ledger)
        self.assertIn("BOUNDED_ADMITTED_REFERENCE_PIPELINE", ledger)

    def test_checkpoint_status_and_scope(self) -> None:
        self.assertIn("M01_M02_M03_M06_M09_BOUNDED_ADMITTED", self.checkpoint["status"])
        self.assertEqual(6, self.admission["m01Issue"])
        self.assertEqual(7, self.admission["m02Issue"])
        self.assertEqual("BOUNDED_ADMITTED_REFERENCE_PIPELINE", self.admission["m01Status"])
        self.assertEqual("BOUNDED_ADMITTED_REFERENCE_PIPELINE", self.admission["m02Status"])
        self.assertEqual(["M04", "M05", "M07", "M08", "M10", "M11", "M12"], self.admission["notAdmitted"])
        excluded = " ".join(self.admission["excludedScope"]).lower()
        for phrase in ("runtime", "renderer", "shaders", "render2d", "fps"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, excluded)
        self.assertFalse(self.admission["ciRelaxation"])
        self.assertFalse(self.admission["runtimeAdmission"])

    def test_m01_m02_blocks_reflect_the_admission(self) -> None:
        for key in ("s02Admission", "s04Admission", "s07AuditPack"):
            with self.subTest(key=key):
                self.assertEqual("BOUNDED_ADMITTED_REFERENCE_PIPELINE", self.checkpoint[key]["parentM01"])
        for key in ("m02s01Prototype", "m02s02Prototype", "m02s03Prototype", "m02s04Prototype",
                    "m02s05Prototype", "m02s06Research", "m02s07Qa"):
            with self.subTest(key=key):
                self.assertEqual("BOUNDED_ADMITTED_REFERENCE_PIPELINE", self.checkpoint[key]["parentM02"])

    def test_agents_and_scope_point_to_current_admission(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        scope = SCOPE.read_text(encoding="utf-8")
        self.assertIn("Current work status |", agents)
        self.assertIn("BOUNDED_ADMITTED_REFERENCE_PIPELINE", agents)
        self.assertIn("NOT_ADMITTED", agents)
        self.assertIn("Current bounded admission |", scope)
        self.assertIn("BOUNDED_ADMITTED_REFERENCE_PIPELINE", scope)
        self.assertIn("NOT_ADMITTED", scope)

    def test_lock_binds_base_scope_and_writer(self) -> None:
        self.assertEqual("e729774583eb8ce3b75271aea66589bb9e04a587", self.lock["authorityBaseSha"])
        self.assertEqual(6, self.lock["issue"])
        self.assertEqual(7, self.lock["secondaryIssue"])
        self.assertEqual(22, len(self.lock["authorityBaseFingerprints"]))
        self.assertEqual("ADMIN_SOLO_SINGLE_WRITER", self.lock["executionMode"])
        allowed = " ".join(self.lock["scope"]["writeAllowedExact"])
        for phrase in ("NEX-ADR-0008", "DECISIONS-LEDGER.md", "AGENTS.md", "SCOPE.md", "CHECKPOINT.json"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, allowed)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, SCOPE, WO))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.admission["audit"])


if __name__ == "__main__":
    unittest.main()

"""Consistency tests for the M07/M08/M10/M11/M12 bounded admission."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0010-M07-M12-BOUNDED-ADMISSION.md"
LEDGER = REPO / ".engineering" / "DECISIONS-LEDGER.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
AGENTS = REPO / "AGENTS.md"
SCOPE = REPO / ".engineering" / "SCOPE.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-ADMISSION-M07-M08-M10-M11-M12-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-ADMISSION-M07-M08-M10-M11-M12-WO-001-EXECUTION.json"
STATUSES = {
    "M07": "BOUNDED_ADMITTED_RENDER2D_PIPELINE",
    "M08": "BOUNDED_ADMITTED_COMPOSITION_PIPELINE",
    "M10": "BOUNDED_ADMITTED_ANIMATION_PIPELINE",
    "M11": "BOUNDED_ADMITTED_ASSET_PIPELINE",
    "M12": "BOUNDED_ADMITTED_IDENTITY_PIPELINE",
}


class M07M12AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.admission = cls.checkpoint["m07M08M10M11M12BoundedAdmission"]
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, LEDGER, CHECKPOINT, AGENTS, SCOPE, WO, LOCK):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_adr_and_ledger_record_the_decision(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        ledger = LEDGER.read_text(encoding="utf-8")
        for phrase in ("M07", "M08", "M10", "M11", "M12", "runtime", "renderer", "NOT_ADMITTED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, adr)
        for status in STATUSES.values():
            with self.subTest(status=status):
                self.assertIn(status, adr)
                self.assertIn(status, ledger)
        self.assertIn("NEX-D-020", ledger)

    def test_checkpoint_status_and_scope(self) -> None:
        self.assertIn("ALL_PARENTS_BOUNDED_ADMITTED", self.checkpoint["status"])
        self.assertIn("BOUNDED_ADMITTED", self.checkpoint["status"])
        self.assertEqual(STATUSES, self.admission["statuses"])
        self.assertEqual([], self.admission["notAdmitted"])
        excluded = " ".join(self.admission["excludedScope"]).lower()
        for phrase in ("runtime", "renderer", "asset", "brand", "performance"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, excluded)
        self.assertFalse(self.admission["ciRelaxation"])
        self.assertFalse(self.admission["runtimeAdmission"])

    def test_parent_blocks_reflect_the_admission(self) -> None:
        expected = {
            "m07s01Prototype": ("parentM07", STATUSES["M07"]),
            "m08Contract": ("parentM08", STATUSES["M08"]),
            "m08CompositionPrototype": ("parentM08", STATUSES["M08"]),
            "m10Contract": ("parentM10", STATUSES["M10"]),
            "m10FeedbackPrototype": ("parentM10", STATUSES["M10"]),
            "m11Contract": ("parentM11", STATUSES["M11"]),
            "m11AuditPrototype": ("parentM11", STATUSES["M11"]),
            "m12Contract": ("parentM12", STATUSES["M12"]),
            "m12ValidatorPrototype": ("parentM12", STATUSES["M12"]),
        }
        for block, (key, value) in expected.items():
            with self.subTest(block=block):
                self.assertEqual(value, self.checkpoint[block][key])

    def test_agents_and_scope_point_to_current_admission(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        scope = SCOPE.read_text(encoding="utf-8")
        for text in (agents, scope):
            self.assertIn("NOT_ADMITTED", text)
            for status in STATUSES.values():
                with self.subTest(status=status):
                    self.assertIn(status, text)
        self.assertIn("Current work status |", agents)
        self.assertIn("Current bounded admission |", scope)

    def test_lock_binds_base_scope_and_writer(self) -> None:
        self.assertEqual("8bb4bef1b216e71eafe0dc83efe897bb926530ce", self.lock["authorityBaseSha"])
        self.assertEqual([12, 13, 15, 16, 17], self.lock["issues"])
        self.assertEqual(49, len(self.lock["authorityBaseFingerprints"]))
        self.assertEqual("ADMIN_SOLO_SINGLE_WRITER", self.lock["executionMode"])
        allowed = " ".join(self.lock["scope"]["writeAllowedExact"])
        for phrase in ("NEX-ADR-0010", "DECISIONS-LEDGER.md", "AGENTS.md", "SCOPE.md", "CHECKPOINT.json"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, allowed)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, SCOPE, WO))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.admission["audit"])


if __name__ == "__main__":
    unittest.main()

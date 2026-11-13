"""Acceptance tests for the NEX M02-S07 QA ledger and regression pack."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m02"
CONTRACT = PACK / "qa-contract.v1.json"
LEDGER = PACK / "qa-ledger.v1.json"
TOOL_PATH = PACK / "tools" / "qa_ledger.py"
REGRESSION = PACK / "REGRESSION-REPORT.md"
QUALITY = PACK / "QUALITY-LEDGER.md"
INTERFACE = PACK / "INTERFACE-M03-M06.md"
README = PACK / "README.md"


def _load_tool():
    spec = importlib.util.spec_from_file_location("m02_qa_ledger", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load qa_ledger.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOL = _load_tool()


class QaContractTests(unittest.TestCase):
    def test_contract_defines_statuses_rules_and_interface(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual("nex_m02_qa_contract.v1", contract["schema_version"])
        self.assertEqual("PROPOSED_NOT_PROMOTED", contract["status"])
        self.assertEqual(["corridor_static", "arena_combat", "dense_city"], contract["scenes"])
        self.assertIn("PASS", contract["statuses"])
        self.assertIn("INCONCLUSIVE_NOT_RUN", contract["statuses"])
        rules = " ".join(contract["rules"]).lower()
        self.assertIn("pass requires", rules)
        self.assertIn("missing scene or performance measurement is inconclusive_not_run", rules)
        self.assertIn("headless ci", rules)
        self.assertEqual("ASPIRATIONAL_NOT_MEASURED", contract["targets"]["quality_1080p60"])
        self.assertEqual("EXPERIMENTAL_NOT_MEASURED", contract["targets"]["performance_120"])
        for consumer in ("M03_lighting", "M04_materials", "M05_vfx", "M06_optimization"):
            self.assertIn(consumer, contract["interface"])


class QaLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_ledger_is_reproducible_and_valid(self):
        self.assertEqual([], TOOL.check(self.ledger))
        self.assertEqual(TOOL.build(), self.ledger)
        self.assertEqual(6, len(self.ledger["components"]))
        self.assertEqual(["corridor_static", "arena_combat", "dense_city"], self.ledger["scenes"])

    def test_components_are_structural_pass_but_not_scene_pass(self):
        for component in self.ledger["components"]:
            with self.subTest(id=component["id"]):
                self.assertEqual("PASS", component["structural_status"])
                self.assertIn(component["scene_comparison"],
                              {"INCONCLUSIVE_NOT_RUN", "NOT_APPLICABLE_RESEARCH"})
                self.assertIn(component["performance"],
                              {"INCONCLUSIVE_NOT_RUN", "NOT_APPLICABLE_RESEARCH"})
                for evidence in component["evidence"]:
                    self.assertEqual(64, len(evidence["sha256"]))

    def test_claims_defects_and_integration_are_conservative(self):
        self.assertFalse(any(self.ledger["claims"].values()))
        self.assertEqual({"high": 0, "critical": 0}, self.ledger["defects"])
        self.assertEqual("SERIAL_STEWARD", self.ledger["integration"]["mode"])
        self.assertEqual(0, self.ledger["integration"]["conflicts"])
        self.assertEqual("ASPIRATIONAL_NOT_MEASURED", self.ledger["targets"]["quality_1080p60"])
        self.assertEqual("EXPERIMENTAL_NOT_MEASURED", self.ledger["targets"]["performance_120"])

    def test_evidence_hashes_match_files(self):
        for component in self.ledger["components"]:
            for evidence in component["evidence"]:
                with self.subTest(path=evidence["path"]):
                    self.assertEqual(TOOL.staged_sha(evidence["path"])[0], evidence["sha256"])

    def test_scene_pass_without_evidence_is_rejected(self):
        tampered = json.loads(json.dumps(self.ledger))
        tampered["components"][0]["scene_comparison"] = "PASS"
        self.assertTrue(any("scene PASS without scene_evidence" in error for error in TOOL.validate(tampered)))

    def test_measured_performance_without_evidence_is_rejected(self):
        tampered = json.loads(json.dumps(self.ledger))
        tampered["components"][0]["performance"] = "MEASURED"
        self.assertTrue(any("measured performance without performance_evidence" in error for error in TOOL.validate(tampered)))

    def test_measured_claim_high_defect_and_conflict_are_rejected(self):
        for mutate, expected in (
            (lambda ledger: ledger["claims"].__setitem__("measured_gain", True), "claims must be false"),
            (lambda ledger: ledger["defects"].__setitem__("high", 1), "HIGH/CRITICAL defects"),
            (lambda ledger: ledger["integration"].__setitem__("conflicts", 1), "integration conflicts"),
        ):
            tampered = json.loads(json.dumps(self.ledger))
            mutate(tampered)
            self.assertTrue(any(expected in error for error in TOOL.validate(tampered)))

    def test_evidence_tampering_is_detected(self):
        tampered = json.loads(json.dumps(self.ledger))
        tampered["components"][0]["evidence"][0]["sha256"] = "0" * 64
        self.assertTrue(any("digests diverged" in error for error in TOOL.check(tampered)))


class QaDocumentTests(unittest.TestCase):
    def test_regression_report_covers_every_component(self):
        text = REGRESSION.read_text(encoding="utf-8")
        for identifier in ("S01", "S02", "S03", "S04", "S05", "S06"):
            with self.subTest(id=identifier):
                self.assertIn(identifier, text)
        self.assertIn("INCONCLUSIVE_NOT_RUN", text)
        self.assertIn("No frame-time number is claimed", text)

    def test_quality_ledger_has_no_measured_gain(self):
        text = QUALITY.read_text(encoding="utf-8").lower()
        self.assertIn("no fps", text)
        self.assertIn("structural pass", text)
        for forbidden in ("fps improved", "performance gain measured", "visual gain measured"):
            self.assertNotIn(forbidden, text)

    def test_interface_covers_all_consumers(self):
        text = INTERFACE.read_text(encoding="utf-8")
        for consumer in ("M03", "M04", "M05", "M06"):
            with self.subTest(consumer=consumer):
                self.assertIn(consumer, text)
        self.assertIn("DRAFTS", text.upper())

    def test_readme_states_inconclusive_scene_and_performance(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("INCONCLUSIVE_NOT_RUN", text)
        self.assertIn("No checkpoint is promoted", text)


if __name__ == "__main__":
    unittest.main()

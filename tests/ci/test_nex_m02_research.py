"""Acceptance tests for the NEX M02-S06 R&D decision atlas."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESEARCH = REPO / "docs" / "research" / "nex-m02"
HYPOTHESES = RESEARCH / "hypotheses.v1.json"
ENGINE_PATH = RESEARCH / "tools" / "decision_engine.py"
ATLAS = RESEARCH / "DECISION-ATLAS.md"
CONTRACTS = RESEARCH / "proposed-contracts.md"
README = RESEARCH / "README.md"


def _load_engine():
    spec = importlib.util.spec_from_file_location("m02_decision_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load decision engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ENGINE = _load_engine()


def _hypothesis(**overrides):
    base = {
        "id": "SYNTH", "name": "Synthetic", "kind": "render_feature",
        "owner_module": "M02", "touches_modules": ["M02"],
        "question": "Does it work?", "native_gap": "MEASURED",
        "redundant_with_native": False, "simplest_alternative": "none",
        "data_contract": "state", "cost": {"cpu": "LOW", "gpu": "LOW", "vram": "NONE", "maintenance": "LOW"},
        "visual_risk": "LOW", "license_risk": "NONE", "compatibility_2_5d": "COMPATIBLE",
        "rollback": "disable", "benchmark": {"a": "A", "b": "B", "a2": "A", "plan": "A/B/A"},
        "metrics": ["m"], "evidence_status": "MEASURED",
        "sources": ["https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html"],
        "owner_decision": "PENDING", "recommended": "GO",
    }
    base.update(overrides)
    return base


class ResearchDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(HYPOTHESES.read_text(encoding="utf-8"))

    def test_document_validates_and_recommendations_match_engine(self):
        self.assertEqual([], ENGINE.check(self.document))
        results = {entry["id"]: entry["decision"] for entry in ENGINE.evaluate(self.document)}
        self.assertEqual(5, len(results))
        for hypothesis in self.document["hypotheses"]:
            self.assertEqual(hypothesis["recommended"], results[hypothesis["id"]])

    def test_five_refutable_hypotheses_with_sources_and_ab_a(self):
        hypotheses = self.document["hypotheses"]
        self.assertEqual(5, len(hypotheses))
        self.assertEqual(len(hypotheses), len({item["id"] for item in hypotheses}))
        for hypothesis in hypotheses:
            with self.subTest(id=hypothesis["id"]):
                self.assertTrue(hypothesis["question"].endswith("?"))
                self.assertTrue(hypothesis["sources"][0].startswith("https://docs.godotengine.org/"))
                self.assertEqual("PENDING", hypothesis["owner_decision"])
                self.assertIn("plan", hypothesis["benchmark"])
                self.assertIn(hypothesis["owner_module"], hypothesis["touches_modules"])
                self.assertIn(hypothesis["compatibility_2_5d"], {"COMPATIBLE", "CONFLICTS", "UNKNOWN"})

    def test_no_render_feature_claims_measurement(self):
        for hypothesis in self.document["hypotheses"]:
            if hypothesis["kind"] == "render_feature":
                with self.subTest(id=hypothesis["id"]):
                    self.assertEqual("NOT_MEASURED", hypothesis["evidence_status"])
            else:
                self.assertEqual("PROTOTYPE_VERIFIED", hypothesis["evidence_status"])
        serialized = json.dumps(self.document).lower()
        for forbidden in ('"gain_ms"', '"fps_improvement"', '"measured_value"'):
            self.assertNotIn(forbidden, serialized)

    def test_redundancies_are_rejected(self):
        rejected = self.document["rejected_redundancies"]
        self.assertGreaterEqual(len(rejected), 5)
        names = {entry["name"] for entry in rejected}
        self.assertIn("Custom mesh LOD", names)
        self.assertIn("Custom occlusion culling", names)
        self.assertIn("Custom TAA/upscaler", names)
        self.assertIn("Global z-depth hack", names)
        self.assertIn("GPU-driven core C++ patch", names)
        for entry in rejected:
            with self.subTest(id=entry["id"]):
                self.assertEqual("NO_GO", entry["decision"])
                self.assertTrue(entry["source"].startswith("https://docs.godotengine.org/"))


class ResearchArtifactTests(unittest.TestCase):
    def test_atlas_matches_document(self):
        document = json.loads(HYPOTHESES.read_text(encoding="utf-8"))
        atlas = ATLAS.read_text(encoding="utf-8")
        for hypothesis in document["hypotheses"]:
            with self.subTest(id=hypothesis["id"]):
                self.assertIn(hypothesis["id"], atlas)
                self.assertIn(hypothesis["recommended"], atlas)
        for entry in document["rejected_redundancies"]:
            self.assertIn(entry["id"], atlas)
        self.assertIn("PENDING", atlas)

    def test_contracts_are_drafts(self):
        text = CONTRACTS.read_text(encoding="utf-8")
        self.assertIn("DRAFT_NOT_PROMOTED", text)
        for contract in ("C1", "C2", "C3", "C4"):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_no_patent_or_implementation_claim(self):
        for path in (README, ATLAS, CONTRACTS):
            with self.subTest(path=path.name):
                self.assertNotIn("patentable", path.read_text(encoding="utf-8").lower())
        readme = README.read_text(encoding="utf-8").lower()
        self.assertIn("no implementation", readme)


class DecisionEngineRuleTests(unittest.TestCase):
    def test_native_gap_none_is_no_go(self):
        decision, reason = ENGINE.recommend(_hypothesis(native_gap="NONE"))
        self.assertEqual(("NO_GO", "NATIVE_SUFFICIENT"), (decision, reason))

    def test_redundant_is_no_go(self):
        self.assertEqual("NO_GO", ENGINE.recommend(_hypothesis(redundant_with_native=True))[0])

    def test_unmeasured_feature_is_research_more(self):
        self.assertEqual(("RESEARCH_MORE", "EVIDENCE_NOT_MEASURED"),
                         ENGINE.recommend(_hypothesis(evidence_status="NOT_MEASURED")))

    def test_measured_high_risk_is_no_go(self):
        self.assertEqual("NO_GO", ENGINE.recommend(_hypothesis(visual_risk="HIGH"))[0])

    def test_measured_missing_rollback_is_no_go(self):
        self.assertEqual("NO_GO", ENGINE.recommend(_hypothesis(rollback=""))[0])

    def test_measured_with_simple_alternative_is_research_more(self):
        self.assertEqual(("RESEARCH_MORE", "SIMPLER_ALTERNATIVE_FIRST"),
                         ENGINE.recommend(_hypothesis(simplest_alternative="config")))

    def test_measured_gap_with_rollback_is_go(self):
        self.assertEqual(("GO", "MEASURED_GAP_ROLLBACK_READY"), ENGINE.recommend(_hypothesis()))

    def test_process_tool_rules(self):
        self.assertEqual("GO", ENGINE.recommend(_hypothesis(kind="process_tool", evidence_status="PROTOTYPE_VERIFIED"))[0])
        self.assertEqual("RESEARCH_MORE",
                         ENGINE.recommend(_hypothesis(kind="process_tool", evidence_status="NOT_MEASURED"))[0])

    def test_evaluation_is_deterministic(self):
        document = json.loads(HYPOTHESES.read_text(encoding="utf-8"))
        first = ENGINE.evaluate(document)
        second = ENGINE.evaluate(document)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

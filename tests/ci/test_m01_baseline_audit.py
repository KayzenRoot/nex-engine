"""Audit tests for the NEX M01 baseline pack (NEX-M01-S07-WO-001)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m01"
MANIFEST = PACK / "manifest.json"
HEX_SHA = re.compile(r"^[0-9a-f]{64}$")


def _load_builder():
    spec = importlib.util.spec_from_file_location("m01_manifest_builder", PACK / "tools" / "build_manifest.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load build_manifest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = _load_builder()


class BaselineManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_identity_and_no_completion_claims(self) -> None:
        self.assertEqual("nex_m01_baseline_manifest.v1", self.manifest["schema_version"])
        self.assertEqual("FROZEN_PROPOSED", self.manifest["status"])
        self.assertEqual("871fd1bc89c272ba04327ddc81e407d35ff5fee0", self.manifest["base_sha"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", self.manifest["audit"])
        for key, value in self.manifest["claims"].items():
            with self.subTest(claim=key):
                self.assertFalse(value, f"claim {key} must be false in the frozen proposal")

    def test_every_artifact_hash_is_recorded_and_well_formed(self) -> None:
        artifacts = self.manifest["artifacts"]
        self.assertGreaterEqual(len(artifacts), 60)
        self.assertEqual(len(artifacts), len({entry["path"] for entry in artifacts}))
        kinds = {entry["kind"] for entry in artifacts}
        for required in ("s04-run", "s04-validation", "s05-run", "s05-validation", "contract", "budget"):
            self.assertIn(required, kinds)
        for entry in artifacts:
            with self.subTest(path=entry["path"]):
                self.assertRegex(entry["sha256"], HEX_SHA)
                self.assertGreater(entry["bytes"], 0)
                self.assertNotEqual("docs/benchmarks/m01/manifest.json", entry["path"])

    def test_manifest_is_reproducible_from_the_git_index(self) -> None:
        fresh = BUILDER.build(self.manifest["head_sha_at_manifest_generation"])
        self.assertEqual(fresh["artifacts"], self.manifest["artifacts"])

    def test_committed_blob_hashes_match_the_manifest(self) -> None:
        for entry in self.manifest["artifacts"]:
            with self.subTest(path=entry["path"]):
                content = BUILDER.staged_blob(entry["path"])
                self.assertEqual(entry["sha256"], hashlib.sha256(content).hexdigest())

    def test_matrices_match_the_evidence(self) -> None:
        matrices = self.manifest["matrices"]
        self.assertEqual("12_OF_12_COMPLETE", matrices["s04"]["status"])
        self.assertEqual(["1791933080-760888025"], matrices["s04"]["invalid_runs"])
        self.assertEqual("invalid_monotonic_tick", matrices["s04"]["invalid_reason"])
        self.assertEqual("15_OF_15_COMPLETE", matrices["s05"]["status"])
        self.assertEqual(3, matrices["s05"]["baseline_repetitions"])


class BaselineBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.budget = json.loads((PACK / "budget.v1.json").read_text(encoding="utf-8"))

    def test_budget_is_proposed_and_non_authorizing(self) -> None:
        self.assertEqual("PROPOSED_PENDING_OWNER_APPROVAL", self.budget["status"])
        self.assertFalse(self.budget["claims"]["targets_achieved"])
        self.assertFalse(self.budget["claims"]["gpu_benchmark_claim"])
        self.assertEqual("OWNER", self.budget["approval"]["required"])

    def test_ceilings_exceed_measured_baselines(self) -> None:
        for ceiling in self.budget["ceilings"]:
            with self.subTest(id=ceiling["id"]):
                if "measured" in ceiling:
                    self.assertGreater(ceiling["ceiling"], ceiling["measured"])
                if "measured_max" in ceiling:
                    self.assertGreaterEqual(ceiling["ceiling"], ceiling["measured_max"])
                if "measured_min" in ceiling:
                    self.assertLessEqual(ceiling["floor"], ceiling["measured_min"])

    def test_targets_are_aspirational(self) -> None:
        self.assertEqual(2, len(self.budget["targets"]))
        for target in self.budget["targets"]:
            with self.subTest(target=target["id"]):
                self.assertEqual("ASPIRATIONAL_NOT_MEASURED", target["status"])


class BaselineDocumentTests(unittest.TestCase):
    def test_required_documents_exist(self) -> None:
        for name in ("README.md", "BASELINE.md", "PERFORMANCE-BUDGET.md", "RISKS.md", "DEVIATIONS.md",
                     "CI_LINKS.md", "research.md", "manifest.json"):
            with self.subTest(name=name):
                self.assertTrue((PACK / name).is_file())

    def test_baseline_disclaims_engine_completion(self) -> None:
        text = (PACK / "BASELINE.md").read_text(encoding="utf-8").lower()
        self.assertIn("conclusão do engine", text)
        self.assertIn("não", text)
        self.assertIn("aspiracionais", text)

    def test_ci_links_reference_the_integrations(self) -> None:
        text = (PACK / "CI_LINKS.md").read_text(encoding="utf-8")
        for expected in ("#107", "#112", "#120", "#122", "4d69b7bd", "871fd1bc"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()

"""Acceptance tests for the M01 full reference-lab gate."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m01"
GOLDEN = PACK / "golden-matrix.v1.json"
BUDGET = PACK / "final-budget.v1.json"
GATE = PACK / "M01-FINAL-GATE.md"
LICENSE = PACK / "LICENSE-AUDIT.md"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0012-M01-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M01-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M01-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
GOLDEN_DIR = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m01-golden"
PERF_DIR = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m01-perf-1080"


class M01FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        cls.budget = json.loads(BUDGET.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, GOLDEN, BUDGET, GATE, LICENSE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_golden_matrix_is_deterministic_and_complete(self) -> None:
        self.assertEqual("m01_golden_matrix.v1", self.golden["schema_version"])
        self.assertEqual(18, self.golden["runs"])
        self.assertEqual([1920, 1080], self.golden["viewport_px"])
        self.assertEqual(3, len(self.golden["scenes"]))
        for scene in self.golden["scenes"]:
            with self.subTest(scene=scene["scene_id"]):
                self.assertTrue(scene["aa"]["identical_sha"])
                image = GOLDEN_DIR / scene["acceptance_image"]["file"]
                self.assertTrue(image.is_file())
                self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),
                                 scene["acceptance_image"]["sha256"])
                self.assertGreater(scene["ab"]["metrics"]["changed_pixels_pct"], 0.0)
                self.assertEqual(6, len(scene["regions"]))
        self.assertEqual("ORIGINAL_NEX_GENERATED_NO_THIRD_PARTY_ASSETS", self.golden["license"]["status"])

    def test_performance_budget_passes_and_is_owner_approved(self) -> None:
        self.assertEqual("m01_final_performance_budget.v1", self.budget["schema_version"])
        self.assertEqual(9, self.budget["runs"])
        self.assertEqual("OWNER_APPROVED", self.budget["ownerDecision"]["status"])
        self.assertEqual(3, len(self.budget["scenes"]))
        for scene in self.budget["scenes"]:
            with self.subTest(scene=scene["scene_id"]):
                self.assertTrue(all(scene["checks"].values()))
                self.assertLessEqual(scene["gpu_p95_ms"], 1.0)
                self.assertLessEqual(scene["cpu_p95_ms"], 2.0)
                self.assertLessEqual(scene["pacing_p95_ms"], 16.67)
                self.assertGreaterEqual(scene["one_percent_low_fps"], 60.0)
        self.assertEqual({"MET_ON_REFERENCE_WORKLOAD"},
                         {target["status"] for target in self.budget["targets"]})

    def test_evidence_directories_are_complete(self) -> None:
        self.assertEqual(18, len(list(GOLDEN_DIR.glob("*.png"))))
        captures = [path for path in PERF_DIR.glob("gpu_profile_*.json") if not path.name.endswith(".validation.json")]
        self.assertEqual(9, len(captures))
        self.assertEqual(9, len(list(PERF_DIR.glob("*.validation.json"))))
        self.assertTrue((GOLDEN_DIR / "SHA256SUMS.txt").is_file())
        self.assertTrue((PERF_DIR / "SHA256SUMS.txt").is_file())

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m01FinalReference"]
        self.assertEqual("NEX-M01-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([6, 21, 23, 27], block["issues"])
        self.assertEqual("OWNER_APPROVED", block["budget"]["status"])
        self.assertEqual("M01_REFERENCE_LAB_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builders_are_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m01/tools/build_golden_matrix.py --check", workflow)
        self.assertIn("docs/benchmarks/m01/tools/build_performance_budget.py --check", workflow)

    def test_gate_covers_the_closed_issues(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("S01", "S03", "S07", "#21", "#23", "#27", "#6", "M01_REFERENCE_LAB_COMPLETE"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertIn("não é uma promessa de 60/120 FPS em jogo", text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

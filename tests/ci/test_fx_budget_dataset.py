"""Structural and reproducibility tests for the NEX M05 FX budget dataset."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "vfx" / "fxbudget"
DATASET = MODULE / "dataset.gd"
EVIDENCE = MODULE / "evidence" / "fx-budget-dataset-2026-11-15.json"
REPORT = REPO / "docs" / "benchmarks" / "m05" / "fx-budget-dataset.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m05" / "FX-BUDGET-DATASET.md"
TOOL = REPO / "docs" / "benchmarks" / "m05" / "tools" / "build_fx_budget_dataset.py"


class FxBudgetDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.archetypes = {entry["archetype_id"]: entry for entry in cls.evidence["archetypes"]}

    def test_evidence_covers_three_archetypes(self) -> None:
        self.assertEqual("fx_budget_dataset.v1", self.evidence["schema_version"])
        self.assertEqual(["skirmish", "elite", "boss"],
                         [entry["archetype_id"] for entry in self.evidence["archetypes"]])
        self.assertEqual("99437b22e94a6494eaef801872bb8fd0c79c0f1a", self.evidence["source_sha"])
        self.assertEqual(3, len(self.evidence["limitations"]))

    def test_verdicts_exercise_fit_tight_and_over_budget(self) -> None:
        expected = {"skirmish": ("FIT", 484), "elite": ("TIGHT", 1047), "boss": ("OVER_BUDGET", 2753)}
        for archetype_id, (verdict, particles) in expected.items():
            with self.subTest(id=archetype_id):
                report = self.archetypes[archetype_id]["report"]
                self.assertEqual(verdict, report["verdict"])
                self.assertEqual(particles, report["totals"]["particles"])
        self.assertIn("tight_particles", [item["code"] for item in self.archetypes["elite"]["report"]["findings"]])
        self.assertIn("over_particles", [item["code"] for item in self.archetypes["boss"]["report"]["findings"]])

    def test_boss_reduction_plan_is_deterministic(self) -> None:
        plan = self.archetypes["boss"]["report"]["reduction_plan"]["particles"]
        self.assertEqual(3, plan["steps_count"])
        self.assertEqual(1834, plan["projected_particles"])
        self.assertEqual(["meteor-burst", "lance-burst", "meteor-charge"],
                         [step["emitter_id"] for step in plan["steps"]])

    def test_builder_reproduces_committed_outputs(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("M05_FX_BUDGET_DATASET_CHECK_PASS: 3 runs", result.stdout)

    def test_report_matches_evidence(self) -> None:
        self.assertEqual("m05_fx_budget_dataset.v1", self.report["schema_version"])
        self.assertEqual("BUDGET_PLANNING_DERIVED", self.report["verdict"])
        self.assertEqual(3, self.report["runs"])
        self.assertEqual(["skirmish", "elite", "boss"],
                         [entry["archetype_id"] for entry in self.report["archetypes"]])
        self.assertEqual({"FIT", "TIGHT", "OVER_BUDGET"},
                         {entry["verdict"] for entry in self.report["archetypes"]})
        self.assertEqual(64, len(self.report["evidence_sha256"]))

    def test_dataset_is_data_only(self) -> None:
        source = DATASET.read_text(encoding="utf-8")
        for forbidden in ("GPUParticles", "CPUParticles", "RenderingServer", "ParticleProcessMaterial"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn("fx_budget_planner.gd", source)

    def test_report_makes_no_performance_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        for forbidden in ("fps improved", "performance gain", "quality verified", "rendered benchmark"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)
        self.assertIn("não é benchmark de hardware", lowered)


if __name__ == "__main__":
    unittest.main()

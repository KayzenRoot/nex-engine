"""Structural and reproducibility tests for the M10 archetype feedback dataset."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "animation" / "combat_feedback"
SCRIPT = MODULE / "archetype_feedback.gd"
EVIDENCE = MODULE / "evidence" / "archetype-feedback-2026-11-15.json"
DATASET = REPO / "nex_modules" / "vfx" / "fxbudget" / "evidence" / "fx-budget-dataset-2026-11-15.json"
REPORT = REPO / "docs" / "benchmarks" / "m10" / "archetype-feedback.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m10" / "ARCHETYPE-FEEDBACK.md"
TOOL = REPO / "docs" / "benchmarks" / "m10" / "tools" / "build_archetype_feedback.py"


class ArchetypeFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.archetypes = {entry["archetype_id"]: entry for entry in cls.evidence["archetypes"]}

    def test_evidence_binds_the_m05_dataset(self) -> None:
        self.assertEqual("m10_archetype_feedback_run.v1", self.evidence["schema_version"])
        self.assertEqual("91e6c15794662b3502244c2d03879b8dbb9980dd", self.evidence["source_sha"])
        self.assertEqual(hashlib.sha256(DATASET.read_bytes()).hexdigest(), self.evidence["dataset_sha256"])
        self.assertEqual(["skirmish", "elite", "boss"],
                         [entry["archetype_id"] for entry in self.evidence["archetypes"]])

    def test_every_spell_plan_is_safe_and_conflict_free(self) -> None:
        expected = {"skirmish": (2, 10, 40), "elite": (3, 15, 60), "boss": (5, 25, 100)}
        for archetype_id, (spells, channels, hit_stop) in expected.items():
            with self.subTest(id=archetype_id):
                summary = self.archetypes[archetype_id]["summary"]
                self.assertEqual(spells, summary["spells"])
                self.assertEqual(channels, summary["total_channels"])
                self.assertEqual(hit_stop, summary["total_hit_stop_ms"])
                self.assertEqual(5, summary["max_peak_concurrency"])
                self.assertEqual({"high": 0, "medium": 0, "low": 0, "info": 0}, summary["conflicts"])
                self.assertEqual({"SAFE_CONFIG_HEURISTIC"}, set(summary["verdicts"]))

    def test_damage_mapping_is_deterministic(self) -> None:
        damage = {plan["spell_id"]: plan["damage"] for plan in self.archetypes["boss"]["spells"]}
        self.assertEqual({"ember-bolt": 32, "frost-nova": 64, "storm-lance": 128,
                          "meteor-storm": 225, "grave-bind": 75}, damage)
        critical = {plan["spell_id"]: plan["critical"] for plan in self.archetypes["boss"]["spells"]}
        self.assertEqual({"storm-lance", "meteor-storm"},
                         {spell_id for spell_id, value in critical.items() if value})

    def test_builder_reproduces_committed_outputs(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("M10_ARCHETYPE_FEEDBACK_CHECK_PASS: 3 runs", result.stdout)

    def test_report_matches_evidence(self) -> None:
        self.assertEqual("m10_archetype_feedback.v1", self.report["schema_version"])
        self.assertEqual("FEEDBACK_PLANNING_DERIVED", self.report["verdict"])
        self.assertEqual(3, self.report["runs"])
        self.assertEqual(25, self.report["archetypes"][2]["summary"]["total_channels"])
        self.assertEqual(self.evidence["dataset_sha256"], self.report["dataset_sha256"])
        self.assertEqual(64, len(self.report["evidence_sha256"]))

    def test_script_is_planning_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("AnimationPlayer", "Camera3D", "RenderingServer", "ShaderMaterial", "GPUParticles"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn("feedback_planner.gd", source)

    def test_no_game_feel_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        for forbidden in ("game feel improved", "game-feel verified", "fps improved", "quality verified"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()

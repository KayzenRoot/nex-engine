"""Acceptance tests for the M03 cinematic-lighting reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m03"
RUNTIME = PACK / "lighting-runtime.v1.json"
GATE = PACK / "M03-FINAL-GATE.md"
BRIDGE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m03-bridge" / "bridge-smoke-2026-11-15.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0014-M03-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M03-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M03-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"


class M03FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, GATE, BRIDGE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_three_looks_cover_three_scenes(self) -> None:
        looks = self.runtime["s01"]["looks"]
        self.assertEqual(9, len(looks))
        self.assertEqual({"dungeon_torch", "moonlit_exterior", "boss_arena"},
                         {item["look"] for item in looks})
        self.assertEqual({"corridor_static", "arena_combat", "dense_city"},
                         {item["scene_id"] for item in looks})
        self.assertEqual({"look_dungeon", "look_moonlit", "look_boss"},
                         set(self.runtime["s01"]["gpu_p95_ms"]))

    def test_shadow_and_gi_costs_are_recorded(self) -> None:
        self.assertLess(self.runtime["s02"]["gpu_low_p95_ms"], self.runtime["s02"]["gpu_ultra_p95_ms"])
        self.assertGreater(self.runtime["s02"]["gpu_delta_pct"], 0.0)
        self.assertEqual("NOT_RUN", self.runtime["s02"]["temporal_stability"])
        self.assertLess(self.runtime["s03"]["gpu_off_p95_ms"], self.runtime["s03"]["gpu_sdfgi_p95_ms"])
        self.assertGreater(self.runtime["s03"]["allocation_delta_mib"], 0.0)
        self.assertEqual("SDFGI_QUALITY_PROFILE_ONLY", self.runtime["s03"]["verdict"])

    def test_fog_and_budget_are_conservative(self) -> None:
        self.assertGreater(self.runtime["s04"]["gpu_delta_pct"], 0.0)
        self.assertEqual("VOLUMETRIC_WITH_DEPTH_FALLBACK", self.runtime["s04"]["verdict"])
        self.assertEqual(2, self.runtime["s06"]["shadowed_on"])
        self.assertEqual(4, self.runtime["s06"]["shadowed_off"])
        self.assertLess(self.runtime["s06"]["gpu_on_p95_ms"], self.runtime["s06"]["gpu_off_p95_ms"])
        self.assertEqual("LIGHT_BUDGET_MVP", self.runtime["s06"]["verdict"])

    def test_light_bridge_smoke_passes(self) -> None:
        self.assertEqual("PASS", self.bridge["verdict"])
        self.assertEqual(13, self.bridge["checks"])
        self.assertEqual([], self.bridge["failures"])
        self.assertEqual(self.bridge["checks"], self.runtime["s05"]["bridge_checks"])

    def test_rnd_decisions_are_explicit(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s07"]["decisions"]}
        self.assertEqual("GO", decisions["CineLight Bible"])
        self.assertEqual("GO", decisions["LightBridge"])
        self.assertEqual("RESEARCH_MORE", decisions["LightBudget"])
        self.assertIn("GO", decisions["GI Atlas"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m03FinalReference"]
        self.assertEqual("NEX-M03-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([8, 36, 37, 38, 39, 40, 41, 42, 43], block["issues"])
        self.assertEqual("M03_REFERENCE_LIGHTING_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builder_is_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m03/tools/build_lighting_runtime.py --check", workflow)

    def test_gate_covers_the_closed_issues(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#36", "#37", "#38", "#39", "#40", "#41", "#42", "#43", "#8",
                       "M03_LIGHTING_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

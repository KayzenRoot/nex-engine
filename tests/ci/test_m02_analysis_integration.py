"""Structural and reproducibility tests for the M02 scene-analysis integration."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m02" / "tools" / "build_analysis_integration.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m02" / "analysis-integration.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m02" / "ANALYSIS-INTEGRATION.md"
ANALYSIS_DIR = REPO / "nex_bench" / "scenes" / "m02_analysis"
SOURCES = {
    "sightline_controller.gd": REPO / "nex_modules" / "render3d" / "sightline" / "sightline_controller.gd",
    "depth_composition_solver.gd": REPO / "nex_modules" / "render3d" / "depth_composition" / "depth_composition_solver.gd",
    "temporal_guard_analyzer.gd": REPO / "nex_modules" / "render3d" / "temporal" / "temporal_guard_analyzer.gd",
}


class M02AnalysisIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m02_build_analysis_integration", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.scenes = {scene["scene_id"]: scene for scene in cls.report["scenes"]}

    def test_report_covers_three_scenes(self) -> None:
        self.assertEqual("m02_scene_analysis_integration.v1", self.report["schema_version"])
        self.assertEqual(3, self.report["runs"])
        self.assertEqual({"corridor_static", "arena_combat", "dense_city"}, set(self.scenes))
        self.assertEqual({"corridor_static": 17, "arena_combat": 34, "dense_city": 23},
                         {scene_id: scene["mesh_count"] for scene_id, scene in self.scenes.items()})

    def test_sightline_policy_is_exercised(self) -> None:
        for scene_id, scene in self.scenes.items():
            with self.subTest(scene=scene_id):
                summary = scene["sightline"]["summary"]
                self.assertEqual(1, summary["active_reveals"])
                self.assertEqual(1, summary["danger_alerts"])
                self.assertFalse(summary["critical_unseen"])
                actors = {actor["id"]: actor for actor in scene["sightline"]["actors"]}
                self.assertEqual(["mesh_00"], actors["player"]["blocked_by"])
                self.assertTrue(actors["player"]["visual_readable"])
                self.assertTrue(actors["threat"]["danger_alert"])

    def test_depth_and_temporal_results(self) -> None:
        self.assertEqual({"corridor_static": 0, "arena_combat": 4, "dense_city": 4},
                         {scene_id: scene["depth"]["z_fight_risks"] for scene_id, scene in self.scenes.items()})
        for scene in self.scenes.values():
            self.assertEqual(0, scene["depth"]["alpha_over_critical"])
            self.assertEqual(0, scene["depth"]["overlay_gameplay_conflicts"])
            self.assertEqual("BASELINE_ACCEPTABLE", scene["temporal"]["verdict"])
            self.assertEqual(5, scene["temporal"]["frames"])
            self.assertEqual(16, scene["temporal"]["regions"])

    def test_vendored_controllers_match_sources(self) -> None:
        for name, source in SOURCES.items():
            with self.subTest(name=name):
                self.assertEqual(source.read_bytes(), (ANALYSIS_DIR / name).read_bytes())

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.tool, self.report, REPORT_JSON, REPORT_MD)

    def test_report_makes_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertNotIn("fps improved", lowered)
        self.assertNotIn("quality verified", lowered)
        self.assertNotIn("universal gain", lowered)
        self.assertEqual("SCENE_ANALYSIS_DERIVED", self.report["verdict"])


if __name__ == "__main__":
    unittest.main()

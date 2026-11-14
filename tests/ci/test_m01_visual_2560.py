"""Structural and reproducibility tests for the 2560x1440 visual-truth report."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m09" / "tools" / "build_m01_visual_2560.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m09" / "m01-visual-2560.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m09" / "M01-VISUAL-2560-REPORT.md"


class M01Visual2560Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m09_build_m01_visual_2560", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.scenes = {scene["scene_id"]: scene for scene in cls.report["scenes"]}

    def test_report_covers_eighteen_images(self) -> None:
        self.assertEqual("m09_preset_m01_visual_2560.v1", self.report["schema_version"])
        self.assertEqual([2560, 1440], self.report["viewport_px"])
        self.assertEqual(18, self.report["runs"])
        self.assertEqual({"corridor_static", "arena_combat", "dense_city"}, set(self.scenes))
        for scene in self.scenes.values():
            with self.subTest(scene=scene["scene_id"]):
                self.assertEqual(6, len(scene["images"]))
                self.assertEqual(6, scene["aa"]["comparisons"])

    def test_aa_is_exact_and_ab_is_measured(self) -> None:
        expected = {
            "corridor_static": [0.3694, 168, 2.996, 39.085],
            "arena_combat": [0.3863, 190, 3.074, 37.136],
            "dense_city": [0.1524, 123, 1.031, 40.79],
        }
        for scene_id, values in expected.items():
            with self.subTest(scene=scene_id):
                scene = self.scenes[scene_id]
                self.assertTrue(scene["aa"]["identical_sha"])
                self.assertEqual(0.0, scene["aa"]["metrics"]["mean_abs_diff"])
                ab = scene["ab"]["metrics"]
                self.assertEqual(values, [
                    round(ab["mean_abs_diff"], 4), ab["max_abs_diff"],
                    round(ab["changed_pixels_pct"], 3), round(ab["psnr_db"], 3),
                ])

    def test_comparison_uses_the_1920_context(self) -> None:
        expected = {
            "corridor_static": [-11.4, -11.0],
            "arena_combat": [-8.4, -8.3],
            "dense_city": [-14.6, -19.2],
        }
        for scene_id, deltas in expected.items():
            with self.subTest(scene=scene_id):
                comparison = self.scenes[scene_id]["comparison_1920"]
                self.assertEqual(deltas, [
                    comparison["delta_mean_abs_pct"], comparison["delta_changed_pixels_pct"],
                ])
        self.assertEqual("docs/benchmarks/m09/m01-visual-1920.v1.json", self.report["context_report"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.tool, self.report, REPORT_JSON, REPORT_MD)

    def test_report_makes_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertNotIn("fps improved", lowered)
        self.assertNotIn("quality verified", lowered)
        self.assertNotIn("universal gain", lowered)


if __name__ == "__main__":
    unittest.main()

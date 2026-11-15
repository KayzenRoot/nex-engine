"""Structural and reproducibility tests for the M02-S01 camera integration."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m02" / "tools" / "build_camera_integration.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m02" / "camera-integration.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m02" / "CAMERA-INTEGRATION.md"
VENDORED = REPO / "nex_bench" / "scenes" / "m02_camera" / "camera_rig.gd"
SOURCE = REPO / "nex_modules" / "render3d" / "camera" / "camera_rig.gd"


class M02CameraIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m02_build_camera_integration", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.visual = {scene["scene_id"]: scene for scene in cls.report["visual"]["scenes"]}
        cls.performance = {scene["scene_id"]: scene for scene in cls.report["performance"]["scenes"]}

    def test_report_covers_three_scenes_and_eighteen_runs(self) -> None:
        self.assertEqual("m02_camera_integration.v1", self.report["schema_version"])
        self.assertEqual(18, self.report["visual"]["runs"])
        self.assertEqual(18, self.report["performance"]["runs"])
        self.assertEqual({"corridor_static", "arena_combat", "dense_city"}, set(self.visual))
        self.assertEqual(set(self.visual), set(self.performance))

    def test_visual_aa_and_ab_metrics(self) -> None:
        expected = {
            "corridor_static": [0.002, 0.013, 59.661],
            "arena_combat": [0.0003, 0.003, 71.951],
            "dense_city": [0.0, 0.0, 106.527],
        }
        for scene_id, values in expected.items():
            with self.subTest(scene=scene_id):
                scene = self.visual[scene_id]
                self.assertTrue(scene["aa_identical"])
                ab = scene["ab"]
                self.assertEqual(values, [
                    round(ab["mean_abs_diff"], 4), round(ab["changed_pixels_pct"], 3), round(ab["psnr_db"], 3),
                ])

    def test_performance_deltas(self) -> None:
        self.assertEqual({"gpu_p95_ms": 0.0, "cpu_p95_ms": 0.0, "pacing_p95_ms": 0.33},
                         self.performance["corridor_static"]["delta_pct"])
        self.assertEqual({"gpu_p95_ms": 0.94, "cpu_p95_ms": 13.3, "pacing_p95_ms": 0.29},
                         self.performance["arena_combat"]["delta_pct"])
        self.assertEqual({"gpu_p95_ms": 1.25, "cpu_p95_ms": 12.94, "pacing_p95_ms": -0.4},
                         self.performance["dense_city"]["delta_pct"])

    def test_vendored_rig_matches_source(self) -> None:
        self.assertEqual(SOURCE.read_bytes(), VENDORED.read_bytes())

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.tool, self.report, REPORT_JSON, REPORT_MD)

    def test_report_makes_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertNotIn("fps improved", lowered)
        self.assertNotIn("quality verified", lowered)
        self.assertNotIn("universal gain", lowered)
        self.assertEqual("CAMERA_RIG_REPRODUCES_BASELINE_FRAMING", self.report["verdict"])


if __name__ == "__main__":
    unittest.main()

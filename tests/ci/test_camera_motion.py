"""Structural and reproducibility tests for the camera-motion sequence report."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m09" / "tools" / "build_camera_motion.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m09" / "camera-motion.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m09" / "CAMERA-MOTION-REPORT.md"


class CameraMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m09_build_camera_motion", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.cells = {(cell["scene_id"], cell["preset_id"]): cell for cell in cls.report["cells"]}

    def test_report_covers_six_cells_and_thirty_frames(self) -> None:
        self.assertEqual("m09_camera_motion.v1", self.report["schema_version"])
        self.assertEqual(30, self.report["runs"])
        self.assertEqual([1280, 720], self.report["viewport_px"])
        self.assertEqual(6, len(self.cells))
        for (scene_id, preset), cell in self.cells.items():
            with self.subTest(scene=scene_id, preset=preset):
                self.assertEqual(5, cell["frames"])
                self.assertEqual(4, len(cell["pairs"]))

    def test_every_pair_differs_and_aggregates_match(self) -> None:
        expected = {
            ("corridor_static", "ab-low"): [5.0913, 19.766, 21.734],
            ("corridor_static", "ab-high"): [5.1619, 19.168, 21.428],
            ("arena_combat", "ab-low"): [2.1781, 8.534, 25.912],
            ("arena_combat", "ab-high"): [2.2321, 8.088, 25.728],
            ("dense_city", "ab-low"): [1.7989, 7.051, 27.127],
            ("dense_city", "ab-high"): [1.8396, 6.477, 26.768],
        }
        for key, values in expected.items():
            with self.subTest(cell=key):
                cell = self.cells[key]
                self.assertEqual(values, [
                    cell["mean_abs_diff_mean"], cell["changed_pixels_pct_max"], cell["psnr_db_min"],
                ])
                for pair in cell["pairs"]:
                    self.assertGreater(pair["changed_pixels_pct"], 0.0)

    def test_motion_configuration_is_recorded(self) -> None:
        motion = self.report["workload"]["camera_motion"]
        self.assertEqual(("orbit", 3.0, 5), (motion["mode"], motion["step_deg"], motion["frames"]))
        self.assertEqual(100, self.report["workload"]["proxy_count"])
        self.assertEqual("lights", self.report["workload"]["effect_mode"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.tool, self.report, REPORT_JSON, REPORT_MD)

    def test_report_makes_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertNotIn("fps improved", lowered)
        self.assertNotIn("quality verified", lowered)
        self.assertNotIn("universal gain", lowered)

    def test_static_stability_is_not_claimed(self) -> None:
        self.assertIn("not a quality, stability or performance claim", " ".join(self.report["observations"]))
        self.assertIn("static scene content", " ".join(self.report["limitations"]))


if __name__ == "__main__":
    unittest.main()

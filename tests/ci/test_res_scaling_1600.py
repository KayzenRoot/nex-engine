"""Structural and reproducibility tests for the 1600x900 resolution report."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m09" / "tools" / "build_res_scaling_1600.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m09" / "res-scaling-1600.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m09" / "RES-SCALING-1600-REPORT.md"


class ResScaling1600Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m09_build_res_scaling_1600", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.cells = {cell["preset_id"]: cell for cell in cls.report["cells"]}

    def test_report_covers_six_runs_and_two_cells(self) -> None:
        self.assertEqual("m09_resolution_scaling_1600.v1", self.report["schema_version"])
        self.assertEqual("b9fd2ed1cbde0625200b104fbd2c34796258dad3", self.report["source_sha"])
        self.assertEqual(6, self.report["runs"])
        self.assertEqual({"ab-low", "ab-high"}, set(self.cells))
        for preset, cell in self.cells.items():
            with self.subTest(preset=preset):
                self.assertEqual((3, 100, 1600, 900), (
                    cell["runs"], cell["proxy_count"], cell["width"], cell["height"],
                ))

    def test_cells_have_expected_medians(self) -> None:
        low, high = self.cells["ab-low"], self.cells["ab-high"]
        self.assertEqual([0.120, 0.133, 0.135, 0.462, 4.252, 213.08, 0.8, 3.0], [
            low["gpu_p50_ms"], low["gpu_p95_ms"], low["gpu_p99_ms"], low["cpu_p95_ms"],
            low["pacing_p95_ms"], low["one_percent_low_fps"],
            low["gpu_p95_spread_pct"], low["one_percent_low_spread_pct"],
        ])
        self.assertEqual([0.625, 0.632, 0.917, 0.749, 4.274, 214.03, 0.5, 3.3], [
            high["gpu_p50_ms"], high["gpu_p95_ms"], high["gpu_p99_ms"], high["cpu_p95_ms"],
            high["pacing_p95_ms"], high["one_percent_low_fps"],
            high["gpu_p95_spread_pct"], high["one_percent_low_spread_pct"],
        ])

    def test_resolution_deltas_use_the_integrated_context(self) -> None:
        self.assertEqual(375.2, self.report["deltas_high_vs_low"]["gpu_p95_pct"])
        self.assertEqual({"ab-low": 25.5, "ab-high": 37.4},
                         self.report["resolution_deltas"]["1280x720_to_1600x900"])
        self.assertEqual({"ab-low": 17.3, "ab-high": 30.7},
                         self.report["resolution_deltas"]["1600x900_to_1920x1080"])

    def test_model_context_is_between_calibration_and_1920(self) -> None:
        low, high = self.report["model_context"]["cells"]
        self.assertEqual((0.379, 0.133, 185.0, False), (
            low["predicted_gpu_ms"], low["measured_gpu_p95_ms"], low["error_pct"], low["within_2pct"],
        ))
        self.assertEqual((0.46, 0.632, -27.2, False), (
            high["predicted_gpu_ms"], high["measured_gpu_p95_ms"], high["error_pct"], high["within_2pct"],
        ))

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.tool, self.report, REPORT_JSON, REPORT_MD)

    def test_report_makes_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertNotIn("fps improved", lowered)
        self.assertNotIn("quality verified", lowered)
        self.assertNotIn("universal gain", lowered)


if __name__ == "__main__":
    unittest.main()

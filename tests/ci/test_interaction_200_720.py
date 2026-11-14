"""Structural and reproducibility tests for the 200-proxy / 1280x720 report."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m09" / "tools" / "build_interaction_200_720.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m09" / "interaction-200-720.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m09" / "INTERACTION-200-720-REPORT.md"


class Interaction200720Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m09_build_interaction_200_720", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.cells = {cell["preset_id"]: cell for cell in cls.report["cells"]}

    def test_report_covers_six_runs_and_two_cells(self) -> None:
        self.assertEqual("m09_preset_interaction_200_720.v1", self.report["schema_version"])
        self.assertEqual("99eaad041b84c373da33ec1bb8a5922c31f4dad4", self.report["source_sha"])
        self.assertEqual(6, self.report["runs"])
        self.assertEqual({"ab-low", "ab-high"}, set(self.cells))
        for preset, cell in self.cells.items():
            with self.subTest(preset=preset):
                self.assertEqual((3, 200, 1280, 720), (
                    cell["runs"], cell["proxy_count"], cell["width"], cell["height"],
                ))

    def test_cells_have_expected_medians(self) -> None:
        low, high = self.cells["ab-low"], self.cells["ab-high"]
        self.assertEqual([0.107, 0.111, 0.116, 0.445, 4.232, 207.25, 0.9, 9.3], [
            low["gpu_p50_ms"], low["gpu_p95_ms"], low["gpu_p99_ms"], low["cpu_p95_ms"],
            low["pacing_p95_ms"], low["one_percent_low_fps"],
            low["gpu_p95_spread_pct"], low["one_percent_low_spread_pct"],
        ])
        self.assertEqual([0.463, 0.468, 0.656, 0.647, 4.234, 219.25, 0.0, 7.6], [
            high["gpu_p50_ms"], high["gpu_p95_ms"], high["gpu_p99_ms"], high["cpu_p95_ms"],
            high["pacing_p95_ms"], high["one_percent_low_fps"],
            high["gpu_p95_spread_pct"], high["one_percent_low_spread_pct"],
        ])

    def test_deltas_and_100_proxy_context(self) -> None:
        self.assertEqual(321.6, self.report["deltas_high_vs_low"]["gpu_p95_pct"])
        self.assertEqual({"ab-low": 0.109, "ab-high": 0.462}, {
            preset: values["gpu_p95_ms"] for preset, values in self.report["context_100"].items()
        })
        self.assertEqual({"ab-low": [1.8, 29.0], "ab-high": [1.3, 48.7]}, {
            preset: [values["gpu_p95_pct"], values["cpu_p95_pct"]]
            for preset, values in self.report["proxy_100_to_200"].items()
        })

    def test_model_context_keeps_high_within_two_percent(self) -> None:
        low, high = self.report["model_context"]["cells"]
        self.assertEqual((0.379, 0.111, 241.4, False), (
            low["predicted_gpu_ms"], low["measured_gpu_p95_ms"], low["error_pct"], low["within_2pct"],
        ))
        self.assertEqual((0.46, 0.468, -1.7, True), (
            high["predicted_gpu_ms"], high["measured_gpu_p95_ms"], high["error_pct"], high["within_2pct"],
        ))

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.tool.build_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.tool.render_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))

    def test_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertFalse(any(phrase in lowered for phrase in (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        )))


if __name__ == "__main__":
    unittest.main()

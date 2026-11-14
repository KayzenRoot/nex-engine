"""Structural, semantic and reproducibility tests for the M06 advisories."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_no_fabricated, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m06" / "tools" / "build_advisories.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m06" / "advisories.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m06" / "ADVISORIES.md"
OBSERVATIONS = REPO / "docs" / "benchmarks" / "m06" / "observations" / "m09-observations.v1.json"


class M06AdvisoriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m06_build_advisories", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))["observations"]
        cls.advisories = {entry["observation_id"]: entry for entry in cls.report["advisories"]}

    def test_report_covers_every_observation(self) -> None:
        self.assertEqual("m06_performance_advisories.v1", self.report["schema_version"])
        self.assertEqual(12, self.report["observation_count"])
        self.assertEqual(12, len(self.report["advisories"]))
        expected = {observation["observation_id"] for observation in self.observations}
        self.assertEqual(expected, set(self.advisories))

    def test_summary_and_first_advisory_values(self) -> None:
        summary = self.report["summary"]
        self.assertEqual({"pacing": 12}, summary["bottleneck_counts"])
        self.assertEqual(3.402, summary["min_render_headroom_ms"])
        self.assertEqual(3.914, summary["max_render_headroom_ms"])
        self.assertEqual(19.92, summary["max_gpu_share_of_frame_pct"])
        first = self.advisories["m09-preset-ab-low"]
        self.assertEqual("pacing", first["bottleneck"])
        self.assertEqual(0.147, first["measured"]["gpu_render_ms"])
        self.assertEqual(0.357, first["measured"]["cpu_render_ms"])
        self.assertEqual(4.199, first["measured"]["frame_pacing_ms"])
        self.assertEqual(3.842, first["frame_budget"]["render_headroom_ms"])
        self.assertEqual(3.5, first["frame_budget"]["gpu_share_of_frame_pct"])
        self.assertEqual(8.5, first["frame_budget"]["cpu_share_of_frame_pct"])
        self.assertEqual(4.167, first["frame_budget"]["target_frame_ms"])

    def test_recommendations_are_safe_and_require_measurement(self) -> None:
        for observation_id, advisory in self.advisories.items():
            with self.subTest(observation=observation_id):
                recommendation = advisory["recommendation"]
                self.assertEqual("LOW", recommendation["risk"])
                self.assertTrue(recommendation["requires_measurement"])
                self.assertIn("re-measure", recommendation["action"])
                self.assertIn("does not prove", recommendation["reason"])

    def test_no_fps_or_quality_claim(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        assert_no_fabricated(self, text, (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        ))

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.tool.build_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.tool.render_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

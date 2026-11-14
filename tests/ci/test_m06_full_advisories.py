"""Structural and reproducibility tests for the full M06 performance advisories."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_no_fabricated, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m06" / "tools" / "build_advisories.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m06" / "advisories-full.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m06" / "ADVISORIES-FULL.md"
OBSERVATIONS = REPO / "docs" / "benchmarks" / "m06" / "observations" / "m09-observations-full.v1.json"
SOURCE_BUNDLE = "docs/benchmarks/m06/observations/m09-observations-full.v1.json"


class M06FullAdvisoriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m06_build_full_advisories", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))["observations"]
        cls.advisories = {entry["observation_id"]: entry for entry in cls.report["advisories"]}

    def test_full_report_covers_every_observation(self) -> None:
        self.assertEqual("m06_performance_advisories.v1", self.report["schema_version"])
        self.assertEqual(SOURCE_BUNDLE, self.report["source_bundle"])
        self.assertEqual(144, self.report["observation_count"])
        self.assertEqual(144, len(self.advisories))
        expected = {observation["observation_id"] for observation in self.observations}
        self.assertEqual(expected, set(self.advisories))

    def test_summary_matches_the_derived_advisories(self) -> None:
        summary = self.report["summary"]
        self.assertEqual({"pacing": 144}, summary["bottleneck_counts"])
        headrooms = [entry["frame_budget"]["render_headroom_ms"] for entry in self.advisories.values()]
        gpu_shares = [entry["frame_budget"]["gpu_share_of_frame_pct"] for entry in self.advisories.values()]
        self.assertEqual(min(headrooms), summary["min_render_headroom_ms"])
        self.assertEqual(max(headrooms), summary["max_render_headroom_ms"])
        self.assertEqual(max(gpu_shares), summary["max_gpu_share_of_frame_pct"])
        self.assertEqual(4.167, summary["target_frame_ms_240_fps"])
        self.assertEqual(3.327, summary["min_render_headroom_ms"])
        self.assertEqual(4.009, summary["max_render_headroom_ms"])
        self.assertEqual(21.05, summary["max_gpu_share_of_frame_pct"])

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
        rebuilt = self.tool.build_report(self.tool.SOURCE_FULL, self.tool.EXPECTED_OBSERVATIONS_FULL)
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            self.tool.render_markdown(rebuilt, self.tool.FULL_TITLE),
            REPORT_MD.read_text(encoding="utf-8"),
        )

    def test_curated_default_still_covers_twelve(self) -> None:
        curated = self.tool.build_report()
        self.assertEqual(12, curated["observation_count"])
        self.assertEqual("docs/benchmarks/m06/observations/m09-observations.v1.json", curated["source_bundle"])


if __name__ == "__main__":
    unittest.main()

"""Structural and reproducibility tests for the full M06 performance advisories."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m06" / "tools" / "build_advisories.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m06" / "advisories-full.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m06" / "ADVISORIES-FULL.md"
OBSERVATIONS = REPO / "docs" / "benchmarks" / "m06" / "observations" / "m09-observations-full.v1.json"


class M06FullAdvisoriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m06_build_full_advisories", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.advisories = {entry["observation_id"]: entry for entry in cls.report["advisories"]}

    def test_full_report_covers_every_observation(self) -> None:
        self.assertEqual("m06_performance_advisories.v1", self.report["schema_version"])
        self.assertEqual("docs/benchmarks/m06/observations/m09-observations-full.v1.json", self.report["source_bundle"])
        expected = {entry["observation_id"] for entry in json.loads(OBSERVATIONS.read_text(encoding="utf-8"))["observations"]}
        self.assertEqual(expected, set(self.advisories))
        self.assertEqual(144, self.report["observation_count"])

    def test_summary_and_recommendations_are_derived_and_safe(self) -> None:
        summary = self.report["summary"]
        self.assertEqual({"pacing": 144}, summary["bottleneck_counts"])
        headrooms = [entry["frame_budget"]["render_headroom_ms"] for entry in self.advisories.values()]
        shares = [entry["frame_budget"]["gpu_share_of_frame_pct"] for entry in self.advisories.values()]
        self.assertEqual([min(headrooms), max(headrooms), max(shares)], [
            summary["min_render_headroom_ms"], summary["max_render_headroom_ms"], summary["max_gpu_share_of_frame_pct"],
        ])
        self.assertEqual([3.327, 4.009, 21.05, 4.167], [
            summary["min_render_headroom_ms"], summary["max_render_headroom_ms"],
            summary["max_gpu_share_of_frame_pct"], summary["target_frame_ms_240_fps"],
        ])
        self.assertTrue(all(entry["recommendation"]["risk"] == "LOW" for entry in self.advisories.values()))
        self.assertTrue(all(entry["recommendation"]["requires_measurement"] for entry in self.advisories.values()))
        self.assertTrue(all("re-measure" in entry["recommendation"]["action"] for entry in self.advisories.values()))

    def test_outputs_are_reproducible_and_make_no_fps_claim(self) -> None:
        rebuilt = self.tool.build_report(self.tool.SOURCE_FULL, self.tool.EXPECTED_OBSERVATIONS_FULL)
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.tool.render_markdown(rebuilt, self.tool.FULL_TITLE), REPORT_MD.read_text(encoding="utf-8"))
        markdown = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertFalse(any(phrase in markdown for phrase in (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        )))

    def test_curated_default_still_covers_twelve(self) -> None:
        curated = self.tool.build_report()
        self.assertEqual(
            (12, "docs/benchmarks/m06/observations/m09-observations.v1.json"),
            (curated["observation_count"], curated["source_bundle"]),
        )


if __name__ == "__main__":
    unittest.main()

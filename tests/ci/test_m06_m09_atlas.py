"""Structural and reproducibility tests for the M06 M09 performance atlas."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_no_fabricated, load_builder

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs" / "benchmarks" / "m06"
BUILDER = DOCS / "tools" / "build_m09_atlas.py"
REPORT_JSON = DOCS / "m09-performance-atlas.v1.json"
REPORT_MD = DOCS / "M09-PERFORMANCE-ATLAS.md"
SOURCE = DOCS / "observations" / "m09-observations-full.v1.json"
EXPECTED_COUNTS = {"preset-ab": 6, "proxy-scaling": 18, "m01-ab": 18, "res-scaling": 18,
                   "interaction": 24, "cross-scene": 48, "interaction-200": 12}


class M06M09AtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m06_build_m09_atlas", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.bundles = {bundle["bundle"]: bundle for bundle in cls.report["bundles"]}

    def test_report_covers_seven_bundles_and_144_observations(self) -> None:
        self.assertEqual("m06_m09_performance_atlas.v1", self.report["schema_version"])
        self.assertEqual(144, self.report["observation_count"])
        self.assertEqual(7, self.report["bundle_count"])
        self.assertEqual(144, len(self.source["observations"]))
        self.assertEqual(EXPECTED_COUNTS, {name: bundle["runs"] for name, bundle in self.bundles.items()})

    def test_every_bundle_is_pacing_and_has_cells(self) -> None:
        for name, bundle in self.bundles.items():
            with self.subTest(bundle=name):
                self.assertEqual({"pacing": bundle["runs"]}, bundle["bottleneck_counts"])
                self.assertGreater(len(bundle["cells"]), 0)
                for cell in bundle["cells"]:
                    self.assertEqual("pacing", cell["bottleneck"])
                    self.assertGreaterEqual(cell["gpu_p95_ms"], 0.0)

    def test_summary_and_top_cell_values(self) -> None:
        summary = self.report["summary"]
        self.assertEqual({"pacing": 144}, summary["bottleneck_counts"])
        self.assertEqual(0.068, summary["gpu_p95_ms"]["min"])
        self.assertEqual(0.887, summary["gpu_p95_ms"]["max"])
        self.assertEqual(0.196, summary["gpu_p95_ms"]["median"])
        self.assertEqual(21.05, summary["max_gpu_share_pct"])
        top = max((cell for bundle in self.report["bundles"] for cell in bundle["cells"]),
                  key=lambda cell: cell["gpu_p95_ms"])
        self.assertEqual("preset-ab", top["bundle"])
        self.assertEqual("ab-high", top["preset_id"])
        self.assertEqual(200, top["proxy_count"])
        self.assertEqual(0.881, top["gpu_p95_ms"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.builder.build_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.builder.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.builder.render_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))

    def test_no_fps_or_quality_claim(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        assert_no_fabricated(self, text, (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        ))


if __name__ == "__main__":
    unittest.main()

"""Structural and reproducibility tests for the NEX M09 measurement atlas."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, assert_no_fabricated, load_builder

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_measurement_atlas.py"
REPORT_JSON = DOCS / "measurement-atlas.v1.json"
REPORT_MD = DOCS / "MEASUREMENT-ATLAS.md"


class MeasurementAtlasFilesTests(unittest.TestCase):
    def test_atlas_and_builder_exist(self) -> None:
        for path in (BUILDER, REPORT_JSON, REPORT_MD):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())


class MeasurementAtlasContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_atlas", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.entries = {entry["id"]: entry for entry in cls.report["entries"]}

    def test_totals_cover_eight_bundles(self) -> None:
        self.assertEqual("m09_measurement_atlas.v1", self.report["schema_version"])
        self.assertEqual(8, self.report["totals"]["bundles"])
        self.assertEqual(144, self.report["totals"]["performance_captures"])
        self.assertEqual(18, self.report["totals"]["visual_images"])
        self.assertEqual(330, self.report["totals"]["evidence_files"])
        self.assertEqual(8, self.report["totals"]["unique_source_shas"])
        self.assertEqual(144, self.report["runs"])

    def test_entry_counts_and_source_shas(self) -> None:
        expected = {
            "preset-ab": (6, 15, "baf818ef934c418d111091af755e0a19ddd6ac9e"),
            "proxy-scaling": (18, 39, "4e4719ac504ddb0ea7961d5c9d557c745f216990"),
            "m01-ab": (18, 39, "617db53d6752f30584b296f133e6990ca6602549"),
            "m01-visual": (18, 21, "952b5a63bc1696cadf7436a061a7d996c80fa220"),
            "res-scaling": (18, 39, "6ebb98e8c7c9c6a9a0aa3faae5af7e8d4290b7f5"),
            "interaction": (24, 51, "2ef072c70189d5d013a62b7efc821f81078ef6d1"),
            "cross-scene": (48, 99, "2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce"),
            "interaction-200": (12, 27, "c1b73743c0c95d9fb8867079cb91fb74cfc03d49"),
        }
        for entry_id, (runs, files, sha) in expected.items():
            with self.subTest(entry=entry_id):
                entry = self.entries[entry_id]
                self.assertEqual(runs, entry["runs"])
                self.assertEqual(files, entry["evidence_files"])
                self.assertEqual(sha, entry["source_sha"])

    def test_key_findings_match_source_reports(self) -> None:
        self.assertEqual(499.3, self.entries["preset-ab"]["key_findings"]["gpu_p95_high_vs_low_pct"])
        scaling = self.entries["proxy-scaling"]["key_findings"]["gpu_p95_high_vs_low_pct"]
        self.assertEqual({"25": 504.7, "100": 499.3, "200": 478.3}, scaling)
        m01 = self.entries["m01-ab"]["key_findings"]["gpu_p95_high_vs_low_pct"]
        self.assertEqual({"corridor_static": 380.7, "arena_combat": 323.9, "dense_city": 331.0}, m01)
        visual = self.entries["m01-visual"]["key_findings"]
        self.assertTrue(visual["aa_identical"])
        self.assertEqual({"corridor_static": 4.077, "arena_combat": 3.884, "dense_city": 1.745},
                         visual["ab_changed_pixels_pct"])
        res = self.entries["res-scaling"]["key_findings"]["gpu_p95_high_vs_low_pct"]
        self.assertEqual({"960x540": 230.2, "1280x720": 334.0, "1920x1080": 429.5}, res)
        interaction = self.entries["interaction"]["key_findings"]["gpu_p95_high_vs_low_pct"]
        self.assertEqual({"50/960x540": 219.8, "50/1920x1080": 469.4,
                          "100/960x540": 227.1, "100/1920x1080": 473.6}, interaction)
        cross = self.entries["cross-scene"]["key_findings"]["gpu_p95_high_vs_low_pct"]
        self.assertEqual(294.4, cross["corridor_static"]["50/960x540"])
        self.assertEqual(461.5, cross["dense_city"]["50/1920x1080"])
        last = self.entries["interaction-200"]["key_findings"]
        self.assertEqual({"200/960x540": 228.6, "200/1920x1080": 438.2}, last["gpu_p95_high_vs_low_pct"])
        self.assertEqual(60.2, last["resolution_scaling_pct"]["200"]["ab-low"])
        self.assertEqual(162.4, last["resolution_scaling_pct"]["200"]["ab-high"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_no_fabricated_quality_or_gain_claim(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        assert_no_fabricated(self, text, (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        ))


if __name__ == "__main__":
    unittest.main()

"""Structural and reproducibility tests for the NEX M06 Bottleneck Atlas."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO / "docs" / "benchmarks" / "m06"
BUILDER_PATH = MODULE_DIR / "tools" / "build_atlas.py"
ATLAS_PATH = MODULE_DIR / "atlas.v1.json"
REPORT_PATH = MODULE_DIR / "ATLAS.md"
BUNDLE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-13-s05"


def _load_builder():
    spec = importlib.util.spec_from_file_location("nex_m06_build_atlas", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load build_atlas.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AtlasFilesTests(unittest.TestCase):
    def test_outputs_and_builder_exist(self) -> None:
        for path in (ATLAS_PATH, REPORT_PATH, BUILDER_PATH):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_atlas_is_versioned_and_complete(self) -> None:
        atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        self.assertEqual("m06_bottleneck_atlas.v1", atlas["schema_version"])
        self.assertEqual(15, atlas["capture_count"])
        self.assertEqual(15, len(atlas["runs"]))
        self.assertEqual(13, len(atlas["cells"]))
        self.assertEqual(15, len({run["run_id"] for run in atlas["runs"]}))


class AtlasClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))

    def test_every_run_is_pacing_bound_with_measured_evidence(self) -> None:
        for run in self.atlas["runs"]:
            with self.subTest(run=run["run_id"]):
                self.assertEqual("pacing", run["classification"])
                self.assertEqual("measured", run["evidence"])
                self.assertIn(run["confidence"], ("high", "medium"))
                self.assertGreater(run["render_headroom_ms"], 0.0)

    def test_baseline_references_cover_each_count(self) -> None:
        references = self.atlas["baseline_references"]
        self.assertEqual({"25", "100", "200"}, set(references))
        self.assertEqual(3, references["25"]["runs"])
        self.assertEqual(1, references["100"]["runs"])
        self.assertEqual(1, references["200"]["runs"])
        for reference in references.values():
            with self.subTest(reference=reference):
                self.assertGreater(reference["gpu_p95_median_ms"], 0.0)
                self.assertGreater(reference["pacing_p95_median_ms"], reference["gpu_p95_median_ms"])

    def test_shadow_delta_is_recomputed_from_the_capture(self) -> None:
        run = next(item for item in self.atlas["runs"] if item["scenario"] == "shadows-25")
        baseline = self.atlas["baseline_references"]["25"]["gpu_p95_median_ms"]
        expected = round((run["gpu_ms"]["p95"] - baseline) / baseline * 100.0, 1)
        self.assertEqual(expected, run["delta_vs_baseline"]["gpu_p95_pct"])
        self.assertEqual(154.1, expected)

    def test_baseline_runs_have_no_delta(self) -> None:
        for run in self.atlas["runs"]:
            if run["preset"] == "baseline":
                self.assertIsNone(run["delta_vs_baseline"])
            else:
                self.assertIsNotNone(run["delta_vs_baseline"])

    def test_summary_and_observations_are_consistent(self) -> None:
        summary = self.atlas["summary"]
        self.assertEqual("pacing", summary["dominant_classification"])
        self.assertEqual({"pacing": 15}, summary["classification_counts"])
        self.assertEqual(1.194, summary["max_gpu_p95_ms"])
        self.assertEqual(0.002, summary["baseline25_gpu_p50_spread_ms"])
        observations = " ".join(self.atlas["observations"])
        self.assertIn("shadows-25", observations)
        self.assertIn("combined-25", observations)
        self.assertIn("pacing-bound", observations)


class AtlasReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = _load_builder()
        cls.atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def test_bundle_hashes_pass(self) -> None:
        verification = self.builder.verify_bundle()
        self.assertEqual("PASS", verification["status"])
        self.assertEqual(32, verification["verified_files"])
        self.assertTrue(verification["measurement_captures_strict"])

    def test_builder_reproduces_committed_json(self) -> None:
        rebuilt = self.builder.build_atlas()
        self.assertEqual(self.atlas, rebuilt)
        self.assertEqual(self.builder.render_json(rebuilt), ATLAS_PATH.read_text(encoding="utf-8"))

    def test_builder_reproduces_committed_markdown(self) -> None:
        rebuilt = self.builder.build_atlas()
        self.assertEqual(self.report, self.builder.render_markdown(rebuilt))

    def test_source_table_maps_every_raw_capture(self) -> None:
        rows = self.builder.parse_analysis_table()
        table_ids = {row["run_id"] for row in rows}
        raw_ids = {
            match.group(1)
            for path in BUNDLE.glob("gpu_profile_*.json")
            if (match := re.fullmatch(r"gpu_profile_([0-9]+-[0-9]+)\.json", path.name))
        }
        self.assertEqual(15, len(table_ids))
        self.assertEqual(table_ids, raw_ids)

    def test_limits_are_explicit(self) -> None:
        limitations = " ".join(self.atlas["limitations"]).lower()
        for expected in ("single synthetic session", "vsync-limited", "no new measurement", "not device vram"):
            with self.subTest(expected=expected):
                self.assertIn(expected, limitations)
        self.assertNotIn("fps", self.atlas)
        self.assertNotIn("benchmark passed", self.report.lower())


if __name__ == "__main__":
    unittest.main()

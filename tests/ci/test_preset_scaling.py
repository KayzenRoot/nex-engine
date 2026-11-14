"""Structural and reproducibility tests for the NEX M09 preset scaling matrix."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

from _preset_ab_support import assert_no_fabricated, assert_sha256sums, load_builder

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-preset-scaling"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_scaling.py"
REPORT_JSON = DOCS / "scaling.v1.json"
REPORT_MD = DOCS / "SCALING-REPORT.md"
COUNTS = (25, 100, 200)
PRESETS = ("ab-low", "ab-high")


class ScalingFilesTests(unittest.TestCase):
    def test_evidence_and_report_files_exist(self) -> None:
        for path in (
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
        ):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
        raw = [p for p in EVIDENCE.glob("gpu_profile_*.json") if not p.name.endswith(".validation.json")]
        self.assertEqual(18, len(raw))
        for path in raw:
            with self.subTest(run=path.name):
                self.assertTrue((EVIDENCE / f"{path.name}.validation.json").is_file())

    def test_manifest_covers_six_cells(self) -> None:
        manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(18, len(manifest["runs"]))
        cells = {(run["proxy_count"], run["preset_id"]) for run in manifest["runs"]}
        self.assertEqual({(count, preset) for count in COUNTS for preset in PRESETS}, cells)
        for cell in cells:
            with self.subTest(cell=cell):
                self.assertEqual(3, sum(1 for run in manifest["runs"] if (run["proxy_count"], run["preset_id"]) == cell))


class ScalingEvidenceTests(unittest.TestCase):
    def test_captures_are_complete_and_consistent(self) -> None:
        manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        for entry in manifest["runs"]:
            with self.subTest(run=entry["run_id"]):
                document = json.loads((EVIDENCE / f"gpu_profile_{entry['run_id']}.json").read_text(encoding="utf-8"))
                self.assertEqual("COMPLETE", document["run_status"])
                self.assertEqual(manifest["source_sha"], document["source_sha"])
                self.assertEqual("Preset A/B/A", document["workload"]["scene"])
                self.assertEqual(entry["proxy_count"], document["workload"]["proxy_count"])
                self.assertEqual("lights", document["workload"]["effect_mode"])
                self.assertEqual(240, document["settings"]["max_fps"])
                self.assertEqual(0, document["settings"]["vsync_mode"])

    def test_validations_pass(self) -> None:
        manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        for entry in manifest["runs"]:
            with self.subTest(run=entry["run_id"]):
                validation = json.loads((EVIDENCE / f"gpu_profile_{entry['run_id']}.json.validation.json").read_text(encoding="utf-8"))
                self.assertEqual("PASS", validation["status"])

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 39)


class ScalingReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_scaling", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_six_cells_and_expected_deltas(self) -> None:
        self.assertEqual("m09_preset_scaling.v1", self.report["schema_version"])
        self.assertEqual(18, len(self.report["runs"]))
        self.assertEqual(6, len(self.report["cells"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        self.assertEqual(504.7, self.report["deltas_high_vs_low"]["25"]["gpu_p95_pct"])
        self.assertEqual(499.3, self.report["deltas_high_vs_low"]["100"]["gpu_p95_pct"])
        self.assertEqual(478.3, self.report["deltas_high_vs_low"]["200"]["gpu_p95_pct"])
        self.assertEqual(18.7, self.report["scaling_25_to_200"]["ab-low"]["gpu_p95_25_to_200_pct"])
        self.assertEqual(13.6, self.report["scaling_25_to_200"]["ab-high"]["gpu_p95_25_to_200_pct"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.builder.build_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.builder.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.builder.render_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))

    def test_limits_and_no_fabricated_gain(self) -> None:
        limitations = " ".join(self.report["limitations"]).lower()
        for expected in ("single session", "no cross-scene", "vsync disabled", "not device vram"):
            with self.subTest(expected=expected):
                self.assertIn(expected, limitations)
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        assert_no_fabricated(self, text, ("fps improved", "benchmark passed", "universal gain", "quality verified"))


if __name__ == "__main__":
    unittest.main()

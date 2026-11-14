"""Structural, provenance and reproducibility tests for the NEX interaction run."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import (
    assert_builder_reproduces,
    assert_captures,
    assert_limits,
    assert_sha256sums,
    assert_validations,
    load_builder,
)

REPO = Path(__file__).resolve().parents[2]
SCENE = REPO / "nex_bench" / "scenes" / "preset_ab"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-interaction"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_interaction.py"
REPORT_JSON = DOCS / "interaction.v1.json"
REPORT_MD = DOCS / "INTERACTION-REPORT.md"
CELLS = ((50, 960, 540), (50, 1920, 1080), (100, 960, 540), (100, 1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class InteractionFilesTests(unittest.TestCase):
    def test_harness_evidence_and_report_files_exist(self) -> None:
        required = [
            SCENE / "preset_ab.gd",
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
        ]
        self.assertEqual([], [str(path) for path in required if not path.is_file()])
        raw = [p for p in EVIDENCE.glob("gpu_profile_*.json") if not p.name.endswith(".validation.json")]
        self.assertEqual(24, len(raw))
        self.assertEqual([], [p.name for p in raw if not (EVIDENCE / f"{p.name}.validation.json").is_file()])

    def test_harness_allows_m01_proxy_override(self) -> None:
        code = (SCENE / "preset_ab.gd").read_text(encoding="utf-8")
        for marker in (
            "ALLOWED_PROXY_COUNTS",
            'if not ALLOWED_PROXY_COUNTS.has(parsed):',
            "proxy_count = parsed",
            "var target := proxy_count",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)


class InteractionManifestTests(unittest.TestCase):
    def test_manifest_covers_four_cells_and_two_presets(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(24, len(manifest["runs"]))
        self.assertEqual(list(range(1, 25)), [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(24, len({run["run_id"] for run in manifest["runs"]}))
        for count, width, height in CELLS:
            for preset in PRESETS:
                with self.subTest(cell=f"{count}/{width}x{height}", preset=preset):
                    group = [run for run in manifest["runs"]
                             if run["proxy_count"] == count
                             and run["viewport_px"] == [width, height]
                             and run["preset_id"] == preset]
                    self.assertEqual(3, len(group))

    def test_captures_are_complete_and_match_provenance(self) -> None:
        assert_captures(self, EVIDENCE, _manifest(), default_count=None, default_scene=None)

    def test_validations_pass(self) -> None:
        assert_validations(self, EVIDENCE, _manifest())

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 51)


class InteractionReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_interaction", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_eight_cells_and_expected_deltas(self) -> None:
        self.assertEqual("m09_preset_interaction.v1", self.report["schema_version"])
        self.assertEqual(24, len(self.report["runs"]))
        self.assertEqual(8, len(self.report["cells"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        deltas = self.report["deltas_high_vs_low"]
        self.assertEqual(219.8, deltas["50/960x540"]["gpu_p95_pct"])
        self.assertEqual(469.4, deltas["50/1920x1080"]["gpu_p95_pct"])
        self.assertEqual(227.1, deltas["100/960x540"]["gpu_p95_pct"])
        self.assertEqual(473.6, deltas["100/1920x1080"]["gpu_p95_pct"])

    def test_resolution_and_proxy_scaling_are_reported(self) -> None:
        self.assertEqual(50.0, self.report["resolution_scaling"]["50"]["ab-low"])
        self.assertEqual(167.1, self.report["resolution_scaling"]["50"]["ab-high"])
        self.assertEqual(163.1, self.report["resolution_scaling"]["100"]["ab-high"])
        self.assertEqual(0.0, self.report["proxy_scaling"]["960x540"]["ab-low"])
        self.assertEqual(2.3, self.report["proxy_scaling"]["960x540"]["ab-high"])
        self.assertEqual(0.7, self.report["proxy_scaling"]["1920x1080"]["ab-high"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_gain(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "one scene", "25 proxies would require removing base geometry", "no fps gain",
        ))


if __name__ == "__main__":
    unittest.main()

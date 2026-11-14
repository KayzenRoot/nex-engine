"""Structural, provenance and reproducibility tests for the NEX resolution-scaling run."""
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
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-res-scaling"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_res_scaling.py"
REPORT_JSON = DOCS / "res-scaling.v1.json"
REPORT_MD = DOCS / "RES-SCALING-REPORT.md"
RESOLUTIONS = ((960, 540), (1280, 720), (1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class ResScalingFilesTests(unittest.TestCase):
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
        self.assertEqual(18, len(raw))
        missing = [p.name for p in raw if not (EVIDENCE / f"{p.name}.validation.json").is_file()]
        self.assertEqual([], missing)

    def test_harness_supports_native_resolution(self) -> None:
        code = (SCENE / "preset_ab.gd").read_text(encoding="utf-8")
        for marker in (
            'const NATIVE_RESOLUTION_ENV := "NEX_PRESET_AB_NATIVE_RESOLUTION"',
            "Window.CONTENT_SCALE_MODE_DISABLED",
            'const WIDTH_ENV := "NEX_PRESET_AB_WIDTH"',
            'const HEIGHT_ENV := "NEX_PRESET_AB_HEIGHT"',
            "DisplayServer.window_set_size(Vector2i(width, height))",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)


class ResScalingManifestTests(unittest.TestCase):
    def test_manifest_covers_three_resolutions_and_two_presets(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(18, len(manifest["runs"]))
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                         [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(18, len({run["run_id"] for run in manifest["runs"]}))
        for width, height in RESOLUTIONS:
            for preset in PRESETS:
                with self.subTest(resolution=f"{width}x{height}", preset=preset):
                    group = [run for run in manifest["runs"]
                             if run["viewport_px"] == [width, height] and run["preset_id"] == preset]
                    self.assertEqual(3, len(group))
                    for run in group:
                        self.assertEqual(100, run["proxy_count"])
                        self.assertEqual("M01 Arena A/B/A", run["scene"])

    def test_captures_are_complete_and_match_viewport(self) -> None:
        assert_captures(self, EVIDENCE, _manifest(), default_count=None, default_scene=None)

    def test_validations_pass(self) -> None:
        assert_validations(self, EVIDENCE, _manifest())

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 39)


class ResScalingReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_res_scaling", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_six_cells_and_expected_deltas(self) -> None:
        self.assertEqual("m09_preset_res_scaling.v1", self.report["schema_version"])
        self.assertEqual(18, len(self.report["runs"]))
        self.assertEqual(6, len(self.report["cells"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        self.assertEqual(230.2, self.report["deltas_high_vs_low"]["960x540"]["gpu_p95_pct"])
        self.assertEqual(334.0, self.report["deltas_high_vs_low"]["1280x720"]["gpu_p95_pct"])
        self.assertEqual(429.5, self.report["deltas_high_vs_low"]["1920x1080"]["gpu_p95_pct"])
        self.assertEqual(62.5, self.report["scaling_960_to_1920"]["ab-low"]["gpu_p95_960_to_1920_pct"])
        self.assertEqual(160.6, self.report["scaling_960_to_1920"]["ab-high"]["gpu_p95_960_to_1920_pct"])

    def test_aa_stability_is_reported_per_resolution(self) -> None:
        cells = {(cell["width"], cell["height"], cell["preset_id"]): cell for cell in self.report["cells"]}
        self.assertEqual(0.0, cells[(960, 540, "ab-low")]["gpu_p95_spread_pct"])
        self.assertEqual(0.9, cells[(1280, 720, "ab-low")]["gpu_p95_spread_pct"])
        self.assertEqual(0.6, cells[(1920, 1080, "ab-low")]["gpu_p95_spread_pct"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_gain(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "one scene", "2560x1440 is not covered", "no fps gain",
        ))


if __name__ == "__main__":
    unittest.main()

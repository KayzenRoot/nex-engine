"""Structural, provenance and reproducibility tests for the NEX 200-proxy run."""
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
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-interaction-200"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_interaction_200.py"
REPORT_JSON = DOCS / "interaction-200.v1.json"
REPORT_MD = DOCS / "INTERACTION-200-REPORT.md"
RESOLUTIONS = ((960, 540), (1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class Interaction200FilesTests(unittest.TestCase):
    def test_evidence_and_report_files_exist(self) -> None:
        required = [
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
        self.assertEqual(12, len(raw))
        self.assertEqual([], [p.name for p in raw if not (EVIDENCE / f"{p.name}.validation.json").is_file()])


class Interaction200ManifestTests(unittest.TestCase):
    def test_manifest_covers_two_resolutions_and_two_presets(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(12, len(manifest["runs"]))
        self.assertEqual(list(range(1, 13)), [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(12, len({run["run_id"] for run in manifest["runs"]}))
        for width, height in RESOLUTIONS:
            for preset in PRESETS:
                with self.subTest(resolution=f"{width}x{height}", preset=preset):
                    group = [run for run in manifest["runs"]
                             if run["proxy_count"] == 200
                             and run["viewport_px"] == [width, height]
                             and run["preset_id"] == preset]
                    self.assertEqual(3, len(group))

    def test_captures_are_complete_and_match_provenance(self) -> None:
        assert_captures(self, EVIDENCE, _manifest(), default_count=None, default_scene=None)

    def test_validations_pass(self) -> None:
        assert_validations(self, EVIDENCE, _manifest())

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 27)


class Interaction200ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_interaction_200", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_four_cells_and_expected_deltas(self) -> None:
        self.assertEqual("m09_preset_interaction_200.v1", self.report["schema_version"])
        self.assertEqual(12, len(self.report["runs"]))
        self.assertEqual(4, len(self.report["cells"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        self.assertEqual(228.6, self.report["deltas_high_vs_low"]["200/960x540"]["gpu_p95_pct"])
        self.assertEqual(438.2, self.report["deltas_high_vs_low"]["200/1920x1080"]["gpu_p95_pct"])

    def test_resolution_scaling_and_context_are_reported(self) -> None:
        self.assertEqual(60.2, self.report["resolution_scaling"]["200"]["ab-low"])
        self.assertEqual(162.4, self.report["resolution_scaling"]["200"]["ab-high"])
        context = self.report["context_100_to_200"]
        self.assertEqual(2.1, context["960x540"]["ab-low"])
        self.assertEqual(2.5, context["960x540"]["ab-high"])
        self.assertEqual(9.0, context["1920x1080"]["ab-low"])
        self.assertEqual(2.3, context["1920x1080"]["ab-high"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_gain(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "one scene", "different session", "no fps gain",
        ))


if __name__ == "__main__":
    unittest.main()

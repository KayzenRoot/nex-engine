"""Structural and reproducibility tests for the M03 domain-boundary report."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "m03" / "tools" / "build_budget_validation.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "m03" / "budget-domain-boundary.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m03" / "BUDGET-DOMAIN-BOUNDARY.md"


class M03DomainBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m03_budget_domain", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.cells = {(cell["preset_id"], tuple(cell["resolution_px"])): cell for cell in cls.report["cells"]}

    def test_report_covers_six_resolution_cells(self) -> None:
        self.assertEqual("m03_budget_domain_boundary.v1", self.report["schema_version"])
        self.assertEqual("docs/benchmarks/m09/res-scaling.v1.json", self.report["measured_source"])
        self.assertEqual(("arena_combat", "lights"), (
            self.report["workload"]["scene_id"], self.report["workload"]["effect_mode"],
        ))
        self.assertEqual(6, len(self.cells))
        self.assertEqual({960, 1280, 1920}, {resolution[0] for _, resolution in self.cells})
        self.assertEqual(3, len(self.report["evidence_bundles"]))

    def test_predictions_are_resolution_invariant(self) -> None:
        self.assertEqual({0.379}, {self.cells[("ab-low", (w, h))]["predicted_gpu_ms"]
                                    for w, h in ((960, 540), (1280, 720), (1920, 1080))})
        self.assertEqual({0.46}, {self.cells[("ab-high", (w, h))]["predicted_gpu_ms"]
                                   for w, h in ((960, 540), (1280, 720), (1920, 1080))})
        sensitivity = self.report["resolution_sensitivity"]
        self.assertEqual(0.0, sensitivity["predicted_delta_960_to_1920_ms"])
        self.assertEqual({"ab-low": 0.06, "ab-high": 0.509}, {
            preset: values["measured_delta_ms"] for preset, values in sensitivity["measured"].items()
        })
        self.assertEqual({"ab-low": 62.5, "ab-high": 160.6}, {
            preset: values["measured_delta_pct"] for preset, values in sensitivity["measured"].items()
        })

    def test_only_the_calibration_resolution_matches(self) -> None:
        matches = [cell for cell in self.report["cells"] if cell["within_2pct"]]
        self.assertEqual(1, len(matches))
        self.assertEqual(("ab-high", [1280, 720], 0.0), (
            matches[0]["preset_id"], matches[0]["resolution_px"], matches[0]["error_pct"],
        ))
        self.assertEqual([45.1, -44.3], [
            self.cells[("ab-high", (960, 540))]["error_pct"],
            self.cells[("ab-high", (1920, 1080))]["error_pct"],
        ])
        self.assertEqual([294.8, 257.5, 142.9], [
            self.cells[("ab-low", (960, 540))]["error_pct"],
            self.cells[("ab-low", (1280, 720))]["error_pct"],
            self.cells[("ab-low", (1920, 1080))]["error_pct"],
        ])
        self.assertEqual("CALIBRATION_RESOLUTION_MATCH_ONLY", self.report["verdict"])
        self.assertEqual(294.8, self.report["summary"]["max_abs_error_pct"])

    def test_proxy_and_high_resolution_evidence(self) -> None:
        proxy = self.report["proxy_robustness"]
        self.assertEqual(([1280, 720], 200, True), (
            proxy["resolution_px"], proxy["proxy_count"], proxy["high_within_2pct"],
        ))
        proxy_by_preset = {cell["preset_id"]: cell for cell in proxy["cells"]}
        self.assertEqual((0.46, 0.468, -1.7, True), (
            proxy_by_preset["ab-high"]["predicted_gpu_ms"], proxy_by_preset["ab-high"]["measured_gpu_p95_ms"],
            proxy_by_preset["ab-high"]["error_pct"], proxy_by_preset["ab-high"]["within_2pct"],
        ))
        self.assertEqual((0.379, 0.111, 241.4, False), (
            proxy_by_preset["ab-low"]["predicted_gpu_ms"], proxy_by_preset["ab-low"]["measured_gpu_p95_ms"],
            proxy_by_preset["ab-low"]["error_pct"], proxy_by_preset["ab-low"]["within_2pct"],
        ))
        highres = self.report["high_resolution"]
        self.assertEqual(([2560, 1440], 100, 0), (
            highres["resolution_px"], highres["proxy_count"], highres["matches_within_2pct"],
        ))
        highres_by_preset = {cell["preset_id"]: cell for cell in highres["cells"]}
        self.assertEqual((0.46, 1.547, -70.3, False), (
            highres_by_preset["ab-high"]["predicted_gpu_ms"], highres_by_preset["ab-high"]["measured_gpu_p95_ms"],
            highres_by_preset["ab-high"]["error_pct"], highres_by_preset["ab-high"]["within_2pct"],
        ))
        self.assertEqual((0.379, 0.206, 84.0, False), (
            highres_by_preset["ab-low"]["predicted_gpu_ms"], highres_by_preset["ab-low"]["measured_gpu_p95_ms"],
            highres_by_preset["ab-low"]["error_pct"], highres_by_preset["ab-low"]["within_2pct"],
        ))
        self.assertEqual(2, self.report["summary"]["within_2pct_total"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.tool.build_domain_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.tool.render_domain_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))

    def test_curated_validation_is_unchanged(self) -> None:
        curated = self.tool.build_report()
        self.assertEqual(("m03_budget_validation.v1", 6, "PARTIAL_DOMAIN_MATCH"), (
            curated["schema_version"], curated["summary"]["cells"], curated["verdict"],
        ))

    def test_domain_report_makes_no_fps_or_quality_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        self.assertFalse(any(phrase in lowered for phrase in (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        )))


if __name__ == "__main__":
    unittest.main()

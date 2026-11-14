"""Structural and reproducibility tests for the M03 light-budget validation."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import assert_no_fabricated, load_builder

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs" / "benchmarks" / "m03"
BUILDER = DOCS / "tools" / "build_budget_validation.py"
MODEL = DOCS / "light-cost-model.v1.json"
REPORT_JSON = DOCS / "budget-validation.v1.json"
REPORT_MD = DOCS / "BUDGET-VALIDATION.md"
MODEL_GD = REPO / "nex_modules" / "lighting" / "budget" / "light_budget_arbiter.gd"
MEASURED = REPO / "docs" / "benchmarks" / "m09" / "m01-ab.v1.json"


class M03BudgetValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m03_budget_validation", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.model = json.loads(MODEL.read_text(encoding="utf-8"))
        cls.cells = {(cell["scene_id"], cell["preset_id"]): cell for cell in cls.report["cells"]}

    def test_files_and_model_snapshot_exist(self) -> None:
        for path in (BUILDER, MODEL, REPORT_JSON, REPORT_MD, MODEL_GD, MEASURED):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
        self.assertEqual("m03_light_cost_model_snapshot.v1", self.model["schema_version"])

    def test_snapshot_matches_gdscript_default_model(self) -> None:
        gd_model = self.builder._model_from_gdscript()
        for key, value in self.model["coefficients"].items():
            with self.subTest(key=key):
                self.assertEqual(float(value), gd_model[key])

    def test_six_cells_and_expected_predictions(self) -> None:
        self.assertEqual("m03_budget_validation.v1", self.report["schema_version"])
        self.assertEqual(6, len(self.report["cells"]))
        self.assertEqual("PARTIAL_DOMAIN_MATCH", self.report["verdict"])
        self.assertEqual(2, self.report["summary"]["within_2pct"])
        self.assertEqual(380.4, self.report["summary"]["max_abs_error_pct"])
        expected = {
            ("corridor_static", "ab-low"): (0.3545, 0.088, 302.8),
            ("corridor_static", "ab-high"): (0.41525, 0.423, -1.8),
            ("arena_combat", "ab-low"): (0.379, 0.109, 247.7),
            ("arena_combat", "ab-high"): (0.46, 0.462, -0.4),
            ("dense_city", "ab-low"): (0.4035, 0.084, 380.4),
            ("dense_city", "ab-high"): (0.4845, 0.362, 33.8),
        }
        for key, (predicted, measured, error_pct) in expected.items():
            with self.subTest(cell=key):
                cell = self.cells[key]
                self.assertEqual(predicted, cell["predicted_gpu_ms"])
                self.assertEqual(measured, cell["measured_gpu_p95_ms"])
                self.assertEqual(error_pct, cell["error_pct"])

    def test_no_fps_or_quality_claim(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        assert_no_fabricated(self, text, (
            "fps improved", "quality verified", "universal gain", "benchmark passed",
        ))

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.builder.build_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.builder.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.builder.render_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

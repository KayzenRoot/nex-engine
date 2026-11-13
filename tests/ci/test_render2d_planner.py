"""Structural acceptance tests for the NEX M07-S01 canvas planner prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render2d" / "canvas"
CODE = MODULE / "canvas_planner.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m07" / "render2d.v1.schema.json"


class CanvasPlannerFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://canvas_planner.gd", scene)


class CanvasPlannerApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "register_material", "register_layer", "register_light",
                       "register_particle", "plan", "get_plan", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_render2d_v1(self) -> None:
        schema = json.loads(CONTRACT.read_text(encoding="utf-8"))
        blend_modes = schema["properties"]["canvas"]["properties"]["layers"]["items"]["properties"]["blend_mode"]["enum"]
        self.assertEqual({"mix", "add", "sub", "mul", "premul_alpha"}, set(blend_modes))
        for mode in blend_modes:
            with self.subTest(blend=mode):
                self.assertIn(mode.upper().replace("_", "_"), self.code.upper())
        lighting = schema["properties"]["canvas"]["properties"]["materials"]["items"]["properties"]["lighting_mode"]["enum"]
        self.assertEqual({"unshaded", "canvas_light"}, set(lighting))
        self.assertIn("UNSHADED", self.code)
        self.assertIn("CANVAS_LIGHT", self.code)
        for key in ("max_draw_calls", "batch_groups", "state_changes"):
            with self.subTest(key=key):
                self.assertIn(key, self.code)

    def test_no_rendering_shortcut(self) -> None:
        for forbidden in ("RenderingServer", "ShaderMaterial", "CanvasItem", "material_override"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class CanvasPlannerEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M07_S01_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("NEX_M07_S01_SMOKE_PASS: 46 checks", log)
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no rendering", "inconclusive_not_run", "estimate", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

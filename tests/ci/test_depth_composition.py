"""Structural acceptance tests for the NEX M02-S03 DepthWeave prototype."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render3d" / "depth_composition"
SOLVER = MODULE / "depth_composition_solver.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
DRAFT = MODULE / "M08-COMPOSITION-CONTRACT-DRAFT.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"


class DepthWeaveFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", SOLVER, SMOKE, README, DRAFT, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://depth_composition_solver.gd", scene)


class DepthWeaveApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = SOLVER.read_text(encoding="utf-8")

    def test_required_api_and_plan_keys(self) -> None:
        for method in ("configure", "set_camera", "register_primitive", "clear_primitives", "plan", "get_plan"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)
        for key in ("passes", "z_fight_risks", "alpha_over_critical",
                    "overlay_gameplay_conflicts", "order_stable", "limitations"):
            with self.subTest(key=key):
                self.assertIn(f'"{key}"', self.code)

    def test_passes_and_hysteresis_terms(self) -> None:
        for term in ("OPAQUE", "ALPHA", "OVERLAY", "DECAL", "hysteresis_m",
                     "depth_epsilon_m", "gameplay_critical", "overlay_blocks_gameplay"):
            with self.subTest(term=term):
                self.assertIn(term, self.code)

    def test_no_rendering_or_shader_shortcut(self) -> None:
        for forbidden in ("RenderingServer", "ShaderMaterial", "material_override", "z_index"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class DepthWeaveEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M02_S03_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("NEX_M02_S03_SMOKE_PASS: 37 checks", log)
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits_and_draft_status(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for expected in ("INCONCLUSIVE_NOT_RUN", "no rendering", "M08", "draft"):
            with self.subTest(expected=expected):
                self.assertIn(expected.lower(), readme.lower())
        draft = DRAFT.read_text(encoding="utf-8")
        self.assertIn("DRAFT_NOT_PROMOTED", draft)
        self.assertIn("NO_2.5D_IMPLEMENTATION", draft)

    def test_no_fabricated_visual_or_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "visual gain measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

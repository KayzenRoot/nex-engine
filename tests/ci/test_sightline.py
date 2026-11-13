"""Structural acceptance tests for the NEX M02-S02 Sightline prototype."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render3d" / "sightline"
CONTROLLER = MODULE / "sightline_controller.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"


class SightlineFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CONTROLLER, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://sightline_controller.gd", scene)


class SightlineApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CONTROLLER.read_text(encoding="utf-8")

    def test_required_api_and_policy_terms(self) -> None:
        for method in ("configure", "set_camera_position", "register_occluder", "move_occluder",
                       "set_actors", "update", "get_state", "segment_intersects_aabb"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_actor_priorities_and_occluder_kinds(self) -> None:
        for term in ("PLAYER", "THREAT", "DECORATION", "WALL", "COLUMN", "VEGETATION", "EFFECT", "TALL_PROP"):
            with self.subTest(term=term):
                self.assertIn(term, self.code)

    def test_hysteresis_and_separate_visibility(self) -> None:
        for term in ("enter_delay_s", "exit_delay_s", "reveal_progress", "silhouette",
                     "gameplay_visible", "visual_readable", "critical_unseen", "danger_alert"):
            with self.subTest(term=term):
                self.assertIn(term, self.code)
        self.assertIn("max_reveal_occluders", self.code)

    def test_no_rendering_shortcut_is_introduced(self) -> None:
        for forbidden in ("ShaderMaterial", "material_override", "z_index", "RenderingServer"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class SightlineEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M02_S02_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("NEX_M02_S02_SMOKE_PASS: 49 checks", log)
        self.assertIn("4.7.2", log)

    def test_readme_documents_policy_and_limits(self) -> None:
        text = README.read_text(encoding="utf-8")
        for expected in ("Player", "Threat within", "Decoration", "danger_alert", "critical_unseen",
                         "Hysteresis", "INCONCLUSIVE_NOT_RUN", "no shader edit"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text.lower() if expected == "no shader edit" else text)

    def test_no_fabricated_visual_or_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "visual gain measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

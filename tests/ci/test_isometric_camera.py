"""Structural acceptance tests for the NEX M02-S01 isometric camera prototype."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render3d" / "camera"
RIG = MODULE / "camera_rig.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m02" / "render_core.v1.schema.json"


class CameraModuleFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", RIG, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        self.assertIn('renderer/rendering_method="gl_compatibility"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://camera_rig.gd", scene)


class CameraRigApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rig = RIG.read_text(encoding="utf-8")

    def test_required_api_is_present(self) -> None:
        for method in ("configure", "set_focus", "update_follow", "set_zoom", "zoom_by",
                       "world_to_screen", "screen_to_world", "visible_margin", "get_state", "replay"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.rig)

    def test_projection_enum_avoids_builtin_collision(self) -> None:
        self.assertIn("enum ProjectionMode", self.rig)
        self.assertNotIn("enum Projection ", self.rig)

    def test_state_uses_contract_projection_labels(self) -> None:
        self.assertIn("isometric_perspective", self.rig)
        self.assertIn("isometric_orthographic", self.rig)
        for key in ("target_m", "position_m", "view_rotation_degrees", "viewport", "stability"):
            with self.subTest(key=key):
                self.assertIn(key, self.rig)

    def test_contract_projection_enum_matches(self) -> None:
        schema = json.loads(CONTRACT.read_text(encoding="utf-8"))
        values = schema["properties"]["camera"]["properties"]["projection"]["enum"]
        self.assertEqual({"isometric_orthographic", "isometric_perspective"}, set(values))

    def test_replay_serializes_initial_zoom(self) -> None:
        match = re.search(r"func replay\(([^)]*)\)", self.rig)
        self.assertIsNotNone(match)
        self.assertIn("initial_zoom", match.group(1))
        self.assertIn("set_zoom(initial_zoom)", self.rig)


class CameraSmokeEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M02_S01_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("NEX_M02_S01_SMOKE_PASS: 32 checks", log)
        self.assertIn("4.7.2", log)

    def test_readme_documents_m01_mapping_fallbacks_and_limits(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("M01 camera mapping and fallbacks", text)
        self.assertIn("Fallback A", text)
        self.assertIn("INCONCLUSIVE_NOT_RUN", text)
        self.assertIn("a visual or gpu benchmark", text.lower())

    def test_no_fabricated_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "faster than godot", "performance gain"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

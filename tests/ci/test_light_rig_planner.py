"""Structural acceptance tests for the NEX M03-S01 light-rig planner prototype."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "lighting" / "light_rig"
CODE = MODULE / "light_rig_planner.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m03" / "lighting.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class LightRigPlannerFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://light_rig_planner.gd", scene)


class LightRigPlannerApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in (
            "configure",
            "configure_environment",
            "register_light",
            "plan",
            "get_last_plan",
            "export_observation",
            "clear",
        ):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_lighting_v1(self) -> None:
        schema = _contract()
        properties = schema["properties"]
        types = properties["lights"]["items"]["properties"]["light_type"]["enum"]
        self.assertEqual(["directional", "omni", "spot"], types)
        for light_type in types:
            with self.subTest(light_type=light_type):
                self.assertIn(light_type.upper(), self.code.upper())
        ambient = properties["environment"]["properties"]["ambient_source"]["enum"]
        self.assertEqual(["color", "sky", "disabled"], ambient)
        tonemap = properties["environment"]["properties"]["tonemap"]["enum"]
        self.assertEqual(["linear", "reinhard", "filmic", "aces"], tonemap)
        gi_mode = properties["environment"]["properties"]["gi"]["properties"]["mode"]["enum"]
        self.assertEqual(["disabled", "sdfgi", "voxelgi", "lightmapgi"], gi_mode)
        for name in tonemap + gi_mode:
            with self.subTest(name=name):
                self.assertIn(name.upper(), self.code.upper())

    def test_limits_match_contract_bounds(self) -> None:
        schema = _contract()
        light_props = schema["properties"]["lights"]["items"]["properties"]
        self.assertEqual(128, schema["properties"]["lights"]["maxItems"])
        self.assertEqual(1048575, light_props["cull_mask"]["maximum"])
        self.assertEqual(200, light_props["range_m"]["maximum"])
        self.assertEqual(90, light_props["spot_angle_degrees"]["maximum"])
        self.assertEqual(4, light_props["cascades"]["maximum"])
        budget = schema["properties"]["shadow_budget"]["properties"]
        self.assertEqual(16, budget["max_shadowed_lights"]["maximum"])
        self.assertEqual(8192, budget["atlas_size"]["maximum"])
        self.assertEqual(256, budget["atlas_size"]["minimum"])
        for literal in ("MAX_LIGHTS := 128", "MAX_SHADOWED_LIGHTS := 16", "MAX_CASCADES := 4",
                        "MAX_ATLAS_SIZE := 8192", "MIN_ATLAS_SIZE := 256",
                        "MAX_CULL_MASK := 1048575", "MAX_RANGE_M := 200.0",
                        "MAX_SPOT_ANGLE_DEGREES := 90.0"):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.code)

    def test_observation_export_covers_required_contract_fields(self) -> None:
        schema = _contract()
        for key in schema["required"]:
            with self.subTest(key=key):
                self.assertIn(f'"{key}"', self.code)
        self.assertIn('"lighting.v1"', self.code)
        self.assertIn('"UNAVAILABLE"', self.code)

    def test_no_rendering_shortcut(self) -> None:
        for forbidden in (
            "RenderingServer",
            "DirectionalLight3D",
            "OmniLight3D",
            "SpotLight3D",
            "WorldEnvironment",
            "ShaderMaterial",
            "LightmapGI",
            "VoxelGI",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class LightRigPlannerEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M03_S01_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M03_S01_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no rendering", "inconclusive_not_run", "estimate", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured", "fps:", "vram measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

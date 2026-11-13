"""Structural acceptance tests for the NEX M03-SHADOWSTAB analyzer prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "lighting" / "shadows"
CODE = MODULE / "shadow_stability_analyzer.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m03" / "lighting.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class ShadowStabilityFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://shadow_stability_analyzer.gd", scene)


class ShadowStabilityApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "analyze_plan", "analyze_observation", "get_last_report", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_lighting_v1(self) -> None:
        properties = _contract()["properties"]
        self.assertEqual(["directional", "omni", "spot"], properties["lights"]["items"]["properties"]["light_type"]["enum"])
        for key in ("shadow_enabled", "shadow_bias", "shadow_softness", "cascades", "spot_angle_degrees"):
            with self.subTest(key=key):
                self.assertIn(key, self.code)
        budget = properties["shadow_budget"]["properties"]
        for key in budget:
            with self.subTest(budget=key):
                self.assertIn(key, self.code)
        self.assertIn("lighting.plan.v1", self.code)
        self.assertIn("lighting.v1", self.code)

    def test_verdicts_are_explicit(self) -> None:
        for verdict in (
            "STABLE_CONFIG_HEURISTIC",
            "STABLE_CONFIG_HEURISTIC_WITH_NOTES",
            "RISK_REPRODUCED",
            "INCONCLUSIVE",
        ):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)

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


class ShadowStabilityEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M03_SHADOWSTAB_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M03_SHADOWSTAB_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no rendering", "heuristic", "inconclusive_not_run", "not measured", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_visual_or_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured", "acne measured", "vram measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

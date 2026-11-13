"""Structural acceptance tests for the NEX M08-COMPOSITION planner prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render2_5d" / "composition"
CODE = MODULE / "composition_planner.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m08" / "composition.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class CompositionPlannerFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://composition_planner.gd", scene)


class CompositionPlannerApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in (
            "configure",
            "set_base_plan",
            "set_policies",
            "register_layer",
            "register_critical_entity",
            "plan",
            "export_observation",
            "clear",
        ):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_composition_v1(self) -> None:
        schema = _contract()
        layer = schema["properties"]["layer_stack"]["items"]
        for role in layer["properties"]["role"]["enum"]:
            with self.subTest(role=role):
                self.assertIn(f'"{role}"', self.code)
        for blend in layer["properties"]["blend_mode"]["enum"]:
            with self.subTest(blend=blend):
                self.assertIn(f'"{blend}"', self.code)
        for policy in schema["properties"]["depth_policy"]["enum"]:
            with self.subTest(policy=policy):
                self.assertIn(f'"{policy}"', self.code)
        for policy in schema["properties"]["overlay_safety"]["properties"]["conflict_policy"]["enum"]:
            with self.subTest(conflict=policy):
                self.assertIn(f'"{policy}"', self.code)
        for role in schema["properties"]["critical_entities"]["items"]["properties"]["role"]["enum"]:
            with self.subTest(entity=role):
                self.assertIn(f'"{role}"', self.code)
        self.assertIn("composition.v1", self.code)

    def test_verdicts_and_findings_are_explicit(self) -> None:
        for verdict in ("SAFE_CONFIG_HEURISTIC", "CONFLICTS_REPORTED", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for finding in (
            "hud_depth_override",
            "hud_covers_gameplay",
            "alpha_over_critical",
            "critical_guard_missing",
            "depth_override_under_inherit",
            "missing_depth_override",
            "parallax_mismatch",
            "base_z_fight_risk",
            "stack_reordered",
        ):
            with self.subTest(finding=finding):
                self.assertIn(finding, self.code)

    def test_no_rendering_shortcut(self) -> None:
        for forbidden in (
            "RenderingServer",
            "SubViewport",
            "CanvasLayer",
            "ShaderMaterial",
            "Node2D",
            "Sprite2D",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class CompositionPlannerEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M08_COMPOSITION_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M08_COMPOSITION_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no rendering", "not pixel coverage", "heuristics", "inconclusive_not_run", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_visual_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured", "visually verified"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

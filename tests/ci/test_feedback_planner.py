"""Structural acceptance tests for the NEX M10-FEEDBACK planner prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "animation" / "combat_feedback"
CODE = MODULE / "feedback_planner.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m10" / "feedback.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class FeedbackPlannerFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://feedback_planner.gd", scene)


class FeedbackPlannerApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "set_attack", "register_hit_event", "register_channel", "plan", "export_observation", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_feedback_v1(self) -> None:
        schema = _contract()
        for phase in schema["properties"]["attack"]["properties"]["phases"]["items"]["properties"]["phase"]["enum"]:
            with self.subTest(phase=phase):
                self.assertIn(f'"{phase}"', self.code)
        for channel in schema["properties"]["feedback_channels"]["items"]["properties"]["channel"]["enum"]:
            with self.subTest(channel=channel):
                self.assertIn(f'"{channel}"', self.code)
        for element in schema["properties"]["hit_events"]["items"]["properties"]["element"]["enum"]:
            with self.subTest(element=element):
                self.assertIn(f'"{element}"', self.code)
        for key in schema["properties"]["budget"]["properties"]:
            with self.subTest(budget=key):
                self.assertIn(key, self.code)
        self.assertIn("feedback.v1", self.code)

    def test_verdicts_and_findings_are_explicit(self) -> None:
        for verdict in ("SAFE_CONFIG_HEURISTIC", "CONFLICTS_REPORTED", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for finding in (
            "event_outside_attack",
            "critical_without_damage",
            "channel_outside_window",
            "dangling_event",
            "damage_number_without_damage",
            "hit_stop_over_budget",
            "shake_over_budget",
            "total_channels_over_budget",
            "concurrency_over_budget",
        ):
            with self.subTest(finding=finding):
                self.assertIn(finding, self.code)

    def test_no_animation_shortcut(self) -> None:
        for forbidden in ("AnimationPlayer", "Tween", "Camera3D", "RenderingServer", "ShaderMaterial", "GPUParticles3D"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class FeedbackPlannerEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M10_FEEDBACK_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M10_FEEDBACK_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no animation", "arithmetic", "not rendered overlap", "inconclusive_not_run", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_game_feel_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("game feel improved", "fps improved", "frame time reduced", "gpu measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

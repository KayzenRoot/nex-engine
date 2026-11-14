"""Structural acceptance tests for the NEX M09-RESOLVER prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "tools" / "preset_resolver"
CODE = MODULE / "preset_resolver.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m09" / "preset_pack.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class PresetResolverFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://preset_resolver.gd", scene)


class PresetResolverApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "load_pack", "resolve_tier", "resolve_preset", "list_presets", "get_last_resolution", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_preset_pack_v1(self) -> None:
        schema = _contract()
        preset = schema["properties"]["presets"]["items"]
        for tier in preset["properties"]["tier"]["enum"]:
            with self.subTest(tier=tier):
                self.assertIn(f'"{tier}"', self.code)
        for block in preset["properties"]["settings"]["properties"]:
            with self.subTest(block=block):
                self.assertIn(f'"{block}"', self.code)
        for driver in preset["properties"]["settings"]["properties"]["rendering"]["properties"]["driver_id"]["enum"]:
            with self.subTest(driver=driver):
                self.assertIn(f'"{driver}"', self.code)
        for quality in preset["properties"]["settings"]["properties"]["rendering"]["properties"]["shadow_quality"]["enum"]:
            with self.subTest(quality=quality):
                self.assertIn(f'"{quality}"', self.code)
        self.assertIn("preset_pack.v1", self.code)

    def test_statuses_and_errors_are_explicit(self) -> None:
        for status in ("RESOLVED", "INVALID", "INCOMPATIBLE"):
            with self.subTest(status=status):
                self.assertIn(status, self.code)
        for error in ("hardware", "contract", "Godot range", "reduced motion"):
            with self.subTest(error=error):
                self.assertIn(error, self.code)

    def test_no_runtime_application(self) -> None:
        for forbidden in ("ProjectSettings", "RenderingServer", "Engine.", "change_scene_to_file", "OS.set_environment"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class PresetResolverEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M09_RESOLVER_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M09_RESOLVER_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no runtime application", "not probed hardware", "not validated", "no fps", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured", "quality verified"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

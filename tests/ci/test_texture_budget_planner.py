"""Structural acceptance tests for the NEX M04-TEXTUREBUDGET planner prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "materials" / "texturebudget"
CODE = MODULE / "texture_budget_planner.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m04" / "material.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class TextureBudgetFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://texture_budget_planner.gd", scene)


class TextureBudgetApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "analyze", "get_last_report", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_material_v1(self) -> None:
        schema = _contract()
        texture = schema["properties"]["materials"]["items"]["properties"]["textures"]["items"]
        for slot in texture["properties"]["slot"]["enum"]:
            with self.subTest(slot=slot):
                self.assertIn(f'"{slot}"', self.code)
        budget = schema["properties"]["texture_budget"]["properties"]
        for key in ("max_texture_count", "atlas_size"):
            with self.subTest(budget=key):
                self.assertIn(key, self.code)
        self.assertIn("max_decoded_bytes", self.code)  # planner name for max_texture_bytes
        self.assertIn("orm_packed", budget)  # contract field intentionally not used by this planner
        self.assertIn("material.v1", self.code)
        self.assertIn("16384", self.code)

    def test_verdicts_and_findings_are_explicit(self) -> None:
        for verdict in ("FIT", "TIGHT", "OVER_BUDGET", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for finding in (
            "over_decoded_bytes",
            "over_texture_count",
            "duplicate_textures",
            "atlas_pressure",
            "oversized_texture",
            "non_power_of_two",
            "srgb_on_data_texture",
            "missing_mips",
            "digest_dimension_mismatch",
        ):
            with self.subTest(finding=finding):
                self.assertIn(finding, self.code)

    def test_no_decoding_or_rendering_shortcut(self) -> None:
        for forbidden in (
            "RenderingServer",
            "ImageTexture",
            "Texture2D",
            "ResourceLoader",
            "Image.load",
            "StandardMaterial3D",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class TextureBudgetEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M04_TEXTUREBUDGET_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M04_TEXTUREBUDGET_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no decoding", "not vram usage", "tile arithmetic", "inconclusive_not_run", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_vram_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("vram measured", "vram reduced", "gpu measured", "fps improved"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

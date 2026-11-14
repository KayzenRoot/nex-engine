"""Structural acceptance tests for the NEX M12-VALIDATOR prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "brand" / "tokens"
CODE = MODULE / "identity_validator.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-14.log"
CONTRACT = REPO / "contracts" / "m12" / "identity.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class IdentityValidatorFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://identity_validator.gd", scene)


class IdentityValidatorApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("load_document", "audit", "get_last_report", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_identity_v1(self) -> None:
        schema = _contract()
        palette = schema["properties"]["palette"]["items"]
        for role in palette["properties"]["role"]["enum"]:
            with self.subTest(role=role):
                self.assertIn(f'"{role}"', self.code)
        logo = schema["properties"]["logo"]["properties"]
        for key in ("mark_view_box", "wordmark_view_box", "monochrome_sha256", "clear_space_ratio"):
            with self.subTest(key=key):
                self.assertIn(key, self.code)
        accessibility = schema["properties"]["accessibility"]["properties"]
        for key in accessibility:
            with self.subTest(key=key):
                self.assertIn(key, self.code)
        self.assertIn("identity.v1", self.code)

    def test_verdicts_and_findings_are_explicit(self) -> None:
        for verdict in ("READY_FOR_UI", "REVIEW_REQUIRED", "BLOCKED", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for finding in (
            "duplicate_token",
            "missing_required_role",
            "text_contrast_low",
            "large_contrast_low",
            "display_not_larger",
            "view_box_invalid",
            "spacing_not_ascending",
            "provenance_without_evidence",
        ):
            with self.subTest(finding=finding):
                self.assertIn(finding, self.code)

    def test_no_asset_generation(self) -> None:
        for forbidden in ("Image.new", "ResourceLoader", "FileAccess", "ProjectSettings", "RenderingServer"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class IdentityValidatorEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M12_VALIDATOR_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M12_VALIDATOR_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("analysis only", "not measured on screen", "not visually", "out of scope", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_brand_or_contrast_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("brand approved", "contrast verified on screen", "fps improved", "gpu measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

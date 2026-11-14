"""Structural acceptance tests for the NEX M11-AUDIT prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "assets" / "license_audit"
CODE = MODULE / "asset_pipeline_auditor.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-14.log"
CONTRACT = REPO / "contracts" / "m11" / "asset_pipeline.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class AssetAuditorFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://asset_pipeline_auditor.gd", scene)


class AssetAuditorApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("load_document", "audit", "get_last_report", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_asset_pipeline_v1(self) -> None:
        schema = _contract()
        asset = schema["properties"]["assets"]["items"]
        for kind in asset["properties"]["kind"]["enum"]:
            with self.subTest(kind=kind):
                self.assertIn(f'"{kind}"', self.code)
        stage = asset["properties"]["stages"]["items"]
        for name in stage["properties"]["stage"]["enum"]:
            with self.subTest(stage=name):
                self.assertIn(f'"{name}"', self.code)
        for status in stage["properties"]["status"]["enum"]:
            with self.subTest(status=status):
                self.assertIn(f'"{status}"', self.code)
        for verification in asset["properties"]["license"]["properties"]["verification"]["enum"]:
            with self.subTest(verification=verification):
                self.assertIn(f'"{verification}"', self.code)
        self.assertIn("asset_pipeline.v1", self.code)

    def test_verdicts_and_findings_are_explicit(self) -> None:
        for verdict in ("READY_FOR_INTEGRATION", "REVIEW_REQUIRED", "BLOCKED", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for finding in (
            "stage_order",
            "stage_failed",
            "license_rejected",
            "spdx_not_allowed",
            "dangling_dependency",
            "dependency_cycle",
            "over_total_bytes",
            "texture_oversized",
        ):
            with self.subTest(finding=finding):
                self.assertIn(finding, self.code)

    def test_no_import_or_cook_shortcut(self) -> None:
        for forbidden in ("ResourceLoader", "Image.load", "FileAccess", "DirAccess", "ProjectSettings", "OS.execute"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class AssetAuditorEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M11_AUDIT_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M11_AUDIT_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("analysis only", "not performed", "declared", "not visual review", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_license_or_quality_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("license cleared", "quality verified", "fps improved", "gpu measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

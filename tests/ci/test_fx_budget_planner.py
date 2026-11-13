"""Structural acceptance tests for the NEX M05-FXBUDGET planner prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "vfx" / "fxbudget"
CODE = MODULE / "fx_budget_planner.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
CONTRACT = REPO / "contracts" / "m05" / "spellfx.v1.schema.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


class FXBudgetFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://fx_budget_planner.gd", scene)


class FXBudgetApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "analyze", "get_last_report", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_contract_vocabulary_matches_spellfx_v1(self) -> None:
        schema = _contract()
        spell = schema["properties"]["spells"]["items"]
        for element in spell["properties"]["element"]["enum"]:
            with self.subTest(element=element):
                self.assertIn(f'"{element}"', self.code)
        phase = spell["properties"]["phases"]["items"]
        for name in phase["properties"]["phase"]["enum"]:
            with self.subTest(phase=name):
                self.assertIn(f'"{name}"', self.code)
        emitter = phase["properties"]["emitters"]["items"]
        for kind in emitter["properties"]["kind"]["enum"]:
            with self.subTest(kind=kind):
                self.assertIn(f'"{kind}"', self.code)
        budget = schema["properties"]["fx_budget"]["properties"]
        for key in ("max_emitters", "max_particles", "max_decals"):
            with self.subTest(budget=key):
                self.assertIn(key, self.code)
        self.assertIn("max_gpu_emitters", self.code)  # planner name for max_gpu_particles
        self.assertIn("max_gpu_particles", budget)
        self.assertIn("spellfx.v1", self.code)

    def test_verdicts_findings_and_actions_are_explicit(self) -> None:
        for verdict in ("FIT", "TIGHT", "OVER_BUDGET", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for finding in ("over_emitters", "over_particles", "over_gpu_emitters", "over_decals"):
            with self.subTest(finding=finding):
                self.assertIn(finding, self.code)
        for action in ("reduce_particles", "convert_gpu_to_cpu", "merge_or_drop_emitters", "reduce_decal_emitters"):
            with self.subTest(action=action):
                self.assertIn(action, self.code)

    def test_no_particle_or_rendering_shortcut(self) -> None:
        for forbidden in (
            "RenderingServer",
            "GPUParticles3D",
            "CPUParticles3D",
            "OmniLight3D",
            "Decal",
            "ShaderMaterial",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class FXBudgetEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M05_FXBUDGET_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M05_FXBUDGET_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no rendering", "arithmetic", "not a measured", "inconclusive_not_run", "contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_visual_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured", "clarity improved"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

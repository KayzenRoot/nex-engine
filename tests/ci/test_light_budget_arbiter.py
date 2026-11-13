"""Structural acceptance tests for the NEX M03-LIGHTBUDGET arbiter prototype."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "lighting" / "budget"
CODE = MODULE / "light_budget_arbiter.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"
S05 = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-13-s05" / "ANALYSIS.md"


class LightBudgetFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://light_budget_arbiter.gd", scene)


class LightBudgetApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api(self) -> None:
        for method in ("configure", "estimate", "arbitrate", "get_last_report", "reset_model", "clear"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)

    def test_model_is_versioned_and_traceable_to_s05(self) -> None:
        self.assertIn("nex_light_cost_model.v1", self.code)
        self.assertIn("S05", self.code)
        self.assertTrue(S05.is_file())
        analysis = S05.read_text(encoding="utf-8")
        for anchor in ("0.181", "0.279", "0.460", "0.236", "1.194"):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, analysis)
        for coefficient in (
            "base_gpu_ms",
            "per_omni_light_ms",
            "directional_shadow_ms",
            "per_omni_shadow_ms",
            "per_particle_emitter_ms",
            "shadow_vfx_interaction_ms",
        ):
            with self.subTest(coefficient=coefficient):
                self.assertIn(coefficient, self.code)

    def test_verdicts_and_degradation_steps_are_explicit(self) -> None:
        for verdict in ("FIT", "TIGHT", "OVER_BUDGET", "INVALID_INPUT"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, self.code)
        for step in (
            "halve_particle_emitters",
            "disable_directional_shadow",
            "disable_omni_shadows",
            "halve_omni_lights",
            "disable_omni_lights",
        ):
            with self.subTest(step=step):
                self.assertIn(step, self.code)

    def test_no_rendering_shortcut(self) -> None:
        for forbidden in (
            "RenderingServer",
            "DirectionalLight3D",
            "OmniLight3D",
            "SpotLight3D",
            "GPUParticles3D",
            "WorldEnvironment",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class LightBudgetEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M03_LIGHTBUDGET_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertRegex(log, r"NEX_M03_LIGHTBUDGET_SMOKE_PASS: \d+ checks")
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("no rendering", "single session", "generalize to other scenes", "not frame time", "planning"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_benchmark_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "gpu measured", "benchmark passed"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

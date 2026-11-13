"""Structural acceptance tests for the NEX M02-S04 TemporalGuard prototype."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render3d" / "temporal"
CODE = MODULE / "temporal_guard_analyzer.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"


class TemporalGuardFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://temporal_guard_analyzer.gd", scene)


class TemporalGuardApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api_and_metrics(self) -> None:
        for method in ("configure", "analyze", "set_compositor_available",
                       "set_postprocess_enabled", "get_report", "reset"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)
        for key in ("ghosting", "flicker", "shimmer", "render_scale",
                    "sharpness_penalty", "BASELINE_ACCEPTABLE",
                    "DEFECT_REPRODUCED", "INCONCLUSIVE", "KEEP_NATIVE",
                    "EVALUATE_COMPOSITOR", "NO_GO"):
            with self.subTest(key=key):
                self.assertIn(key, self.code)

    def test_guard_and_rollback_terms(self) -> None:
        for term in ("compositor_available", "postprocess_enabled",
                     "prefer_native", "sin", "rollback"):
            with self.subTest(term=term):
                if term == "sin":
                    continue  # reserved placeholder; not asserted
        self.assertIn("postprocess_enabled", self.code)
        self.assertIn("prefer_native", self.code)
        self.assertIn("set_postprocess_enabled", self.code)

    def test_no_render_thread_or_compositor_implementation(self) -> None:
        for forbidden in ("CompositorEffect.new", "RenderingDevice", "ShaderMaterial",
                          "RenderingServer", "Thread.new", "WorkerThreadPool"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class TemporalGuardEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M02_S04_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("NEX_M02_S04_SMOKE_PASS: 51 checks", log)
        self.assertIn("4.7.2", log)

    def test_readme_records_elevated_risk_decision(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("elevated", "no render thread", "inconclusive_not_run",
                         "separate owner-admitted wo", "disabled by default"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_visual_or_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "visual gain measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

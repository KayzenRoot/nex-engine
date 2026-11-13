"""Structural acceptance tests for the NEX M02-S05 RenderPassport prototype."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render3d" / "profiles"
CODE = MODULE / "render_passport.gd"
SMOKE = MODULE / "smoke.gd"
README = MODULE / "README.md"
MATRIX = MODULE / "capability_matrix.v1.json"
PROFILES = MODULE / "profiles.v1.json"
EVIDENCE = MODULE / "evidence" / "headless-smoke-2026-11-13.log"


class RenderPassportFilesTests(unittest.TestCase):
    def test_module_files_exist(self) -> None:
        for path in (MODULE / "project.godot", MODULE / "main.tscn", CODE, SMOKE, README,
                     MATRIX, PROFILES, EVIDENCE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_project_is_minimal_and_self_contained(self) -> None:
        project = (MODULE / "project.godot").read_text(encoding="utf-8")
        self.assertIn("config_version=5", project)
        self.assertIn('run/main_scene="res://main.tscn"', project)
        scene = (MODULE / "main.tscn").read_text(encoding="utf-8")
        self.assertIn("res://render_passport.gd", scene)


class RenderPassportDataTests(unittest.TestCase):
    def test_capability_matrix_is_documented_and_sourced(self) -> None:
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual("nex_m02_capability_matrix.v1", matrix["schema_version"])
        self.assertEqual("DOCUMENTED_UNVERIFIED_UNLESS_PROBED", matrix["verification"])
        self.assertEqual(9, len(matrix["capabilities"]))
        for capability in matrix["capabilities"]:
            with self.subTest(id=capability["id"]):
                self.assertTrue(capability["source"].startswith("https://docs.godotengine.org/"))
                self.assertIn("forward_plus", capability["states"])
                self.assertIn("gl_compatibility", capability["states"])
        self.assertIn("forward_plus+vulkan", matrix["fallbacks"])

    def test_profiles_are_three_reversible_settings_without_magic_tiers(self) -> None:
        profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
        self.assertEqual("nex_m02_profiles.v1", profiles["schema_version"])
        self.assertEqual("PROVISIONAL_NO_FPS_CLAIM", profiles["status"])
        self.assertEqual({"quality", "balanced", "performance"}, set(profiles["profiles"]))
        self.assertEqual("quality", profiles["defaults"])
        for name, profile in profiles["profiles"].items():
            with self.subTest(profile=name):
                self.assertIn("render_scale", profile)
                self.assertIn("msaa", profile)
                self.assertIn("mesh_lod", profile)


class RenderPassportApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code = CODE.read_text(encoding="utf-8")

    def test_required_api_and_flags(self) -> None:
        for method in ("load_data", "configure", "build_passport", "select_profile",
                       "switch_profile", "list_profiles", "get_report"):
            with self.subTest(method=method):
                self.assertIn(f"func {method}(", self.code)
        for flag in ("project_godot_writes", "personal_hardware_collected",
                     "gpu_name_implies_capability", "INCONCLUSIVE_NOT_PROBED",
                     "MEASURED_ENABLED", "MEASURED_DISABLED"):
            with self.subTest(flag=flag):
                self.assertIn(flag, self.code)

    def test_no_project_write_or_network_or_gpu_name_mapping(self) -> None:
        for forbidden in ("FileAccess.WRITE", "store_string", "HTTPRequest",
                          "HTTPClient", "RTX 5050", "nvidia-smi"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.code)


class RenderPassportEvidenceTests(unittest.TestCase):
    def test_smoke_marker_and_evidence_pass(self) -> None:
        self.assertIn("NEX_M02_S05_SMOKE_PASS", SMOKE.read_text(encoding="utf-8"))
        log = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("NEX_M02_S05_SMOKE_PASS: 87 checks", log)
        self.assertIn("4.7.2", log)

    def test_readme_documents_limits_and_fallbacks(self) -> None:
        text = README.read_text(encoding="utf-8").lower()
        for expected in ("documentation-derived", "no rendering", "no project.godot write",
                         "no remote hardware collection", "inconclusive_not_probed",
                         "m06", "degraded_features"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_no_fabricated_performance_claim(self) -> None:
        text = (README.read_text(encoding="utf-8") + EVIDENCE.read_text(encoding="utf-8")).lower()
        for forbidden in ("fps improved", "frame time reduced", "performance gain measured"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

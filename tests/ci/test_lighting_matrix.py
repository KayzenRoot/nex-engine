"""Structural checks for the NEX M01-S05 lighting matrix measurement stage."""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCENE_DIR = REPO / "nex_bench" / "scenes" / "lighting_matrix"
PRESETS_PATH = REPO / "nex_bench" / "presets" / "lighting_matrix" / "presets.v1.json"
SESSION_PATH = REPO / "nex_bench" / "gpu_profile" / "session.gd"
ALLOWED_MODES = {"geometry", "lights", "vfx", "combined"}
EVIDENCE_DIR = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-13-s05"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LightingMatrixPresetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.presets = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))

    def test_preset_contract(self) -> None:
        self.assertEqual("nex_lighting_matrix_presets.v1", self.presets["schema_version"])
        self.assertEqual([25, 100, 200], self.presets["counts"])
        presets = self.presets["presets"]
        self.assertEqual(5, len(presets))
        self.assertEqual(len(presets), len({preset["id"] for preset in presets}))
        for preset in presets:
            with self.subTest(preset=preset["id"]):
                self.assertIn(preset["effect_mode"], ALLOWED_MODES)
                self.assertIsInstance(preset["directional_shadow"], bool)
                self.assertGreaterEqual(int(preset["omni_lights"]), 0)
                self.assertGreaterEqual(int(preset["particles"]), 0)

    def test_combined_preset_is_capped_to_25(self) -> None:
        combined = [preset for preset in self.presets["presets"] if preset["effect_mode"] == "combined"]
        self.assertEqual(1, len(combined))
        self.assertEqual(25, int(combined[0]["max_proxy_count"]))

    def test_timing_matches_the_profiler_session(self) -> None:
        session = SESSION_PATH.read_text(encoding="utf-8")
        warmup = re.search(r"const WARMUP_SECONDS := ([0-9.]+)", session)
        observation = re.search(r"const OBSERVATION_SECONDS := ([0-9.]+)", session)
        self.assertIsNotNone(warmup)
        self.assertIsNotNone(observation)
        self.assertAlmostEqual(float(warmup.group(1)), float(self.presets["warmup_seconds"]))
        self.assertAlmostEqual(float(observation.group(1)), float(self.presets["observation_seconds"]))


class LightingMatrixScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.script = (SCENE_DIR / "lighting_matrix.gd").read_text(encoding="utf-8")
        self.scene = (SCENE_DIR / "lighting_matrix.tscn").read_text(encoding="utf-8")
        self.smoke = (SCENE_DIR / "smoke.gd").read_text(encoding="utf-8")

    def test_scene_references_the_script_and_smoke_marker(self) -> None:
        self.assertIn("res://scenes/lighting_matrix/lighting_matrix.gd", self.scene)
        self.assertIn("NEX_S05_SMOKE_PASS", self.smoke)
        self.assertIn("lighting_matrix.tscn", self.smoke)

    def test_reuses_the_integrated_profiler_without_fabricating_metrics(self) -> None:
        for call in ("session.begin(", "session.step(", "session.save_document(", "session.cancel("):
            with self.subTest(call=call):
                self.assertIn(call, self.script)
        self.assertIn("NEX_GPU_PROFILE_SOURCE_SHA", self.script)
        self.assertNotIn("one_percent_low", self.script)
        self.assertNotIn("1000.0 /", self.script)

    def test_workload_changes_cancel_an_active_run(self) -> None:
        self.assertIn("workload changed; run not exported", self.script)
        self.assertIn("_cancel_for_workload_change()", self.script)

    def test_count_selection_and_cap_exist(self) -> None:
        for key in ("KEY_Q", "KEY_W", "KEY_E"):
            self.assertIn(key, self.script)
        self.assertIn("max_proxy_count", self.script)
        self.assertIn("mini(count, cap)", self.script)


class LightingMatrixValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = _load_module(SCENE_DIR / "validate_lighting_matrix.py", "s05_validator")
        cls.documents = sorted(path for path in EVIDENCE_DIR.glob("gpu_profile_*.json")
                               if not path.name.endswith(".s05-validation.json"))

    def test_every_committed_capture_validates(self) -> None:
        self.assertEqual(15, len(self.documents))
        for path in self.documents:
            with self.subTest(path=path.name):
                document = self.validator._loads(path.read_bytes())
                result = self.validator.validate_document(document)
                self.assertEqual("PASS", result["status"])
                self.assertEqual("COMPLETE", result["run_status"])
                self.assertEqual("Lighting Matrix", document["workload"]["scene"])

    def test_forged_aggregate_is_rejected(self) -> None:
        document = self.validator._loads(self.documents[0].read_bytes())
        document["series"]["GPU_RENDER_MS"]["aggregates"]["p50"] += 0.05
        with self.assertRaises(self.validator.LightingMatrixError):
            self.validator.validate_document(document)

    def test_wrong_scene_provenance_is_rejected(self) -> None:
        document = self.validator._loads(self.documents[0].read_bytes())
        document["workload"]["scene"] = "Density Ladder"
        with self.assertRaises(self.validator.LightingMatrixError):
            self.validator.validate_document(document)

    def test_s04_validator_rejects_lighting_matrix_by_design(self) -> None:
        s04 = _load_module(REPO / "nex_bench" / "gpu_profile" / "validate_gpu_profile.py", "s05_s04_validator")
        with self.assertRaises(s04.ProfileError):
            s04.validate_payload(self.documents[0].read_bytes())


if __name__ == "__main__":
    unittest.main()

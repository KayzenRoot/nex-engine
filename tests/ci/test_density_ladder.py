"""Density Ladder S04 static bounds and native project wiring checks.

This suite does not run Godot or measure hardware performance.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "nex_bench" / "stress"


class DensityLadderConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((LAB / "config/ladder.v1.json").read_text(encoding="utf-8"))
        cls.script = (LAB / "density_ladder.gd").read_text(encoding="utf-8")
        cls.project = (LAB / "project.godot").read_text(encoding="utf-8")
        cls.scene = (LAB / "main.tscn").read_text(encoding="utf-8")

    def test_version_pinned_renderer(self):
        self.assertEqual(self.config["schema_version"], "nex_density_ladder.v1")
        self.assertEqual(self.config["godot_version"], "4.7.2-stable")
        self.assertEqual(self.config["renderer"], "forward_plus")
        self.assertIn('renderer/rendering_method="forward_plus"', self.project)

    def test_levels_are_strict_and_bounded(self):
        self.assertEqual(self.config["counts"], [25, 50, 100, 200])
        self.assertEqual(self.config["max_proxies"], max(self.config["counts"]))
        self.assertGreater(self.config["counts"][0], 0)
        self.assertEqual(len(self.config["counts"]), len(set(self.config["counts"])))

    def test_effects_are_capped(self):
        self.assertLessEqual(self.config["max_lights"], 6)
        self.assertLessEqual(self.config["max_particle_emitters"], 4)
        self.assertIn("range(max_lights)", self.script)
        self.assertIn("range(max_particle_emitters)", self.script)

    def test_modes_are_explicit_and_separable(self):
        self.assertEqual(self.config["modes"], ["geometry", "lights", "vfx", "combined"])
        for key in ("KEY_1", "KEY_2", "KEY_3", "KEY_4", "KEY_G", "KEY_L", "KEY_V", "KEY_C"):
            with self.subTest(key=key):
                self.assertIn(key, self.script)

    def test_godot_json_float_numbers_require_whole_bounded_values(self):
        for expected in ("TYPE_FLOAT", "number != floor(number)", "_json_integer(",
                         "counts = DEFAULT_COUNTS.duplicate()"):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.script)
        self.assertNotIn("cap is int and light_cap is int", self.script)

    def test_runtime_checks_config_and_safety_fallback(self):
        for token in ("return false", "max_proxies", "safe_fps_timer", "Engine.get_frames_per_second()",
                      "count_index = 0", "current_mode = 0"):
            with self.subTest(token=token):
                self.assertIn(token, self.script)
        self.assertGreaterEqual(self.config["minimum_safe_fps_observed"], 5)
        self.assertGreaterEqual(self.config["safety_consecutive_seconds"], 2)

    def test_scene_and_viewer_are_wired(self):
        self.assertIn('run/main_scene="res://main.tscn"', self.project)
        self.assertIn('path="res://density_ladder.gd"', self.scene)
        for name in ("WorkloadRoot", "HUD", "Status"):
            self.assertRegex(self.scene, r'\[node name="' + name + '"')

    def test_no_hardware_benchmark_claim(self):
        self.assertEqual(self.config["measurement"], "NOT_MEASURED")
        self.assertIn("NOT a validated hardware benchmark", self.script)
        self.assertIn("not benchmark", self.script)


if __name__ == "__main__":
    unittest.main()

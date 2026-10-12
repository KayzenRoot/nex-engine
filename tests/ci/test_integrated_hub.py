"""Unified NEX visual hub static wiring tests, no native Godot or GPU inference."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2] / "nex_bench"


class IntegratedVisualHubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = (ROOT / "project.godot").read_text(encoding="utf-8")
        cls.scene = (ROOT / "main.tscn").read_text(encoding="utf-8")
        cls.script = (ROOT / "hub.gd").read_text(encoding="utf-8")
        cls.stress = (ROOT / "stress/density_ladder.gd").read_text(encoding="utf-8")

    def test_godot_native_parser_regression_stem_type(self):
        self.assertIn("var stem: String =", self.script)
        smoke = (ROOT / "smoke.gd").read_text(encoding="utf-8")
        self.assertIn("window.has_method(\"_activate_mode\")", smoke)

    def test_native_project_launches_hub_in_forward_plus(self):
        self.assertIn('run/main_scene="res://main.tscn"', self.project)
        self.assertIn('renderer/rendering_method="forward_plus"', self.project)
        self.assertIn('path="res://hub.gd"', self.scene)

    def test_three_actual_reference_scene_paths(self):
        for name in ("corridor_static", "arena_combat", "dense_city"):
            with self.subTest(scene=name):
                self.assertTrue((ROOT / f"scenes/base/{name}.tscn").is_file())
                self.assertIn(f'res://scenes/base/{name}.tscn', self.script)

    def test_density_script_uses_relative_config_in_both_projects(self):
        self.assertIn('res://stress/density_ladder.gd', self.script)
        self.assertIn('resource_path.get_base_dir().path_join(SETTINGS_NAME)', self.stress)
        self.assertNotIn('SETTINGS_PATH := "res://config/ladder.v1.json"', self.stress)
        config = json.loads((ROOT / "stress/config/ladder.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(config["counts"], [25, 50, 100, 200])
        self.assertIn('run/main_scene="res://main.tscn"',
                      (ROOT / "stress/project.godot").read_text(encoding="utf-8"))

    def test_toolbar_and_keyboard_route_all_modules(self):
        for token in ('button.pressed.connect(_activate_mode.bind(i))',
                      'button.pressed.connect(_capture.bind("baseline"))',
                      'button.pressed.connect(_capture.bind("candidate"))',
                      'button.pressed.connect(_compare_captures)',
                      "KEY_F1", "KEY_F2", "KEY_F3", "KEY_F4"):
            with self.subTest(token=token):
                self.assertIn(token, self.script)

    def test_native_baseline_candidate_diff_does_not_use_external_commands(self):
        for token in ('CAPTURE_ROOT := "user://visual_truth"',
                      'await RenderingServer.frame_post_draw', '$HUD.visible = false',
                      'image.save_png(', 'Image.load_from_file(', 'first_rgb.convert(Image.FORMAT_RGB8)',
                      'PIXEL_TOLERANCE := 2', 'float(report["changed_ratio"]) * 100.0'):
            with self.subTest(token=token):
                self.assertIn(token, self.script)
        self.assertNotIn('OS.execute(', self.script)
        self.assertNotIn('HTTPClient', self.script)

    def test_native_visual_truth_algorithm_covered_by_godot_smoke(self):
        for token in ('func _pixel_diff(first: Image, second: Image) -> Dictionary:',
                      'first.duplicate() as Image', 'second.duplicate() as Image',
                      'changed_pixels', 'SIZE_MISMATCH', 'mean_absolute_error_normalized'):
            with self.subTest(token=token):
                self.assertIn(token, self.script)
        smoke = (ROOT / "smoke.gd").read_text(encoding="utf-8")
        for token in ('NEX_NATIVE_VISUAL_TRUTH_PASS', 'Image.create(2, 1',
                      'window.call("_pixel_diff"', 'changed_ratio', 'SIZE_MISMATCH'):
            with self.subTest(token=token):
                self.assertIn(token, smoke)

    def test_native_headless_smoke_is_reproducible(self):
        smoke = (ROOT / "smoke.gd").read_text(encoding="utf-8")
        for token in ("extends SceneTree", "NEX_NATIVE_IMPORT_SMOKE_PASS",
                      '"res://main.tscn"', '"res://stress/density_ladder.gd"',
                      "for mode in range(4)", 'quit(1)'):
            with self.subTest(token=token):
                self.assertIn(token, smoke)

    def test_preserves_original_standalone_projects_and_python_comparator(self):
        for path in ("scenes/base/project.godot", "stress/project.godot",
                     "visual_truth/compare.py", "fixtures/base/manifest.v1.json"):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())


if __name__ == "__main__":
    unittest.main()

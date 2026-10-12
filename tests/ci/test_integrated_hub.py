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

    def test_bounded_f10_frame_interval_observation(self):
        for name in ("KEY_F10", "func _begin_frame_observation() -> bool:",
                     "func _observed_percentile_ms(", "func _finish_frame_observation()",
                     "OBS_MAX_FRAMES := 1500", "OBS_MIN_FRAMES := 60",
                     "OBSERVED_MAIN_LOOP_DELTA_NOT_GPU_TIME", "p50_interval_ms",
                     "p95_interval_ms", "p99_interval_ms", "vsync_mode",
                     "Observation cancelled: workload changed"):
            with self.subTest(name=name):
                self.assertIn(name, self.script)
        self.assertIn("NEX_NATIVE_FRAME_OBSERVATION_PASS",
                      (ROOT / "smoke.gd").read_text(encoding="utf-8"))

    def test_reference_camera_navigation_supports_real_nonidentical_screenshots(self):
        for name in ("KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN",
                     "KEY_PAGEUP", "KEY_PAGEDOWN", "KEY_HOME",
                     "func _reference_camera() -> Camera3D:",
                     "func _move_reference_camera(", "func _reset_reference_camera()",
                     "camera_home_position", "camera.look_at(Vector3.ZERO, Vector3.UP)"):
            with self.subTest(name=name):
                self.assertIn(name, self.script)
        smoke = (ROOT / "smoke.gd").read_text(encoding="utf-8")
        self.assertIn("NEX_NATIVE_CAMERA_NAVIGATION_PASS", smoke)
        self.assertIn("yaw navigation produced no visual-position change", smoke)
        self.assertIn("Static camera keys must not modify Density Ladder", smoke)

    def test_renderer_diagnostics_panel_does_not_claim_gpu_benchmark(self):
        for marker in ('"DIAGNOSTICO [F9]"', "KEY_F9",
                       'Performance.get_monitor(Performance.TIME_FPS)',
                       'Performance.get_monitor(Performance.TIME_PROCESS)',
                       'Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)',
                       'Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)',
                       'RenderingServer.get_video_adapter_name()',
                       'RenderingServer.get_current_rendering_driver_name()',
                       'N/A (headless / unavailable)', "NAO representa VRAM total"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.script)
        smoke = (ROOT / "smoke.gd").read_text(encoding="utf-8")
        self.assertIn("NEX_NATIVE_DIAGNOSTICS_PASS", smoke)
        self.assertIn("diagnostics.visible", smoke)

    def test_heatmap_preview_is_native_and_exports_png(self):
        for snippet in ("func _create_heatmap(first: Image, second: Image) -> Image:",
                        "Image.create_from_data(", "Image.FORMAT_RGBA8",
                        "DiffPreview", "TextureRect.new()", "ImageTexture.create_from_image",
                        'directory.path_join(stem + "_heatmap.png")',
                        "heatmap.save_png(output_path)", "_hide_diff_preview()"):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, self.script)
        smoke = (ROOT / "smoke.gd").read_text(encoding="utf-8")
        for snippet in ("NEX_NATIVE_VISUAL_HEATMAP_PASS", "window.call(\"_create_heatmap\"",
                        'window.call("_show_diff_preview"', 'window.call("_hide_diff_preview"'):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, smoke)

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

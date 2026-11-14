"""Structural, determinism and reproducibility tests for the NEX M01 visual run."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _preset_ab_support import (
    assert_builder_reproduces,
    assert_limits,
    assert_no_fabricated,
    assert_sha256sums,
    load_builder,
)

REPO = Path(__file__).resolve().parents[2]
SCENE = REPO / "nex_bench" / "scenes" / "preset_ab"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-m01-visual"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_m01_visual.py"
PNG_MODULE = DOCS / "tools" / "png_image.py"
REPORT_JSON = DOCS / "m01-visual.v1.json"
REPORT_MD = DOCS / "M01-VISUAL-REPORT.md"
SCENES = ("corridor_static", "arena_combat", "dense_city")
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class M01VisualFilesTests(unittest.TestCase):
    def test_harness_evidence_and_report_files_exist(self) -> None:
        for path in (
            SCENE / "preset_ab.gd",
            PNG_MODULE,
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
        ):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
        images = sorted(EVIDENCE.glob("*.png"))
        self.assertEqual(18, len(images))

    def test_harness_supports_visual_capture(self) -> None:
        code = (SCENE / "preset_ab.gd").read_text(encoding="utf-8")
        for marker in (
            'const VISUAL_ENV := "NEX_PRESET_AB_VISUAL"',
            "const VISUAL_WARMUP_FRAMES := 180",
            "NEX_PRESET_AB_VISUAL_OUTPUT",
            "RenderingServer.frame_post_draw",
            "get_viewport().get_texture().get_image()",
            "image.flip_y()",
            "image.save_png(path)",
            "NEX_PRESET_AB_IMAGE",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)


class M01VisualManifestTests(unittest.TestCase):
    def test_manifest_covers_three_scenes_and_two_presets(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_visual_runs.v1", manifest["schema_version"])
        self.assertEqual(18, len(manifest["runs"]))
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                         [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(18, len({run["file"] for run in manifest["runs"]}))
        for scene in SCENES:
            for preset in PRESETS:
                with self.subTest(scene=scene, preset=preset):
                    group = [run for run in manifest["runs"]
                             if run["scene_id"] == scene and run["preset_id"] == preset]
                    self.assertEqual(3, len(group))
                    self.assertEqual(1, len({run["sha256"] for run in group}))
                    for run in group:
                        self.assertEqual(1280, run["width"])
                        self.assertEqual(720, run["height"])
                        self.assertEqual(3, run["channels"])

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 21)


class M01VisualDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.png = load_builder("nex_m09_png_image", PNG_MODULE)

    def test_png_decodes_to_rgb_pixels(self) -> None:
        image = self.png.read_png(EVIDENCE / "corridor_static_ab-low_1.png")
        self.assertEqual((1280, 720, 3), (image.width, image.height, image.channels))
        self.assertEqual(1280 * 720 * 3, len(image.pixels))

    def test_identical_image_has_zero_difference(self) -> None:
        image = self.png.read_png(EVIDENCE / "arena_combat_ab-high_1.png")
        self.assertEqual(
            {"mean_abs_diff": 0.0, "max_abs_diff": 0, "changed_pixels": 0,
             "changed_pixels_pct": 0.0, "psnr_db": None},
            self.png.compare(image, image),
        )

    def test_low_high_difference_matches_report(self) -> None:
        low = self.png.read_png(EVIDENCE / "dense_city_ab-low_1.png")
        high = self.png.read_png(EVIDENCE / "dense_city_ab-high_1.png")
        metrics = self.png.compare(low, high)
        self.assertEqual(0.2317, metrics["mean_abs_diff"])
        self.assertEqual(133, metrics["max_abs_diff"])
        self.assertEqual(1.745, metrics["changed_pixels_pct"])
        self.assertEqual(39.763, metrics["psnr_db"])

    def test_invalid_png_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.png"
            path.write_bytes(b"\x89PNG\r\n\x1a\nbroken")
            with self.assertRaises(self.png.PngError):
                self.png.read_png(path)


class M01VisualReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_m01_visual", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_three_scenes_and_expected_metrics(self) -> None:
        self.assertEqual("m09_preset_m01_visual.v1", self.report["schema_version"])
        self.assertEqual(18, self.report["runs"])
        self.assertEqual(3, len(self.report["scenes"]))
        self.assertEqual("VISUAL_DIFFERENCE_OBSERVED", self.report["verdict"])
        by_scene = {scene["scene_id"]: scene for scene in self.report["scenes"]}
        expected = {
            "corridor_static": (0.5135, 170, 4.077, 37.406),
            "arena_combat": (0.4898, 187, 3.884, 36.386),
            "dense_city": (0.2317, 133, 1.745, 39.763),
        }
        for scene_id, (mean_abs, max_abs, changed_pct, psnr) in expected.items():
            with self.subTest(scene=scene_id):
                metrics = by_scene[scene_id]["ab_comparisons"][0]["metrics"]
                self.assertEqual(mean_abs, metrics["mean_abs_diff"])
                self.assertEqual(max_abs, metrics["max_abs_diff"])
                self.assertEqual(changed_pct, metrics["changed_pixels_pct"])
                self.assertEqual(psnr, metrics["psnr_db"])
                self.assertTrue(by_scene[scene_id]["summary"]["aa_all_identical"])
                self.assertEqual(0.0, by_scene[scene_id]["summary"]["aa_max_mean_abs_diff"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_quality_claim(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "static frame", "not model human perception", "no fps gain",
        ))
        assert_no_fabricated(self, REPORT_MD.read_text(encoding="utf-8").lower(), (
            "visually better", "quality verified", "sharper is better", "universal improvement",
        ))


if __name__ == "__main__":
    unittest.main()

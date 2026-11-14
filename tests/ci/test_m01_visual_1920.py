"""Structural, determinism and reproducibility tests for the 1920x1080 visual run."""
from __future__ import annotations

import json
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
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-m01-visual-1920"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_m01_visual_1920.py"
PNG_MODULE = DOCS / "tools" / "png_image.py"
REPORT_JSON = DOCS / "m01-visual-1920.v1.json"
REPORT_MD = DOCS / "M01-VISUAL-1920-REPORT.md"
SCENES = ("corridor_static", "arena_combat", "dense_city")
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class M01Visual1920FilesTests(unittest.TestCase):
    def test_evidence_and_report_files_exist(self) -> None:
        required = [
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
            PNG_MODULE,
        ]
        self.assertEqual([], [str(path) for path in required if not path.is_file()])
        self.assertEqual(18, len(sorted(EVIDENCE.glob("*.png"))))

    def test_manifest_covers_three_scenes_at_1920(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_visual_runs.v1", manifest["schema_version"])
        self.assertEqual(18, len(manifest["runs"]))
        self.assertEqual(list(range(1, 19)), [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(18, len({run["file"] for run in manifest["runs"]}))
        for scene in SCENES:
            for preset in PRESETS:
                with self.subTest(scene=scene, preset=preset):
                    group = [run for run in manifest["runs"]
                             if run["scene_id"] == scene and run["preset_id"] == preset]
                    self.assertEqual(3, len(group))
                    self.assertEqual(1, len({run["sha256"] for run in group}))
                    for run in group:
                        self.assertEqual(1920, run["width"])
                        self.assertEqual(1080, run["height"])
                        self.assertEqual(3, run["channels"])

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 21)


class M01Visual1920DecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.png = load_builder("nex_m09_png_image_1920", PNG_MODULE)

    def test_png_decodes_to_1920_rgb(self) -> None:
        image = self.png.read_png(EVIDENCE / "corridor_static_ab-low_1.png")
        self.assertEqual((1920, 1080, 3), (image.width, image.height, image.channels))

    def test_identical_image_has_zero_difference(self) -> None:
        image = self.png.read_png(EVIDENCE / "arena_combat_ab-high_1.png")
        self.assertEqual(0.0, self.png.compare(image, image)["mean_abs_diff"])

    def test_low_high_difference_matches_report(self) -> None:
        low = self.png.read_png(EVIDENCE / "corridor_static_ab-low_1.png")
        high = self.png.read_png(EVIDENCE / "corridor_static_ab-high_1.png")
        metrics = self.png.compare(low, high)
        self.assertEqual(0.4168, metrics["mean_abs_diff"])
        self.assertEqual(167, metrics["max_abs_diff"])
        self.assertEqual(3.367, metrics["changed_pixels_pct"])
        self.assertEqual(38.485, metrics["psnr_db"])


class M01Visual1920ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_visual_1920", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_three_scenes_and_expected_metrics(self) -> None:
        self.assertEqual("m09_preset_m01_visual_1920.v1", self.report["schema_version"])
        self.assertEqual(18, self.report["runs"])
        self.assertEqual(3, len(self.report["scenes"]))
        self.assertEqual("VISUAL_DIFFERENCE_OBSERVED", self.report["verdict"])
        by_scene = {scene["scene_id"]: scene for scene in self.report["scenes"]}
        expected = {
            "corridor_static": (0.4168, 167, 3.367, 38.485, -18.8),
            "arena_combat": (0.4215, 189, 3.354, 36.851, -13.9),
            "dense_city": (0.1785, 146, 1.276, 40.464, -23.0),
        }
        for scene_id, (mean_abs, max_abs, changed, psnr, delta) in expected.items():
            with self.subTest(scene=scene_id):
                metrics = by_scene[scene_id]["ab"]["metrics"]
                self.assertEqual(mean_abs, metrics["mean_abs_diff"])
                self.assertEqual(max_abs, metrics["max_abs_diff"])
                self.assertEqual(changed, metrics["changed_pixels_pct"])
                self.assertEqual(psnr, metrics["psnr_db"])
                self.assertTrue(by_scene[scene_id]["aa"]["identical_sha"])
                self.assertEqual(delta, by_scene[scene_id]["comparison_1280"]["delta_mean_abs_pct"])

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

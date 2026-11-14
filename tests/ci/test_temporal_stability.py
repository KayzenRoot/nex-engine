"""Structural, determinism and reproducibility tests for the temporal-stability run."""
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
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-m01-temporal"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_temporal_stability.py"
PNG_MODULE = DOCS / "tools" / "png_image.py"
REPORT_JSON = DOCS / "temporal-stability.v1.json"
REPORT_MD = DOCS / "TEMPORAL-STABILITY-REPORT.md"


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class TemporalFilesTests(unittest.TestCase):
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
        self.assertEqual(30, len(sorted(EVIDENCE.glob("*.png"))))

    def test_manifest_has_six_cells_and_five_frames_each(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_visual_sequence_runs.v1", manifest["schema_version"])
        self.assertEqual(6, len(manifest["cells"]))
        self.assertEqual(30, sum(len(cell["frames"]) for cell in manifest["cells"]))
        for cell in manifest["cells"]:
            with self.subTest(scene=cell["scene_id"], preset=cell["preset_id"]):
                self.assertEqual([0, 1, 2, 3, 4], [frame["index"] for frame in cell["frames"]])
                self.assertEqual(1, len({frame["sha256"] for frame in cell["frames"]}))
                for frame in cell["frames"]:
                    self.assertEqual(1280, frame["width"])
                    self.assertEqual(720, frame["height"])

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 33)


class TemporalDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.png = load_builder("nex_m09_png_image_temporal", PNG_MODULE)

    def test_frame_decodes_to_1280_rgb(self) -> None:
        image = self.png.read_png(EVIDENCE / "corridor_static_ab-low_frame_00.png")
        self.assertEqual((1280, 720, 3), (image.width, image.height, image.channels))

    def test_identical_frames_have_zero_difference(self) -> None:
        first = self.png.read_png(EVIDENCE / "corridor_static_ab-low_frame_00.png")
        last = self.png.read_png(EVIDENCE / "corridor_static_ab-low_frame_04.png")
        metrics = self.png.compare(first, last)
        self.assertEqual(0.0, metrics["mean_abs_diff"])
        self.assertEqual(0, metrics["changed_pixels"])


class TemporalReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_temporal", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_six_stable_cells(self) -> None:
        self.assertEqual("m09_preset_m01_temporal.v1", self.report["schema_version"])
        self.assertEqual(30, self.report["runs"])
        self.assertEqual(6, len(self.report["cells"]))
        self.assertEqual("TEMPORAL_STABILITY_OBSERVED", self.report["verdict"])
        self.assertTrue(self.report["summary"]["all_frames_identical"])
        self.assertEqual(0.0, self.report["summary"]["max_mean_abs_diff"])
        self.assertEqual(0.0, self.report["summary"]["max_changed_pixels_pct"])
        for cell in self.report["cells"]:
            with self.subTest(scene=cell["scene_id"], preset=cell["preset_id"]):
                self.assertTrue(cell["all_frames_identical"])
                self.assertEqual(1, cell["unique_sha_count"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_quality_claim(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "static scenes only", "not model human perception", "no fps gain",
        ))
        assert_no_fabricated(self, REPORT_MD.read_text(encoding="utf-8").lower(), (
            "visually better", "quality verified", "universal gain", "benchmark passed",
        ))


if __name__ == "__main__":
    unittest.main()

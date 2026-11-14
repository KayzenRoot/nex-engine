"""Structural, provenance and reproducibility tests for the NEX cross-scene run."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _preset_ab_support import (
    assert_builder_reproduces,
    assert_captures,
    assert_limits,
    assert_sha256sums,
    assert_validations,
    load_builder,
)

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-cross-scene"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_cross_scene.py"
REPORT_JSON = DOCS / "cross-scene.v1.json"
REPORT_MD = DOCS / "CROSS-SCENE-REPORT.md"
SCENES = ("corridor_static", "dense_city")
CELLS = ((50, 960, 540), (50, 1920, 1080), (100, 960, 540), (100, 1920, 1080))
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


class CrossSceneFilesTests(unittest.TestCase):
    def test_evidence_and_report_files_exist(self) -> None:
        required = [
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
        ]
        self.assertEqual([], [str(path) for path in required if not path.is_file()])
        raw = [p for p in EVIDENCE.glob("gpu_profile_*.json") if not p.name.endswith(".validation.json")]
        self.assertEqual(48, len(raw))
        self.assertEqual([], [p.name for p in raw if not (EVIDENCE / f"{p.name}.validation.json").is_file()])


class CrossSceneManifestTests(unittest.TestCase):
    def test_manifest_covers_two_scenes_and_eight_cells_each(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(48, len(manifest["runs"]))
        self.assertEqual(list(range(1, 49)), [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(48, len({run["run_id"] for run in manifest["runs"]}))
        for scene in SCENES:
            for count, width, height in CELLS:
                for preset in PRESETS:
                    with self.subTest(scene=scene, cell=f"{count}/{width}x{height}", preset=preset):
                        group = [run for run in manifest["runs"]
                                 if run["scene_id"] == scene
                                 and run["proxy_count"] == count
                                 and run["viewport_px"] == [width, height]
                                 and run["preset_id"] == preset]
                        self.assertEqual(3, len(group))

    def test_captures_are_complete_and_match_provenance(self) -> None:
        assert_captures(self, EVIDENCE, _manifest(), default_count=None, default_scene=None)

    def test_validations_pass(self) -> None:
        assert_validations(self, EVIDENCE, _manifest())

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 99)


class CrossSceneReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_cross_scene", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_two_scenes_and_expected_deltas(self) -> None:
        self.assertEqual("m09_preset_cross_scene.v1", self.report["schema_version"])
        self.assertEqual(48, len(self.report["runs"]))
        self.assertEqual(2, len(self.report["scenes"]))
        self.assertEqual(16, sum(len(scene["cells"]) for scene in self.report["scenes"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        by_scene = {scene["scene_id"]: scene for scene in self.report["scenes"]}
        corridor = by_scene["corridor_static"]["deltas_high_vs_low"]
        city = by_scene["dense_city"]["deltas_high_vs_low"]
        self.assertEqual(294.4, corridor["50/960x540"]["gpu_p95_pct"])
        self.assertEqual(476.5, corridor["50/1920x1080"]["gpu_p95_pct"])
        self.assertEqual(464.3, corridor["100/1920x1080"]["gpu_p95_pct"])
        self.assertEqual(245.6, city["50/960x540"]["gpu_p95_pct"])
        self.assertEqual(461.5, city["50/1920x1080"]["gpu_p95_pct"])
        self.assertEqual(457.3, city["100/1920x1080"]["gpu_p95_pct"])

    def test_resolution_scaling_is_reported_per_scene(self) -> None:
        by_scene = {scene["scene_id"]: scene for scene in self.report["scenes"]}
        self.assertEqual(91.5, by_scene["corridor_static"]["resolution_scaling"]["50"]["ab-low"])
        self.assertEqual(180.0, by_scene["corridor_static"]["resolution_scaling"]["50"]["ab-high"])
        self.assertEqual(79.4, by_scene["dense_city"]["resolution_scaling"]["50"]["ab-low"])
        self.assertEqual(191.5, by_scene["dense_city"]["resolution_scaling"]["50"]["ab-high"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_gain(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "two scenes only", "200 proxies and 2560x1440 are not covered", "no fps gain",
        ))


if __name__ == "__main__":
    unittest.main()

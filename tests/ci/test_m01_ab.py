"""Structural, provenance and reproducibility tests for the NEX M01 A/B/A run."""
from __future__ import annotations

import importlib.util
import json
import sys
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
SCENE = REPO / "nex_bench" / "scenes" / "preset_ab"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-m01-ab"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_m01_ab.py"
REPORT_JSON = DOCS / "m01-ab.v1.json"
REPORT_MD = DOCS / "M01-AB-REPORT.md"
SCENES = (
    ("corridor_static", "M01 Corridor A/B/A", "M01 corridor_static + deterministic fillers"),
    ("arena_combat", "M01 Arena A/B/A", "M01 arena_combat + deterministic fillers"),
    ("dense_city", "M01 City A/B/A", "M01 dense_city + deterministic fillers"),
)
PRESETS = ("ab-low", "ab-high")


def _manifest() -> dict:
    return json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))


def _load_validator():
    path = SCENE / "validate_preset_ab.py"
    spec = importlib.util.spec_from_file_location("nex_m01_ab_validator", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load validate_preset_ab.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class M01ABFilesTests(unittest.TestCase):
    def test_harness_evidence_and_report_files_exist(self) -> None:
        for path in (
            SCENE / "preset_ab.gd",
            SCENE / "validate_preset_ab.py",
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
            DOCS / "tools" / "preset_report.py",
        ):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
        raw = [p for p in EVIDENCE.glob("gpu_profile_*.json") if not p.name.endswith(".validation.json")]
        self.assertEqual(18, len(raw))
        for path in raw:
            with self.subTest(run=path.name):
                self.assertTrue((EVIDENCE / f"{path.name}.validation.json").is_file())

    def test_harness_supports_all_m01_scenes(self) -> None:
        code = (SCENE / "preset_ab.gd").read_text(encoding="utf-8")
        for marker in (
            'const SCENE_ENV := "NEX_PRESET_AB_SCENE"',
            "res://scenes/base/corridor_static.tscn",
            "res://scenes/base/arena_combat.tscn",
            "res://scenes/base/dense_city.tscn",
            '"M01 Corridor A/B/A"',
            '"M01 Arena A/B/A"',
            '"M01 City A/B/A"',
            '"proxy_count": 100',
            'find_children("*", "MeshInstance3D", true, false)',
            "mesh count %d does not match proxy_count %d",
            '"layout": scene_layout',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)

    def test_validator_knows_m01_layouts(self) -> None:
        code = (SCENE / "validate_preset_ab.py").read_text(encoding="utf-8")
        for marker in (
            "M01_SCENE_SPECS",
            "M01 corridor_static + deterministic fillers",
            "M01 arena_combat + deterministic fillers",
            "M01 dense_city + deterministic fillers",
            "canonical.validate_report",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)

    def test_session_accepts_only_known_layouts(self) -> None:
        code = (REPO / "nex_bench" / "gpu_profile" / "session.gd").read_text(encoding="utf-8")
        for marker in (
            'const DEFAULT_WORKLOAD_LAYOUT := "built-in deterministic grid"',
            "ALLOWED_WORKLOAD_LAYOUTS",
            "M01 corridor_static + deterministic fillers",
            "M01 arena_combat + deterministic fillers",
            "M01 dense_city + deterministic fillers",
            'str(run_context.get("layout", DEFAULT_WORKLOAD_LAYOUT))',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)


class M01ABManifestTests(unittest.TestCase):
    def test_manifest_covers_three_scenes_and_two_presets(self) -> None:
        manifest = _manifest()
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(18, len(manifest["runs"]))
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                         [run["sequence"] for run in manifest["runs"]])
        self.assertEqual(18, len({run["run_id"] for run in manifest["runs"]}))
        for scene_id, scene, layout in SCENES:
            for preset in PRESETS:
                with self.subTest(scene=scene_id, preset=preset):
                    group = [run for run in manifest["runs"]
                             if run["scene_id"] == scene_id and run["preset_id"] == preset]
                    self.assertEqual(3, len(group))
                    for run in group:
                        self.assertEqual(scene, run["scene"])
                        self.assertEqual(layout, run["layout"])
                        self.assertEqual(100, run["proxy_count"])

    def test_captures_are_complete_and_match_provenance(self) -> None:
        assert_captures(self, EVIDENCE, _manifest(), default_count=None, default_scene=None)

    def test_validations_pass(self) -> None:
        assert_validations(self, EVIDENCE, _manifest())

    def test_sha256sums_match_every_file(self) -> None:
        assert_sha256sums(self, EVIDENCE, 39)


class M01ABValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = _load_validator()
        first = _manifest()["runs"][0]
        cls.document = json.loads(
            (EVIDENCE / f"gpu_profile_{first['run_id']}.json").read_text(encoding="utf-8")
        )

    def _with_workload(self, **changes):
        document = dict(self.document)
        document["workload"] = dict(self.document["workload"], **changes)
        return document

    def test_valid_m01_document_passes(self) -> None:
        result = self.validator.validate_document(self.document)
        self.assertEqual("PASS", result["status"])

    def test_wrong_layout_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.validator.validate_document(self._with_workload(layout="built-in deterministic grid"))

    def test_wrong_count_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.validator.validate_document(self._with_workload(proxy_count=25))

    def test_unknown_scene_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.validator.validate_document(self._with_workload(scene="M01 Unknown A/B/A"))


class M01ABReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder("nex_m09_build_m01_ab", BUILDER)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_three_scenes_and_expected_deltas(self) -> None:
        self.assertEqual("m09_preset_m01_ab.v1", self.report["schema_version"])
        self.assertEqual(18, len(self.report["runs"]))
        self.assertEqual(3, len(self.report["scenes"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        by_scene = {scene["scene_id"]: scene for scene in self.report["scenes"]}
        self.assertEqual(380.7, by_scene["corridor_static"]["deltas_high_vs_low"]["gpu_p95_pct"])
        self.assertEqual(323.9, by_scene["arena_combat"]["deltas_high_vs_low"]["gpu_p95_pct"])
        self.assertEqual(331.0, by_scene["dense_city"]["deltas_high_vs_low"]["gpu_p95_pct"])
        self.assertEqual(3, by_scene["corridor_static"]["baselines"]["ab-low"]["runs"])

    def test_aa_stability_is_reported_per_scene(self) -> None:
        by_scene = {scene["scene_id"]: scene for scene in self.report["scenes"]}
        self.assertEqual(3.4, by_scene["corridor_static"]["baselines"]["ab-low"]["gpu_p95_spread_pct"])
        self.assertEqual(7.3, by_scene["arena_combat"]["baselines"]["ab-low"]["gpu_p95_spread_pct"])
        self.assertEqual(1.2, by_scene["dense_city"]["baselines"]["ab-low"]["gpu_p95_spread_pct"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.builder, self.report, REPORT_JSON, REPORT_MD)

    def test_limits_and_no_fabricated_gain(self) -> None:
        assert_limits(self, self.report, REPORT_MD, (
            "single session", "three specific m01 compositions", "vsync disabled", "not device vram",
        ))


if __name__ == "__main__":
    unittest.main()

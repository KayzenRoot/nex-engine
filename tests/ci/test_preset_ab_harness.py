"""Structural and reproducibility tests for the NEX M09 preset A/B/A harness."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCENE = REPO / "nex_bench" / "scenes" / "preset_ab"
PACK = REPO / "nex_bench" / "presets" / "preset_ab" / "presets.v1.json"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-14-preset-ab"
DOCS = REPO / "docs" / "benchmarks" / "m09"
BUILDER = DOCS / "tools" / "build_ab.py"
REPORT_JSON = DOCS / "ab.v1.json"
REPORT_MD = DOCS / "AB-REPORT.md"
RUN_IDS = (
    "1794650136-34991024",
    "1794650182-34960454",
    "1794650224-33725612",
    "1794653881-34012975",
    "1794653926-33742838",
    "1794653968-33563891",
)


def _load_builder():
    spec = importlib.util.spec_from_file_location("nex_m09_build_ab", BUILDER)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load build_ab.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PresetABFilesTests(unittest.TestCase):
    def test_harness_and_evidence_files_exist(self) -> None:
        paths = [
            SCENE / "preset_ab.gd",
            SCENE / "preset_ab.tscn",
            SCENE / "validate_preset_ab.py",
            SCENE / "README.md",
            PACK,
            EVIDENCE / "runs.v1.json",
            EVIDENCE / "SESSION-FACTS.txt",
            EVIDENCE / "ANALYSIS.md",
            EVIDENCE / "SHA256SUMS.txt",
            REPORT_JSON,
            REPORT_MD,
            BUILDER,
        ]
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
        for run_id in RUN_IDS:
            with self.subTest(run=run_id):
                self.assertTrue((EVIDENCE / f"gpu_profile_{run_id}.json").is_file())
                self.assertTrue((EVIDENCE / f"gpu_profile_{run_id}.json.validation.json").is_file())

    def test_preset_pack_matches_contract_shape(self) -> None:
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        self.assertEqual("preset_pack.v1", pack["schema_version"])
        self.assertEqual("preset-ab-pack", pack["pack_id"])
        presets = {preset["preset_id"]: preset for preset in pack["presets"]}
        self.assertEqual({"ab-low", "ab-high"}, set(presets))
        self.assertEqual(0.5, presets["ab-low"]["settings"]["rendering"]["resolution_scale"])
        self.assertEqual(1.0, presets["ab-high"]["settings"]["rendering"]["resolution_scale"])
        for preset in presets.values():
            self.assertEqual(240, preset["settings"]["performance"]["target_fps"])

    def test_scene_uses_existing_session_and_env_hooks(self) -> None:
        code = (SCENE / "preset_ab.gd").read_text(encoding="utf-8")
        for marker in (
            'const SESSION_SCRIPT := "res://gpu_profile/session.gd"',
            "NEX_PRESET_AB_AUTORUN",
            "NEX_PRESET_AB_PRESET",
            "NEX_GPU_PROFILE_SOURCE_SHA",
            "DisplayServer.VSYNC_DISABLED",
            "Engine.max_fps = 240",
            "const DEFAULT_PROXY_COUNT := 200",
            "NEX_PRESET_AB_PROXY_COUNT",
            '"effect_mode": "lights"',
            "session.begin(get_viewport()",
            "session.step(delta, get_viewport())",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)

    def test_validator_expects_harness_provenance(self) -> None:
        code = (SCENE / "validate_preset_ab.py").read_text(encoding="utf-8")
        for marker in ('EXPECTED_SCENE = "Preset A/B/A"', "EXPECTED_PROXY_COUNTS = (25, 50, 100, 200)", 'EXPECTED_EFFECT_MODE = "lights"', "EXPECTED_MAX_FPS = 240", "EXPECTED_VSYNC = 0", "canonical.validate_report"):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)


class PresetABEvidenceTests(unittest.TestCase):
    def test_captures_are_complete_and_consistent(self) -> None:
        manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        self.assertEqual("preset_ab_runs.v1", manifest["schema_version"])
        self.assertEqual(6, len(manifest["runs"]))
        for entry in manifest["runs"]:
            with self.subTest(run=entry["run_id"]):
                document = json.loads((EVIDENCE / f"gpu_profile_{entry['run_id']}.json").read_text(encoding="utf-8"))
                self.assertEqual("COMPLETE", document["run_status"])
                self.assertEqual(manifest["source_sha"], document["source_sha"])
                self.assertEqual("Preset A/B/A", document["workload"]["scene"])
                self.assertEqual(200, document["workload"]["proxy_count"])
                self.assertEqual("lights", document["workload"]["effect_mode"])
                self.assertEqual(240, document["settings"]["max_fps"])
                self.assertEqual(0, document["settings"]["vsync_mode"])

    def test_validations_pass(self) -> None:
        for run_id in RUN_IDS:
            with self.subTest(run=run_id):
                validation = json.loads((EVIDENCE / f"gpu_profile_{run_id}.json.validation.json").read_text(encoding="utf-8"))
                self.assertEqual("PASS", validation["status"])

    def test_sha256sums_match_every_file(self) -> None:
        lines = [line for line in (EVIDENCE / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(15, len(lines))
        for line in lines:
            digest, name = line.split(" *", 1)
            path = EVIDENCE / name
            with self.subTest(name=name):
                self.assertTrue(path.is_file())
                self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())


class PresetABReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = _load_builder()
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_report_has_three_runs_and_deltas(self) -> None:
        self.assertEqual("m09_preset_ab.v1", self.report["schema_version"])
        self.assertEqual(6, len(self.report["runs"]))
        self.assertEqual("MEASURED_COST_OBSERVED", self.report["verdict"])
        self.assertEqual(499.3, self.report["deltas_high_vs_low"]["gpu_p95_pct"])
        self.assertEqual(3, self.report["baselines"]["ab-low"]["runs"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        rebuilt = self.builder.build_report()
        self.assertEqual(self.report, rebuilt)
        self.assertEqual(self.builder.render_json(rebuilt), REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.builder.render_markdown(rebuilt), REPORT_MD.read_text(encoding="utf-8"))

    def test_limits_and_no_fabricated_gain(self) -> None:
        limitations = " ".join(self.report["limitations"]).lower()
        for expected in ("single session", "no cross-scene", "vsync disabled", "not device vram"):
            with self.subTest(expected=expected):
                self.assertIn(expected, limitations)
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        for forbidden in ("fps improved", "benchmark passed", "universal gain", "quality verified"):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()

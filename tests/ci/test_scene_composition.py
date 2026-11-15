"""Structural and reproducibility tests for the M08 scene-composition dataset."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "render2_5d" / "composition"
SCRIPT = MODULE / "scene_composition.gd"
EVIDENCE = MODULE / "evidence" / "scene-composition-2026-11-15.json"
MANIFEST = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m02-analysis" / "runs.v1.json"
REPORT = REPO / "docs" / "benchmarks" / "m08" / "scene-composition.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m08" / "SCENE-COMPOSITION.md"
TOOL = REPO / "docs" / "benchmarks" / "m08" / "tools" / "build_scene_composition.py"


class SceneCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.scenes = {entry["scene_id"]: entry for entry in cls.evidence["scenes"]}

    def test_evidence_binds_the_m02_manifest(self) -> None:
        self.assertEqual("m08_scene_composition_run.v1", self.evidence["schema_version"])
        self.assertEqual("d218525cbd7cd84b5c69f5e52577a6244f8733b6", self.evidence["source_sha"])
        self.assertEqual(hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                         self.evidence["analysis_manifest_sha256"])
        self.assertEqual(["corridor_static", "arena_combat", "dense_city"],
                         [entry["scene_id"] for entry in self.evidence["scenes"]])

    def test_corridor_is_safe_and_arena_city_report_z_fight(self) -> None:
        corridor = self.scenes["corridor_static"]["report"]
        self.assertEqual("SAFE_CONFIG_HEURISTIC", corridor["verdict"])
        self.assertEqual([], corridor["conflicts"])
        for scene_id in ("arena_combat", "dense_city"):
            with self.subTest(scene=scene_id):
                report = self.scenes[scene_id]["report"]
                self.assertEqual("CONFLICTS_REPORTED", report["verdict"])
                self.assertEqual([("base_z_fight_risk", "medium")],
                                 [(item["code"], item["severity"]) for item in report["conflicts"]])
                self.assertEqual(4, report["base_3d_plan"]["z_fight_risks"])
                self.assertEqual(0, report["base_3d_plan"]["alpha_over_critical"])
                self.assertEqual(0, report["base_3d_plan"]["overlay_gameplay_conflicts"])

    def test_every_plan_has_four_layers_and_two_critical_entities(self) -> None:
        for scene_id, entry in self.scenes.items():
            with self.subTest(scene=scene_id):
                report = entry["report"]
                self.assertEqual(["background", "gameplay", "foreground", "hud"],
                                 [layer["layer_id"] for layer in report["layers"]])
                self.assertEqual(["player", "threat"],
                                 [entity["entity_id"] for entity in report["critical_entities"]])
                self.assertEqual({"high": 0}, {"high": report["summary"]["high"]})

    def test_builder_reproduces_committed_outputs(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("M08_SCENE_COMPOSITION_CHECK_PASS: 3 runs", result.stdout)

    def test_report_matches_evidence(self) -> None:
        self.assertEqual("m08_scene_composition.v1", self.report["schema_version"])
        self.assertEqual("COMPOSITION_PLANNING_DERIVED", self.report["verdict"])
        self.assertEqual(3, self.report["runs"])
        self.assertEqual({"SAFE_CONFIG_HEURISTIC", "CONFLICTS_REPORTED"},
                         {entry["verdict"] for entry in self.report["scenes"]})
        self.assertEqual(64, len(self.report["evidence_sha256"]))

    def test_script_is_planning_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("CanvasLayer", "Viewport", "ShaderMaterial", "RenderingServer", "SubViewport"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn("composition_planner.gd", source)

    def test_no_visual_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        for forbidden in ("visual quality verified", "fps improved", "rendered benchmark", "game feel verified"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()

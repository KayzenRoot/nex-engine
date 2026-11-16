"""Acceptance tests for the M07 render2d reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m07"
RUNTIME = PACK / "m07-runtime.v1.json"
GATE = PACK / "M07-FINAL-GATE.md"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m07"
IMAGES = EVIDENCE / "images"
PLANNER_LOG = REPO / "nex_modules" / "render2d" / "canvas" / "evidence" / "headless-smoke-2026-11-13.log"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0018-M07-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M07-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M07-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
MODES = {"baseline", "lighting", "shadows", "normal", "particles", "parallax",
         "quality_low", "quality_medium", "quality_high"}


class M07FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, GATE, PLANNER_LOG,
                     EVIDENCE / "runs.v1.json", EVIDENCE / "SHA256SUMS.txt"):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_manifest_has_nine_validated_runs(self) -> None:
        self.assertEqual("m07_lab_runs.v1", self.manifest["schema_version"])
        self.assertEqual(self.runtime["source_sha"], self.manifest["source_sha"])
        self.assertEqual(9, len(self.manifest["runs"]))
        self.assertEqual(MODES, {entry["mode"] for entry in self.manifest["runs"]})
        for entry in self.manifest["runs"]:
            with self.subTest(run=entry["run_id"]):
                self.assertTrue((EVIDENCE / entry["file"]).is_file())
                self.assertTrue((EVIDENCE / f"{entry['file']}.validation.json").is_file())

    def test_planner_smoke_is_verified(self) -> None:
        self.assertEqual(46, self.runtime["s01"]["planner_checks"])
        self.assertEqual("CANVAS_PLANNER_VERIFIED", self.runtime["s01"]["verdict"])
        self.assertIn("NEX_M07_S01_SMOKE_PASS: 46 checks", PLANNER_LOG.read_text(encoding="utf-8"))

    def test_visual_evidence_is_complete(self) -> None:
        self.assertEqual(9, len(list(IMAGES.glob("*.png"))))
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertTrue((IMAGES / f"m07_{mode}.png").is_file())

    def test_lighting_and_shadows_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertLess(rows["baseline"]["gpu_p95_ms"], rows["lighting"]["gpu_p95_ms"])
        self.assertLess(rows["lighting"]["gpu_p95_ms"], rows["shadows"]["gpu_p95_ms"])
        self.assertGreater(rows["lighting"]["changed_pixels_pct"], 0.0)
        self.assertGreater(self.runtime["s03"]["shadows_vs_lighting"]["changed_pixels_pct"], 0.0)
        self.assertEqual("RENDER2D_LIGHTING_DERIVED", self.runtime["s02"]["verdict"])
        self.assertEqual("RENDER2D_SHADOWS_GO_WITH_LIMITATIONS", self.runtime["s03"]["verdict"])

    def test_normal_maps_and_particles_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertGreater(rows["normal"]["gpu_p95_ms"], rows["lighting"]["gpu_p95_ms"])
        self.assertGreater(self.runtime["s04"]["normal_vs_lighting"]["changed_pixels_pct"], 0.0)
        self.assertGreater(rows["particles"]["changed_pixels_pct"], 0.0)
        self.assertEqual("RENDER2D_NORMAL_MAPS_GO_WITH_LIMITATIONS", self.runtime["s04"]["verdict"])
        self.assertEqual("RENDER2D_PARTICLES_GO_WITH_LIMITATIONS", self.runtime["s05"]["verdict"])

    def test_parallax_and_quality_profiles_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertGreater(rows["parallax"]["changed_pixels_pct"], 0.0)
        low = rows["quality_low"]["gpu_p95_ms"]
        medium = rows["quality_medium"]["gpu_p95_ms"]
        high = rows["quality_high"]["gpu_p95_ms"]
        self.assertLess(low, medium)
        self.assertLess(medium, high)
        self.assertEqual("RENDER2D_PARALLAX_GO", self.runtime["s06"]["verdict"])
        self.assertEqual("RENDER2D_QUALITY_PROFILES_GO_WITH_LIMITATIONS", self.runtime["s07"]["verdict"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s08"]["decisions"]}
        self.assertEqual("GO", decisions["CanvasPlanner / render2d.v1"])
        self.assertEqual("GO", decisions["ParallaxBackground"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["2D shadows / LightOccluder2D"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["Normal maps / CanvasTexture"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["GPUParticles2D"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m07FinalReference"]
        self.assertEqual("NEX-M07-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([12], block["issues"])
        self.assertEqual("M07_REFERENCE_RENDER2D_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builder_is_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m07/tools/build_m07_runtime.py --check", workflow)

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#12", "M07_RENDER2D_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

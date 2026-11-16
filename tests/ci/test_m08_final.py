"""Acceptance tests for the M08 2.5D composition reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _m0x_final_support import (assert_builder, assert_checkpoint, assert_governance,
                                assert_manifest, assert_no_false_independent)

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m08"
RUNTIME = PACK / "m08-runtime.v1.json"
GATE = PACK / "M08-FINAL-GATE.md"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m08"
IMAGES = EVIDENCE / "images"
PLANNER_LOG = REPO / "nex_modules" / "render2_5d" / "composition" / "evidence" / "headless-smoke-2026-11-13.log"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0019-M08-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M08-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M08-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
MODES = {"baseline", "sprites", "sorted", "shadows", "overlay", "hybrid",
         "perspective", "quality_low", "quality_high"}


class M08FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        assert_governance(self, (ADR, WO, LOCK, RUNTIME, GATE, PLANNER_LOG,
                                 EVIDENCE / "runs.v1.json", EVIDENCE / "SHA256SUMS.txt"))

    def test_manifest_has_nine_validated_runs(self) -> None:
        assert_manifest(self, EVIDENCE, "m08_lab_runs.v1", self.runtime["source_sha"], MODES)

    def test_planner_smoke_is_verified(self) -> None:
        self.assertEqual(69, self.runtime["s01"]["planner_checks"])
        self.assertEqual("COMPOSITION_PLANNER_VERIFIED", self.runtime["s01"]["verdict"])
        self.assertIn("NEX_M08_COMPOSITION_SMOKE_PASS: 69 checks", PLANNER_LOG.read_text(encoding="utf-8"))

    def test_visual_evidence_is_complete(self) -> None:
        self.assertEqual(9, len(list(IMAGES.glob("*.png"))))
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertTrue((IMAGES / f"m08_{mode}.png").is_file())

    def test_sprites_and_sorting_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertLess(rows["baseline"]["gpu_p95_ms"], rows["sprites"]["gpu_p95_ms"])
        self.assertGreater(rows["sprites"]["changed_pixels_pct"], 0.0)
        self.assertEqual(0.0, self.runtime["s02"]["sorted_vs_sprites"]["changed_pixels_pct"])
        self.assertEqual("NO_GO", next(item["decision"] for item in self.runtime["s08"]["decisions"]
                                       if item["id"] == "Custom depth sorting"))

    def test_shadows_overlay_hybrid_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertLess(rows["sprites"]["gpu_p95_ms"], rows["shadows"]["gpu_p95_ms"])
        self.assertLess(rows["sprites"]["gpu_p95_ms"], rows["hybrid"]["gpu_p95_ms"])
        self.assertGreater(rows["overlay"]["changed_pixels_pct"], 0.0)
        self.assertGreater(rows["hybrid"]["changed_pixels_pct"], rows["shadows"]["changed_pixels_pct"])
        self.assertEqual("RENDER25D_HYBRID_GO_WITH_LIMITATIONS", self.runtime["s05"]["verdict"])

    def test_camera_and_quality_profiles(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertLess(rows["perspective"]["gpu_p95_ms"], rows["baseline"]["gpu_p95_ms"])
        self.assertGreater(rows["perspective"]["changed_pixels_pct"], 0.0)
        self.assertLess(rows["quality_low"]["gpu_p95_ms"], rows["quality_high"]["gpu_p95_ms"])
        self.assertEqual("RENDER25D_CAMERA_MODES_GO_WITH_LIMITATIONS", self.runtime["s06"]["verdict"])
        self.assertEqual("RENDER25D_QUALITY_PROFILES_GO_WITH_LIMITATIONS", self.runtime["s07"]["verdict"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s08"]["decisions"]}
        self.assertEqual("GO", decisions["CompositionPlanner / composition.v1"])
        self.assertEqual("NO_GO", decisions["Custom depth sorting"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["Hybrid 2.5D composition"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["Perspective camera mode"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        assert_checkpoint(self, self.checkpoint, "m08FinalReference",
                          "NEX-M08-FINAL-REFERENCE-WO-001", [13], "M08_REFERENCE_RENDER25D_ONLY")

    def test_builder_is_enforced(self) -> None:
        assert_builder(self, WORKFLOW, "docs/benchmarks/m08/tools/build_m08_runtime.py --check")

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#13", "M08_RENDER25D_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

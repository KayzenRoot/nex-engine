"""Acceptance tests for the M10 animation/feedback reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _m0x_final_support import (assert_builder, assert_checkpoint, assert_governance,
                                assert_manifest, assert_no_false_independent)

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m10"
RUNTIME = PACK / "m10-runtime.v1.json"
GATE = PACK / "M10-FINAL-GATE.md"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-17-m10"
IMAGES = EVIDENCE / "images"
PLANNER_LOG = REPO / "nex_modules" / "animation" / "combat_feedback" / "evidence" / "headless-smoke-2026-11-13.log"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0021-M10-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M10-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M10-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
MODES = {"baseline", "blend", "attack", "hit", "hitstop", "camera", "vfx",
         "quality_low", "quality_high"}


class M10FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        assert_governance(self, (ADR, WO, LOCK, RUNTIME, GATE, PLANNER_LOG,
                                 EVIDENCE / "runs.v1.json", EVIDENCE / "SHA256SUMS.txt"))

    def test_manifest_has_nine_validated_runs(self) -> None:
        assert_manifest(self, EVIDENCE, "m10_lab_runs.v1", self.runtime["source_sha"], MODES)

    def test_planner_smoke_is_verified(self) -> None:
        self.assertEqual(66, self.runtime["s01"]["planner_checks"])
        self.assertEqual("FEEDBACK_PLANNER_VERIFIED", self.runtime["s01"]["verdict"])
        self.assertIn("NEX_M10_FEEDBACK_SMOKE_PASS: 66 checks", PLANNER_LOG.read_text(encoding="utf-8"))

    def test_visual_evidence_is_complete(self) -> None:
        self.assertEqual(9, len(list(IMAGES.glob("*.png"))))
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertTrue((IMAGES / f"m10_{mode}.png").is_file())

    def test_blending_and_hit_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertGreater(rows["blend"]["gpu_p95_ms"], rows["baseline"]["gpu_p95_ms"])
        self.assertGreater(rows["blend"]["changed_pixels_pct"], 0.0)
        self.assertGreater(rows["hit"]["changed_pixels_pct"], 0.0)
        self.assertEqual("ANIMATION_BLENDING_DERIVED", self.runtime["s02"]["verdict"])
        self.assertEqual("HIT_REACTION_GO_WITH_LIMITATIONS", self.runtime["s03"]["verdict"])

    def test_hitstop_is_visual_only(self) -> None:
        self.assertEqual(0.0, self.runtime["s04"]["hitstop_vs_attack"]["changed_pixels_pct"])
        self.assertEqual("HITSTOP_VISUAL_ONLY", self.runtime["s04"]["verdict"])
        self.assertLess(self.runtime["s04"]["rows"]["hitstop"]["gpu_p95_ms"], 1.0)

    def test_camera_vfx_and_quality_are_measured(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertGreater(rows["camera"]["changed_pixels_pct"], 0.0)
        self.assertGreater(rows["vfx"]["changed_pixels_pct"], 0.0)
        self.assertGreater(rows["vfx"]["gpu_p95_ms"], rows["baseline"]["gpu_p95_ms"])
        self.assertLess(rows["quality_low"]["gpu_p95_ms"], rows["quality_high"]["gpu_p95_ms"])
        self.assertEqual("SMOOTH_CAMERA_GO_WITH_LIMITATIONS", self.runtime["s05"]["verdict"])
        self.assertEqual("VFX_SYNC_GO_WITH_LIMITATIONS", self.runtime["s06"]["verdict"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s08"]["decisions"]}
        self.assertEqual("GO", decisions["FeedbackPlanner / feedback.v1"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["AnimationTree blending"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["Visual hit-stop"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["M05 VFX synchronization"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        assert_checkpoint(self, self.checkpoint, "m10FinalReference",
                          "NEX-M10-FINAL-REFERENCE-WO-001", [15], "M10_REFERENCE_ANIMATION_ONLY")

    def test_builder_is_enforced(self) -> None:
        assert_builder(self, WORKFLOW, "docs/benchmarks/m10/tools/build_m10_runtime.py --check")

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#15", "M10_ANIMATION_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        assert_no_false_independent(self, (ADR, WO, GATE))


if __name__ == "__main__":
    unittest.main()

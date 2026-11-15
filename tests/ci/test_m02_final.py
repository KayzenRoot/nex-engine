"""Acceptance tests for the M02 full reference-renderer gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m02"
RUNTIME = PACK / "runtime.v1.json"
GATE = PACK / "M02-FINAL-GATE.md"
LEDGER = PACK / "qa-ledger.v1.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0013-M02-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M02-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M02-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"


class M02FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, GATE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_s01_camera_math_and_aspects(self) -> None:
        s01 = self.runtime["s01"]
        self.assertLess(s01["camera_math"]["round_trip_max_error_m"], 0.01)
        self.assertLess(s01["camera_math"]["fast_follow_max_screen_step_px"], 250.0)
        self.assertEqual(4, len(s01["aspects"]))
        self.assertEqual({"16x9", "16x10", "21x9", "4x3"}, {item["tag"] for item in s01["aspects"]})

    def test_s02_reveal_is_rendered(self) -> None:
        for scene in self.runtime["s02"]["scenes"]:
            with self.subTest(scene=scene["scene_id"]):
                self.assertEqual(0, scene["hidden_summary"]["active_reveals"])
                self.assertEqual(1, scene["revealed_summary"]["active_reveals"])
                self.assertGreater(scene["changed_pixels_pct"], 0.0)
                self.assertGreater(scene["gpu_delta_pct"], 0.0)
        self.assertEqual("SIGHTLINE_RENDERED", self.runtime["s02"]["verdict"])

    def test_s03_overlay_has_no_conflicts(self) -> None:
        for scene in self.runtime["s03"]["scenes"]:
            with self.subTest(scene=scene["scene_id"]):
                plan = scene["plan"]
                self.assertEqual(0, plan["z_fight_risks"])
                self.assertEqual(0, plan["alpha_over_critical"])
                self.assertEqual(0, plan["overlay_gameplay_conflicts"])
                self.assertGreater(scene["changed_pixels_pct"], 0.0)
        self.assertEqual("DEPTH_OVERLAY_SAFE", self.runtime["s03"]["verdict"])

    def test_s04_declares_custom_compositor_no_go(self) -> None:
        self.assertEqual("NO_GO_CUSTOM_COMPOSITOR", self.runtime["s04"]["verdict"])
        self.assertEqual(self.runtime["s04"]["off"]["metrics"]["ghosting"],
                         self.runtime["s04"]["on"]["metrics"]["ghosting"])
        self.assertEqual(self.runtime["s04"]["off"]["metrics"]["flicker"],
                         self.runtime["s04"]["on"]["metrics"]["flicker"])

    def test_s05_profiles_and_passport(self) -> None:
        s05 = self.runtime["s05"]
        self.assertEqual("RUNTIME_PROBED", s05["passport"]["probe_status"])
        profiles = {item["profile"]: item for item in s05["profiles"]}
        self.assertEqual({"quality", "balanced", "performance"}, set(profiles))
        self.assertGreater(profiles["quality"]["gpu_p95_ms"], profiles["performance"]["gpu_p95_ms"])
        self.assertGreater(profiles["quality"]["renderer_allocation_bytes_median"],
                           profiles["performance"]["renderer_allocation_bytes_median"])

    def test_qa_ledger_reflects_rendered_components(self) -> None:
        components = {item["id"]: item for item in self.ledger["components"]}
        for component_id in ("S01", "S02", "S03", "S05"):
            with self.subTest(id=component_id):
                self.assertEqual("PASS", components[component_id]["scene_comparison"])
                self.assertEqual("MEASURED", components[component_id]["performance"])
                self.assertTrue(components[component_id]["scene_evidence"])
                self.assertTrue(components[component_id]["performance_evidence"])
        self.assertEqual("PASS", components["S04"]["scene_comparison"])
        self.assertEqual("INCONCLUSIVE_NOT_RUN", components["S04"]["performance"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m02FinalReference"]
        self.assertEqual("NEX-M02-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([7, 28, 29, 30, 31, 32, 33, 34], block["issues"])
        self.assertEqual("M02_REFERENCE_RENDERER_ONLY", block["runtimeAdmission"])
        self.assertEqual("NO_GO_CUSTOM_COMPOSITOR", block["s04"]["verdict"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builder_is_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m02/tools/build_m02_runtime.py --check", workflow)

    def test_gate_covers_the_closed_issues(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("S01", "S02", "S03", "S04", "S05", "S06", "S07",
                       "#28", "#29", "#30", "#31", "#32", "#33", "#34", "#7"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

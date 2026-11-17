"""Acceptance tests for the original NEX ARPG reference demo."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _m0x_final_support import (assert_checkpoint, assert_governance,
                                assert_no_false_independent)

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "nex_bench" / "scenes" / "arpg_demo"
SCENE = DEMO / "arpg_demo.tscn"
SCRIPT = DEMO / "arpg_demo.gd"
HUD = DEMO / "arpg_hud.gd"
HUB = REPO / "nex_bench" / "hub.gd"
SMOKE = REPO / "nex_bench" / "smoke.gd"
BUILD = REPO / "docs" / "benchmarks" / "build"
REPORT = BUILD / "reference-build.v1.json"
GATE = REPO / "docs" / "benchmarks" / "arpg" / "ARPG-DEMO-GATE.md"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0025-ARPG-DEMO.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-ARPG-DEMO-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-ARPG-DEMO-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"


class ArpgDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        assert_governance(self, (ADR, WO, LOCK, GATE, SCENE, SCRIPT, HUD,
                                 BUILD / "evidence" / "nex-mode-arpg.png",
                                 BUILD / "evidence" / "arpg-attack.png",
                                 BUILD / "evidence" / "arpg-move.png"))

    def test_scene_and_hub_are_integrated(self) -> None:
        scene = SCENE.read_text(encoding="utf-8")
        self.assertIn('name="ArpgDemo"', scene)
        self.assertIn("arpg_demo.gd", scene)
        hub = HUB.read_text(encoding="utf-8")
        for token in ('"ARPG DEMO"', 'DEMO_SCENE', "KEY_F5", "_activate_mode(4)"):
            with self.subTest(token=token):
                self.assertIn(token, hub)
        self.assertIn("NEX_NATIVE_ARPG_DEMO_PASS", SMOKE.read_text(encoding="utf-8"))

    def test_demo_is_procedural_and_original(self) -> None:
        for path in (SCRIPT, HUD):
            text = path.read_text(encoding="utf-8")
            for forbidden in ("res://assets", "http://", "https://", ".glb", ".png", ".jpg", ".exr"):
                with self.subTest(path=path.name, forbidden=forbidden):
                    self.assertNotIn(forbidden, text)
        self.assertIn("TRAINING DUMMY", HUD.read_text(encoding="utf-8"))
        self.assertIn("LIFE", HUD.read_text(encoding="utf-8"))
        self.assertIn("MANA", HUD.read_text(encoding="utf-8"))

    def test_build_evidence_includes_the_demo(self) -> None:
        artifact = self.report["artifact"]
        self.assertEqual(109548888, artifact["bytes"])
        self.assertEqual("0f93eaa9c38c061ed7fae19009511dafd5d9f26eef806ac9f768393b7d6a3bdc",
                         artifact["sha256"])
        captures = {Path(item["file"]).name for item in self.report["gui_captures"]}
        self.assertIn("nex-mode-arpg.png", captures)
        self.assertEqual(6, len(captures))
        self.assertEqual("PASS", self.report["checks"]["gui"])

    def test_checkpoint_block_records_the_demo(self) -> None:
        assert_checkpoint(self, self.checkpoint, "arpgDemo",
                          "NEX-ARPG-DEMO-WO-001", [303], "ARPG_REFERENCE_DEMO_ONLY")

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#303", "ARPG_REFERENCE_DEMO_VERIFIED", "Nenhuma paridade com PoE2",
                       "DISTRIBUTION_TRADEMARK_PENDING", "100 → 82"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        assert_no_false_independent(self, (ADR, WO, GATE))


if __name__ == "__main__":
    unittest.main()

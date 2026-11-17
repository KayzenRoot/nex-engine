"""Acceptance tests for the M12 final brand-system reference gate."""
from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path

from _m0x_final_support import (assert_builder, assert_checkpoint, assert_governance,
                                assert_no_false_independent)

REPO = Path(__file__).resolve().parents[2]
BRAND = REPO / "assets" / "brand"
PACK = REPO / "docs" / "benchmarks" / "m12"
REPORT = PACK / "brand-kit.v1.json"
GATE = PACK / "M12-FINAL-GATE.md"
IDENTITY = BRAND / "identity.v1.json"
SMOKE = REPO / "nex_modules" / "brand" / "tokens" / "evidence" / "m12-final-identity-2026-11-17.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0023-M12-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M12-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M12-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
PROJECT = REPO / "nex_bench" / "project.godot"
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class M12FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
        cls.smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        assert_governance(self, (ADR, WO, LOCK, REPORT, GATE, IDENTITY, SMOKE,
                                 BRAND / "wordmark.svg", BRAND / "BRAND-GUIDELINES.md",
                                 PACK / "BRAND-KIT.md", PACK / "tools" / "build_brand_kit.py",
                                 REPO / "nex_modules" / "brand" / "tokens" / "render_brand_assets.gd"))

    def test_final_smoke_passes(self) -> None:
        self.assertEqual("m12_final_identity.v1", self.smoke["schema_version"])
        self.assertEqual("PASS", self.smoke["verdict"])
        self.assertEqual(14, self.smoke["checks"])
        self.assertEqual([], self.smoke["failures"])
        self.assertEqual("READY_FOR_UI", self.smoke["report"]["verdict"])

    def test_brand_kit_report_is_measured(self) -> None:
        self.assertEqual("m12_brand_kit.v1", self.report["schema_version"])
        self.assertEqual("BRAND_SYSTEM_READY_FOR_UI", self.report["verdict"])
        self.assertEqual(list(SIZES), self.report["icons"]["app_icon_sizes"])
        self.assertEqual(10, self.report["icons"]["ui_icons"])
        self.assertEqual(47845, self.report["icons"]["ico_bytes"])
        self.assertEqual(45394, self.report["icons"]["icns_bytes"])
        self.assertEqual(16.48, self.report["contrast"]["mist_on_graphite"])
        self.assertEqual(4.27, self.report["contrast"]["cobalt_on_graphite"])

    def test_identity_hashes_match_the_assets(self) -> None:
        logo = self.identity["logo"]
        self.assertEqual(_sha(BRAND / "logo-mark.svg"), logo["mark_sha256"])
        self.assertEqual(_sha(BRAND / "wordmark.svg"), logo["wordmark_sha256"])
        self.assertEqual(_sha(BRAND / "logo-monochrome.svg"), logo["monochrome_sha256"])
        self.assertEqual([0, 0, 190, 100], logo["wordmark_view_box"])
        self.assertEqual(5, len(self.identity["palette"]))
        palette = json.loads((BRAND / "palette.v1.json").read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in palette["colors"]],
                         [item["token"] for item in self.identity["palette"]])
        self.assertEqual(7.0, self.identity["accessibility"]["min_text_contrast_ratio"])

    def test_app_icons_and_containers_are_valid(self) -> None:
        for size in SIZES:
            with self.subTest(size=size):
                data = (BRAND / "app-icons" / f"nex-engine-{size}.png").read_bytes()
                self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
                self.assertEqual((size, size), struct.unpack(">II", data[16:24]))
        ico = (BRAND / "app-icons" / "nex-engine.ico").read_bytes()
        reserved, kind, count = struct.unpack("<HHH", ico[:6])
        self.assertEqual((0, 1, 9), (reserved, kind, count))
        icns = (BRAND / "app-icons" / "nex-engine.icns").read_bytes()
        self.assertEqual(b"icns", icns[:4])
        self.assertEqual(len(icns), struct.unpack(">I", icns[4:8])[0])

    def test_wordmark_has_no_font_dependency(self) -> None:
        for name in ("logo-primary.svg", "wordmark.svg"):
            with self.subTest(name=name):
                text = (BRAND / name).read_text(encoding="utf-8")
                self.assertNotIn("<text", text)
                self.assertNotIn("font-family", text)

    def test_no_engine_integration(self) -> None:
        project = PROJECT.read_text(encoding="utf-8")
        self.assertNotIn("assets/brand", project)
        self.assertNotIn("brand", project.lower())

    def test_checkpoint_block_records_the_admission(self) -> None:
        assert_checkpoint(self, self.checkpoint, "m12FinalReference",
                          "NEX-M12-FINAL-REFERENCE-WO-001", [17], "M12_REFERENCE_BRAND_SYSTEM_ONLY")

    def test_builder_is_enforced(self) -> None:
        assert_builder(self, WORKFLOW, "docs/benchmarks/m12/tools/build_brand_kit.py --check")

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#17", "M12_BRAND_SYSTEM_REFERENCE_COMPLETE",
                       "Nenhuma paridade com PoE2", "DISTRIBUTION_TRADEMARK_PENDING"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        assert_no_false_independent(self, (ADR, WO, GATE))


if __name__ == "__main__":
    unittest.main()

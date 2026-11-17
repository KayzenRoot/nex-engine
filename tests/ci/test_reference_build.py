"""Acceptance tests for the Windows x86_64 reference build."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

from _m0x_final_support import (assert_builder, assert_checkpoint, assert_governance,
                                assert_no_false_independent)

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "docs" / "benchmarks" / "build"
REPORT = BUILD / "reference-build.v1.json"
GATE = BUILD / "REFERENCE-BUILD-GATE.md"
PRESET = REPO / "nex_bench" / "export_presets.cfg"
ICON = REPO / "nex_bench" / "icon.ico"
BRAND_ICON = REPO / "assets" / "brand" / "app-icons" / "nex-engine.ico"
SCRIPT = REPO / "scripts" / "build_reference_export.py"
CAPTURE_SCRIPT = REPO / "scripts" / "capture-reference-gui.ps1"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0024-REFERENCE-BUILD-EXPORT.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-REFERENCE-BUILD-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-REFERENCE-BUILD-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
CAPTURES = ("nex-mode-corridor.png", "nex-mode-arena.png", "nex-mode-dense-city.png",
            "nex-mode-density.png", "nex-mode-diagnostics.png")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} is not a PNG")
    return struct.unpack(">II", data[16:24])


class ReferenceBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        assert_governance(self, (ADR, WO, LOCK, REPORT, GATE, PRESET, ICON, SCRIPT,
                                 CAPTURE_SCRIPT, BUILD / "REFERENCE-BUILD.md"))

    def test_preset_and_icon_are_bounded(self) -> None:
        preset = PRESET.read_text(encoding="utf-8")
        for token in ('name="Windows Desktop"', 'platform="Windows Desktop"',
                      'binary_format/architecture="x86_64"', "binary_format/embed_pck=true",
                      'application/icon="res://icon.ico"'):
            with self.subTest(token=token):
                self.assertIn(token, preset)
        self.assertEqual(_sha(BRAND_ICON), _sha(ICON))

    def test_evidence_records_a_pass(self) -> None:
        self.assertEqual("nex_reference_build.v1", self.report["schema_version"])
        self.assertEqual("REFERENCE_BUILD_PASS", self.report["verdict"])
        self.assertEqual({"staged_project_smoke": "PASS", "export": "PASS",
                          "exported_headless": "PASS", "gui": "PASS"}, self.report["checks"])
        artifact = self.report["artifact"]
        self.assertEqual("build/NEXEngine.exe", artifact["path"])
        self.assertEqual(109522728, artifact["bytes"])
        self.assertEqual("9aae397ec302a4ba280db2e856abd15550ccab5bbfb989edd3cae1a74eb22f8c",
                         artifact["sha256"])

    def test_gui_captures_are_clean_window_images(self) -> None:
        captures = self.report["gui_captures"]
        self.assertEqual(5, len(captures))
        self.assertEqual(set(CAPTURES), {Path(item["file"]).name for item in captures})
        for item in captures:
            with self.subTest(file=item["file"]):
                path = BUILD / item["file"]
                self.assertTrue(path.is_file())
                self.assertEqual(_sha(path), item["sha256"])
                self.assertEqual((1296, 759), _png_size(path))
                self.assertEqual((1296, 759), (item["width"], item["height"]))

    def test_check_mode_passes(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=REPO,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("REFERENCE_BUILD_CHECK_PASS", result.stdout)

    def test_artifact_is_not_tracked(self) -> None:
        tracked = subprocess.run(["git", "ls-files", "build/NEXEngine.exe"], cwd=REPO,
                                 capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual("", tracked)
        self.assertIn("build/", (REPO / ".gitignore").read_text(encoding="utf-8"))

    def test_checkpoint_block_records_the_build(self) -> None:
        assert_checkpoint(self, self.checkpoint, "referenceBuild",
                          "NEX-REFERENCE-BUILD-WO-001", [300], "REFERENCE_BUILD_EXPORT_ONLY")

    def test_check_is_enforced(self) -> None:
        assert_builder(self, WORKFLOW, "scripts/build_reference_export.py --check")

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#300", "REFERENCE_BUILD_VERIFIED", "Nenhuma paridade com PoE2",
                       "DISTRIBUTION_TRADEMARK_PENDING", "não é versionado"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        assert_no_false_independent(self, (ADR, WO, GATE))


if __name__ == "__main__":
    unittest.main()

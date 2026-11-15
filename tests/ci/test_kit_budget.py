"""Structural and reproducibility tests for the M04 kit-budget analysis."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "materials" / "texturebudget"
SCRIPT = MODULE / "kit_budget.gd"
EVIDENCE = MODULE / "evidence" / "kit-budget-2026-11-15.json"
KIT = REPO / "nex_modules" / "materials" / "kit" / "kit.v1.json"
REPORT = REPO / "docs" / "benchmarks" / "m04" / "kit-budget.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m04" / "KIT-BUDGET.md"
TOOL = REPO / "docs" / "benchmarks" / "m04" / "tools" / "build_kit_budget.py"


class KitBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_evidence_binds_the_kit(self) -> None:
        self.assertEqual("m04_kit_budget_run.v1", self.evidence["schema_version"])
        self.assertEqual("873f4a7d05d3b70912a5112089e3ebfbf068703c", self.evidence["source_sha"])
        self.assertEqual(hashlib.sha256(KIT.read_bytes()).hexdigest(), self.evidence["kit_sha256"])

    def test_planner_result_is_fit_without_findings(self) -> None:
        report = self.evidence["report"]
        self.assertEqual("FIT", report["verdict"])
        self.assertEqual(4, report["materials"])
        self.assertEqual(12, report["texture_refs"])
        self.assertEqual(12, len(report["unique_textures"]))
        self.assertEqual(0, report["duplicate_refs"])
        self.assertEqual(1048572, report["decoded_bytes_dedup"])
        self.assertEqual(0.047, report["atlas"]["pressure_ratio"])
        self.assertEqual([], report["findings"])

    def test_builder_reproduces_committed_outputs(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("M04_KIT_BUDGET_CHECK_PASS: 1 runs", result.stdout)

    def test_report_matches_evidence(self) -> None:
        self.assertEqual("m04_kit_budget.v1", self.report["schema_version"])
        self.assertEqual("FIT", self.report["verdict"])
        self.assertEqual(self.evidence["kit_sha256"], self.report["kit_sha256"])
        self.assertEqual(64, len(self.report["evidence_sha256"]))
        self.assertEqual(12, self.report["unique_textures"])

    def test_script_is_planning_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("RenderingServer", "ImageTexture", "Image.load", "atlas_pack", "ResourceSaver"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn("texture_budget_planner.gd", source)

    def test_no_performance_claim(self) -> None:
        lowered = REPORT_MD.read_text(encoding="utf-8").lower()
        for forbidden in ("fps improved", "performance gain", "quality verified", "rendered benchmark"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()

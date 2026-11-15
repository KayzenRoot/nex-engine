"""Structural and reproducibility tests for the M11 kit asset-pipeline audit."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "nex_modules" / "assets" / "license_audit"
SCRIPT = MODULE / "kit_audit.gd"
EVIDENCE = MODULE / "evidence" / "kit-audit-2026-11-15.json"
KIT = REPO / "nex_modules" / "materials" / "kit" / "kit.v1.json"
REPORT = REPO / "docs" / "benchmarks" / "m11" / "kit-audit.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "m11" / "KIT-AUDIT.md"
TOOL = REPO / "docs" / "benchmarks" / "m11" / "tools" / "build_kit_audit.py"


class KitAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_evidence_binds_the_kit(self) -> None:
        self.assertEqual("m11_kit_audit_run.v1", self.evidence["schema_version"])
        self.assertEqual("7e425920cdaf17c158d46979e68df47e66742724", self.evidence["source_sha"])
        self.assertEqual(hashlib.sha256(KIT.read_bytes()).hexdigest(), self.evidence["kit_sha256"])
        self.assertEqual(12, len(self.evidence["document"]["assets"]))

    def test_audit_has_no_high_findings_but_flags_licenses(self) -> None:
        report = self.evidence["report"]
        self.assertEqual("REVIEW_REQUIRED", report["verdict"])
        self.assertEqual(0, report["summary"]["high"])
        self.assertEqual(12, report["summary"]["medium"])
        self.assertEqual(12, report["summary"]["low"])
        self.assertEqual(12, report["metrics"]["unverified_licenses"])
        self.assertEqual(0, report["metrics"]["failed_stages"])
        self.assertEqual(0, report["metrics"]["pending_stages"])
        self.assertEqual(788844, report["metrics"]["total_cooked_bytes"])
        codes = [item["code"] for item in report["findings"]]
        self.assertEqual(12, codes.count("license_unverified"))
        self.assertEqual(12, codes.count("texture_uncompressed"))

    def test_builder_reproduces_committed_outputs(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("M11_KIT_AUDIT_CHECK_PASS: 1 runs", result.stdout)

    def test_report_matches_evidence(self) -> None:
        self.assertEqual("m11_kit_audit.v1", self.report["schema_version"])
        self.assertEqual("REVIEW_REQUIRED", self.report["verdict"])
        self.assertEqual(12, self.report["metrics"]["assets"])
        self.assertEqual(self.evidence["kit_sha256"], self.report["kit_sha256"])
        self.assertEqual(64, len(self.report["evidence_sha256"]))
        self.assertEqual({"license_unverified": 12, "texture_uncompressed": 12},
                         self.report["findings"])

    def test_script_is_analysis_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("ResourceLoader", "ResourceSaver", "Image.load", "ImageTexture", "RenderingServer", "load(\"res://textures"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn("asset_pipeline_auditor.gd", source)

    def test_no_license_verification_claim(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("licenses_unverified", lowered)
        self.assertNotIn("license verified", lowered)
        self.assertNotIn("verified license", lowered)
        self.assertIn("não é verificação jurídica", lowered)


if __name__ == "__main__":
    unittest.main()

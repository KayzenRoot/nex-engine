"""Tests for the repository-wide SHA256SUMS evidence validator."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from _preset_ab_support import load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "tools" / "validate_evidence.py"
CORRECTION = (REPO / "nex_bench" / "gpu_profile" / "evidence"
              / "windows-rtx5050-2026-10-12-final-head" / "CORRECTION.md")


class EvidenceValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_validate_evidence", TOOL)

    def test_repository_evidence_is_consistent(self) -> None:
        self.assertEqual([], self.tool.validate(REPO))

    def test_repository_has_bundles(self) -> None:
        bundles = [path for path in REPO.rglob("SHA256SUMS.txt") if ".git" not in path.parts]
        self.assertGreaterEqual(len(bundles), 27)

    def test_missing_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SHA256SUMS.txt").write_text("0" * 64 + " *missing.bin\n", encoding="utf-8")
            errors = self.tool.validate(root)
            self.assertTrue(any("missing missing.bin" in error for error in errors))

    def test_tampered_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "asset.bin").write_bytes(b"original")
            (root / "SHA256SUMS.txt").write_text(
                hashlib.sha256(b"different").hexdigest() + " *asset.bin\n", encoding="utf-8")
            errors = self.tool.validate(root)
            self.assertTrue(any("digest mismatch asset.bin" in error for error in errors))

    def test_crlf_variant_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "asset.txt").write_bytes(b"line one\nline two\n")
            (root / "SHA256SUMS.txt").write_text(
                hashlib.sha256(b"line one\r\nline two\r\n").hexdigest() + " *asset.txt\n", encoding="utf-8")
            self.assertEqual([], self.tool.validate(root))

    def test_malformed_line_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SHA256SUMS.txt").write_text("not-a-checksum asset.bin\n", encoding="utf-8")
            errors = self.tool.validate(root)
            self.assertTrue(any("malformed line" in error for error in errors))

    def test_correction_is_recorded(self) -> None:
        text = CORRECTION.read_text(encoding="utf-8")
        self.assertIn("ad93615c062a01dd25ff37678eb1a61b44b44007cbe06653d7d3f8a299a3aadc", text)
        self.assertIn("f3488105dacea7dbf29e0e4166521eb1acfd89463517a71a23870696cb5faec6", text)
        self.assertIn("GPU-DEVICE-SNAPSHOT.txt", text)


if __name__ == "__main__":
    unittest.main()

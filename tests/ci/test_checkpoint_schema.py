"""Schema and coherence tests for the canonical checkpoint validator."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from _preset_ab_support import load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "tools" / "validate_checkpoint.py"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
INDEX = REPO / "docs" / "benchmarks" / "provenance-index.v1.json"


class CheckpointSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_validate_checkpoint", TOOL)
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.index = json.loads(INDEX.read_text(encoding="utf-8"))

    def test_committed_checkpoint_passes(self) -> None:
        self.assertEqual([], self.tool.validate(self.checkpoint, self.index))

    def test_invalid_main_sha_fails(self) -> None:
        mutated = copy.deepcopy(self.checkpoint)
        mutated["mainObservedSha"] = "not-a-sha"
        errors = self.tool.validate(mutated, self.index)
        self.assertTrue(any("mainObservedSha" in error for error in errors))

    def test_pr_without_merge_fails(self) -> None:
        mutated = copy.deepcopy(self.checkpoint)
        block = next(
            value for value in mutated.values()
            if isinstance(value, dict)
            and isinstance(value.get("pr"), int)
            and isinstance(value.get("protectedMergeSha"), str)
        )
        block.pop("protectedMergeSha")
        errors = self.tool.validate(mutated, self.index)
        self.assertTrue(any("merge SHA" in error for error in errors))

    def test_false_independent_approval_fails(self) -> None:
        mutated = copy.deepcopy(self.checkpoint)
        block = next(
            value for value in mutated.values()
            if isinstance(value, dict) and "audit" in value
        )
        block["audit"] = "INDEPENDENT_APPROVED"
        errors = self.tool.validate(mutated, self.index)
        self.assertTrue(any("independent approval" in error for error in errors))

    def test_provenance_count_mismatch_fails(self) -> None:
        mutated = copy.deepcopy(self.index)
        mutated["summary"]["entries"] += 1
        errors = self.tool.validate(self.checkpoint, mutated)
        self.assertTrue(any("entry count" in error for error in errors))

    def test_missing_admission_block_fails(self) -> None:
        mutated = copy.deepcopy(self.checkpoint)
        mutated.pop("m04M05BoundedAdmission")
        errors = self.tool.validate(mutated, self.index)
        self.assertTrue(any("missing admission block" in error for error in errors))

    def test_cli_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(TOOL), "--check"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("CHECKPOINT_SCHEMA_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()

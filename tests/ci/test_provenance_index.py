"""Structural and reproducibility tests for the provenance index."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from _preset_ab_support import assert_builder_reproduces, load_builder

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "docs" / "benchmarks" / "tools" / "build_provenance_index.py"
REPORT_JSON = REPO / "docs" / "benchmarks" / "provenance-index.v1.json"
REPORT_MD = REPO / "docs" / "benchmarks" / "PROVENANCE-INDEX.md"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
SHA = re.compile(r"^[0-9a-f]{40}$")


class ProvenanceIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_build_provenance_index", TOOL)
        cls.report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.entries = {entry["block"]: entry for entry in cls.report["entries"]}

    def test_covers_every_checkpoint_provenance_block(self) -> None:
        expected = {
            key: value["pr"]
            for key, value in self.checkpoint.items()
            if isinstance(value, dict)
            and isinstance(value.get("pr"), int)
            and isinstance(value.get("protectedMergeSha"), str)
        }
        self.assertEqual(expected, {key: entry["pr"] for key, entry in self.entries.items()})
        self.assertEqual(len(expected), self.report["summary"]["entries"])

    def test_merge_shas_are_unique_and_well_formed(self) -> None:
        shas = [entry["protectedMergeSha"] for entry in self.entries.values()]
        self.assertEqual(len(shas), len(set(shas)))
        for entry in self.entries.values():
            with self.subTest(block=entry["block"]):
                self.assertRegex(entry["protectedMergeSha"], SHA)
                self.assertIsInstance(entry["pr"], int)
                self.assertGreater(entry["pr"], 0)

    def test_entries_are_sorted_and_summary_matches(self) -> None:
        prs = [entry["pr"] for entry in self.report["entries"]]
        self.assertEqual(sorted(prs), prs)
        self.assertEqual(prs[0], self.report["summary"]["min_pr"])
        self.assertEqual(prs[-1], self.report["summary"]["max_pr"])
        self.assertEqual(len(set(prs)), len(prs))

    def test_no_false_independent_approval(self) -> None:
        for entry in self.entries.values():
            with self.subTest(block=entry["block"]):
                self.assertNotIn("INDEPENDENT_APPROVED", entry["audit"])
                self.assertIn(entry["audit"], ("", "ADMIN_SOLO_NOT_INDEPENDENT"))
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertNotIn("INDEPENDENT_APPROVED", text)
        self.assertIn("ADMIN_SOLO_NOT_INDEPENDENT", text)

    def test_builder_reproduces_committed_outputs(self) -> None:
        assert_builder_reproduces(self, self.tool, self.report, REPORT_JSON, REPORT_MD)

    def test_index_is_marked_as_navigation_aid(self) -> None:
        self.assertEqual("nex_provenance_index.v1", self.report["schema_version"])
        self.assertEqual(".engineering/CHECKPOINT.json", self.report["source"])
        self.assertEqual("PROVENANCE_INDEX_DERIVED_FROM_CHECKPOINT", self.report["verdict"])
        self.assertIn("checkpoint is the authority", " ".join(self.report["limitations"]))


if __name__ == "__main__":
    unittest.main()

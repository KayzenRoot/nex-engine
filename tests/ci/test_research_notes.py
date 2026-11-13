"""Structural acceptance tests for the NEX M01-S06 research deliverables."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESEARCH = REPO / "docs" / "research" / "nex-m01"
RADAR = RESEARCH / "RADAR-RD-2026-11-13.md"
BACKLOG = RESEARCH / "EXPERIMENT-BACKLOG.md"


class RadarDocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = RADAR.read_text(encoding="utf-8")

    def test_required_sections_exist(self) -> None:
        for heading in (
            "## 1. Método",
            "## 2. Candidatos",
            "## 3. Matriz de experimentos imediatos",
            "## 4. GO/NO_GO",
            "## 5. Limites",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.text)

    def test_candidates_are_unique_and_have_refutable_gates(self) -> None:
        candidates = re.findall(r"### (NEX-RD-\d+) ·", self.text)
        self.assertEqual(10, len(candidates))
        self.assertEqual(len(candidates), len(set(candidates)))
        blocks = re.split(r"\n### ", self.text)[1:]
        for block in blocks:
            with self.subTest(candidate=block.splitlines()[0][:24]):
                self.assertIn("Hipótese:", block)
                self.assertIn("GO:", block)
                self.assertIn("NO_GO:", block)
                self.assertRegex(block, r"Status:\*\* `(RESEARCH_READY|DESIGN_ONLY)`")

    def test_document_disclaims_performance_claims(self) -> None:
        lowered = self.text.lower()
        self.assertIn("não declara desempenho", lowered)
        self.assertIn("anti-patterns", lowered)
        self.assertIn("inconclusive", lowered)

    def test_experiment_matrix_references_existing_harness(self) -> None:
        self.assertIn("E-01", self.text)
        self.assertIn("E-05", self.text)
        self.assertIn("S05", self.text)


class ExperimentBacklogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = BACKLOG.read_text(encoding="utf-8")

    def test_experiment_rows_are_complete(self) -> None:
        rows = [line for line in self.text.splitlines() if line.startswith("| E-")]
        self.assertEqual(5, len(rows))
        ids = [row.split("|")[1].strip() for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        for row in rows:
            with self.subTest(row=row.split("|")[1].strip()):
                self.assertRegex(row, r"READY|DESIGN_ONLY")
                self.assertIn("Gate primário", self.text)

    def test_rules_forbid_fabrication_and_concurrent_gpu(self) -> None:
        lowered = self.text.lower()
        self.assertIn("inconclusive", lowered)
        self.assertIn("gpu concorrente", lowered)
        self.assertIn("sha-256", lowered)


if __name__ == "__main__":
    unittest.main()

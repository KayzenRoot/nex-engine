"""Acceptance tests for the M09 editor-tools reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m09"
RUNTIME = PACK / "editor-tools.v1.json"
GATE = PACK / "M09-FINAL-GATE.md"
LAB = REPO / "nex_modules" / "tools" / "editor_lab"
SMOKE = LAB / "evidence" / "m09-editor-smoke-2026-11-17.json"
RESOLVER_LOG = REPO / "nex_modules" / "tools" / "preset_resolver" / "evidence" / "headless-smoke-2026-11-13.log"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0020-M09-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M09-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M09-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"


class M09FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, GATE, SMOKE, RESOLVER_LOG,
                     LAB / "perf_lint.gd", LAB / "import_guard.gd", LAB / "recipe_builder.gd"):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_editor_smoke_passes(self) -> None:
        self.assertEqual("m09_editor_smoke.v1", self.smoke["schema_version"])
        self.assertEqual("PASS", self.smoke["verdict"])
        self.assertEqual(42, self.smoke["checks"])
        self.assertEqual([], self.smoke["failures"])

    def test_resolver_smoke_passes(self) -> None:
        self.assertEqual(50, self.runtime["s01"]["resolver_checks"])
        self.assertEqual("PRESET_RESOLVER_VERIFIED", self.runtime["s01"]["verdict"])
        self.assertIn("NEX_M09_RESOLVER_SMOKE_PASS: 50 checks", RESOLVER_LOG.read_text(encoding="utf-8"))

    def test_perflint_is_measured(self) -> None:
        self.assertEqual(13, self.runtime["s02"]["findings"])
        self.assertEqual(4, self.runtime["s02"]["errors"])
        self.assertEqual(9, self.runtime["s02"]["warns"])
        self.assertEqual("error", self.runtime["s02"]["highest"])
        for code in ("texture_too_large", "light_budget_exceeded", "draw_call_budget_exceeded",
                     "alpha_overdraw_risk", "sync_load_risk", "missing_license"):
            with self.subTest(code=code):
                self.assertGreaterEqual(self.runtime["s02"]["codes"].get(code, 0), 1)

    def test_import_guard_plan_is_deterministic(self) -> None:
        self.assertEqual({"accepted": 1, "rejected": 3, "noop": 2, "conflicts": 1},
                         self.runtime["s03"]["counts"])
        self.assertEqual(64, len(self.runtime["s03"]["snapshot"]))

    def test_benchmark_recipe_is_valid(self) -> None:
        recipe = self.runtime["s04"]
        self.assertEqual("m09-corridor_static-ab-high-4101", recipe["recipe_id"])
        self.assertEqual("vulkan", recipe["driver"])
        self.assertEqual(3, recipe["runs"])
        self.assertEqual("nex_bench_recipe.v1", self.smoke["recipe"]["schema_version"])
        self.assertIn("--path nex_bench", self.smoke["recipe"]["command"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["decisions"]}
        self.assertEqual("GO", decisions["PresetResolver / preset_pack.v1"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["PerfLint"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["ImportGuard"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["BenchmarkRecipe"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m09FinalReference"]
        self.assertEqual("NEX-M09-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([14], block["issues"])
        self.assertEqual("M09_REFERENCE_EDITOR_TOOLS_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builder_is_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m09/tools/build_m09_editor_tools.py --check", workflow)

    def test_gate_covers_the_closed_issue(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#14", "M09_EDITOR_TOOLS_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

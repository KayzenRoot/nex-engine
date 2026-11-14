"""CI enforcement tests for deterministic M01/M02/M03/M06/M09 builders."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
RULESET = REPO / "ops" / "github" / "nex-main-ruleset.json"
BUILDER_DIRS = {
    "m01": REPO / "docs" / "benchmarks" / "m01" / "tools",
    "m02": REPO / "docs" / "benchmarks" / "m02" / "tools",
    "m03": REPO / "docs" / "benchmarks" / "m03" / "tools",
    "m06": REPO / "docs" / "benchmarks" / "m06" / "tools",
    "m09": REPO / "docs" / "benchmarks" / "m09" / "tools",
}
ALL_PY_MODULES = {"m01", "m02"}
COMMAND = re.compile(
    r"^\s*python3 (docs/benchmarks/(m01|m02|m03|m06|m09)/tools/([a-z0-9_]+\.py)) ([^\n]+)$",
    re.MULTILINE,
)
REQUIRED_JOB = "NEX Fast Lane / Batch Policy Tests"
STEP_NAME = "Verify deterministic builders reproduce committed artifacts"


class BuilderCheckEnforcementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.commands: dict[str, list[str]] = {}
        for path, _, _, args in COMMAND.findall(cls.workflow):
            cls.commands.setdefault(path, []).append(args.strip())

    def test_workflow_step_runs_in_required_job(self) -> None:
        self.assertTrue(WORKFLOW.is_file())
        self.assertIn(STEP_NAME, self.workflow)
        self.assertLess(self.workflow.index(REQUIRED_JOB), self.workflow.index(STEP_NAME))
        ruleset = json.loads(RULESET.read_text(encoding="utf-8"))
        rule = next(r for r in ruleset["rules"] if r["type"] == "required_status_checks")
        contexts = [check["context"] for check in rule["parameters"]["required_status_checks"]]
        self.assertIn(REQUIRED_JOB, contexts)

    def test_every_builder_is_covered(self) -> None:
        expected = set()
        for module, directory in BUILDER_DIRS.items():
            for path in sorted(directory.glob("*.py")):
                if module in ALL_PY_MODULES or path.name.startswith(("build_", "convert_")):
                    expected.add(f"docs/benchmarks/{module}/tools/{path.name}")
        self.assertEqual(expected, set(self.commands))

    def test_all_commands_are_check_only(self) -> None:
        for path, invocations in self.commands.items():
            with self.subTest(path=path):
                self.assertGreaterEqual(len(invocations), 1)
                for args in invocations:
                    self.assertTrue(args.startswith("--check"), args)
                    self.assertNotIn("--write", args)

    def test_full_observation_check_is_enforced(self) -> None:
        args = self.commands["docs/benchmarks/m06/tools/convert_m09_observations.py"]
        self.assertIn("--check", args)
        self.assertIn("--check-full", args)

    def test_full_advisory_check_is_enforced(self) -> None:
        args = self.commands["docs/benchmarks/m06/tools/build_advisories.py"]
        self.assertIn("--check", args)
        self.assertIn("--check-full", args)

    def test_domain_check_is_enforced(self) -> None:
        args = self.commands["docs/benchmarks/m03/tools/build_budget_validation.py"]
        self.assertIn("--check", args)
        self.assertIn("--check-domain", args)

    def test_expected_builder_count(self) -> None:
        # 1 M01 + 1 M02 + 1 M03 (2 invocations) + 4 M06 files (6 invocations) + 13 M09 = 20 files / 23 checks.
        self.assertEqual(20, len(self.commands))
        self.assertEqual(23, sum(len(value) for value in self.commands.values()))


if __name__ == "__main__":
    unittest.main()

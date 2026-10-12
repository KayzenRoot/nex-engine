"""Tests for native build batching, provenance, and fail-closed behavior."""
import importlib.util
import json
import pathlib
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_batch", ROOT / "scripts/ci/native_batch.py")
assert SPEC and SPEC.loader
import sys
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)

BASE = module.BASELINE_SHA
COMMITS = [f"{i:040x}" for i in range(1, 8)]


def make_pr(number, sha, *, label=True, merged=True, wrong_sha=False):
    return {
        "number": number,
        "merged_at": "2026-10-12T00:00:00Z" if merged else None,
        "merge_commit_sha": BASE if wrong_sha else sha,
        "labels": [{"name": "nex-native-module" if label else "documentation"}],
    }


class DecisionTests(unittest.TestCase):
    def run_decision(self, accepted, length=5):
        commits = [{"sha": sha} for sha in COMMITS[:length]]
        associated = {
            sha: [make_pr(i + 100, sha, label=i < accepted)]
            for i, sha in enumerate(COMMITS[:length])
        }
        return module.compute_decision(BASE, COMMITS[length - 1], commits, associated)

    def test_four_accepted_modules_do_not_trigger_build(self):
        d = self.run_decision(4)
        self.assertFalse(d.run_full)
        self.assertEqual(d.to_dict()["module_count"], 4)

    def test_five_accepted_modules_trigger_full_build(self):
        d = self.run_decision(5)
        self.assertTrue(d.run_full)
        self.assertEqual(len(d.accepted_modules), 5)

    def test_docs_not_counted(self):
        d = self.run_decision(0)
        self.assertEqual(d.to_dict()["accepted_module_prs"], [])
        self.assertFalse(d.run_full)

    def test_unmerged_or_wrong_commit_cannot_count(self):
        commits = [{"sha": COMMITS[0]}, {"sha": COMMITS[1]}]
        associations = {
            COMMITS[0]: [make_pr(51, COMMITS[0], merged=False)],
            COMMITS[1]: [make_pr(52, COMMITS[1], wrong_sha=True)],
        }
        d = module.compute_decision(BASE, COMMITS[1], commits, associations)
        self.assertFalse(d.run_full)
        self.assertEqual(len(d.accepted_modules), 0)

    def test_missing_pr_association_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Missing PR association"):
            module.compute_decision(BASE, COMMITS[0], [{"sha": COMMITS[0]}], {})

    def test_malformed_sha_fails_closed(self):
        with self.assertRaises(ValueError):
            module.validate_sha("../refs/heads/main")

    def test_inconsistent_github_compare_fails_closed(self):
        class Fake:
            def request(self, method, path):
                return {"status": "diverged", "total_commits": 2, "commits": []}
        with self.assertRaisesRegex(RuntimeError, "not an ancestor"):
            module.compare_commits(Fake(), "KayzenRoot/nex-engine", BASE, COMMITS[0])

    def test_history_over_limit_stops(self):
        class Fake:
            def request(self, method, path):
                return {"status": "ahead", "total_commits": 251, "commits": []}
        with self.assertRaisesRegex(RuntimeError, "MAX_COMMITS"):
            module.compare_commits(Fake(), "KayzenRoot/nex-engine", BASE, COMMITS[0])

    def test_latest_full_success_is_anchor(self):
        class Fake:
            def request(self, method, path):
                return {"workflow_runs": [
                    {"event": "workflow_dispatch", "head_branch": "main",
                     "status": "completed", "conclusion": "failure", "head_sha": COMMITS[1]},
                    {"event": "workflow_dispatch", "head_branch": "main",
                     "status": "completed", "conclusion": "success", "head_sha": COMMITS[0],
                     "created_at": "2026-10-12T00:00:00Z"},
                ]}
        self.assertEqual(module.latest_anchor(Fake(), "KayzenRoot/nex-engine"), COMMITS[0])

    def test_no_prior_dispatch_uses_reviewed_baseline(self):
        class Fake:
            def request(self, method, path):
                return {"workflow_runs": []}
        self.assertEqual(module.latest_anchor(Fake(), "KayzenRoot/nex-engine"), BASE)

    def test_duplicate_dispatch_detects_exact_sha_only(self):
        class Fake:
            def request(self, method, path):
                return {"workflow_runs": [
                    {"head_sha": COMMITS[0], "status": "completed"},
                    {"head_sha": COMMITS[1], "status": "in_progress"},
                    {"head_sha": COMMITS[2], "status": "queued"},
                ]}
        self.assertTrue(module.native_run_already_active(Fake(), "KayzenRoot/nex-engine", COMMITS[1]))
        self.assertTrue(module.native_run_already_active(Fake(), "KayzenRoot/nex-engine", COMMITS[2]))
        self.assertTrue(module.native_run_already_active(Fake(), "KayzenRoot/nex-engine", COMMITS[0]))

    def test_invalid_object_response_fails_closed(self):
        class Fake:
            def request(self, method, path):
                return []
        with self.assertRaisesRegex(RuntimeError, "malformed object response"):
            module.latest_anchor(Fake(), "KayzenRoot/nex-engine")

    def test_paginated_runs_select_newest_success_by_timestamp(self):
        class Fake:
            def request(self, method, path):
                if path.endswith("&page=1"):
                    older = {"event": "workflow_dispatch", "head_branch": "main",
                             "status": "completed", "conclusion": "success",
                             "head_sha": COMMITS[0], "created_at": "2026-10-10T00:00:00Z"}
                    return {"workflow_runs": [older] * 100}
                if path.endswith("&page=2"):
                    return {"workflow_runs": [{"event": "workflow_dispatch", "head_branch": "main",
                                              "status": "completed", "conclusion": "success",
                                              "head_sha": COMMITS[1], "created_at": "2026-10-12T00:00:00Z"}]}
                raise AssertionError("Unexpected workflow API page")
        self.assertEqual(module.latest_anchor(Fake(), "KayzenRoot/nex-engine"), COMMITS[1])

    def test_response_read_timeout_is_normalized(self):
        class SlowResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return None
            def read(self):
                raise TimeoutError("simulated API read timeout")
        with patch.object(module, "urlopen", return_value=SlowResponse()):
            with self.assertRaisesRegex(RuntimeError, "GitHub API failed"):
                module.GitHub("synthetic-test-token").request("GET", "/repos/KayzenRoot/nex-engine")

    def test_missing_compare_count_is_blocked(self):
        class Fake:
            def request(self, method, path):
                return {"status": "ahead", "commits": []}
        with self.assertRaisesRegex(RuntimeError, "commit count"):
            module.compare_commits(Fake(), "KayzenRoot/nex-engine", BASE, COMMITS[0])

    def test_token_is_required(self):
        with self.assertRaisesRegex(ValueError, "Missing GITHUB_TOKEN"):
            module.GitHub("")


class WorkflowContracts(unittest.TestCase):
    def test_docs_only_cannot_trigger_m00_build(self):
        source = (ROOT / ".github/workflows/nex-m00-smoke.yml").read_text()
        self.assertNotIn("      - '.engineering/evidence/NEX-M00-WO-001-*.md'", source)
        self.assertNotIn("      - '.engineering/checkpoint-deltas/NEX-M00-WO-001-*.md'", source)
        self.assertIn("      - 'tooling/godot/**'", source)
        self.assertIn("      - '.nex/toolchain/**'", source)
        self.assertIn("      - 'tests/m00/**'", source)
        self.assertIn("  workflow_dispatch:", source)

    def test_native_job_is_cancelled_only_for_same_pr_or_branch(self):
        source = (ROOT / ".github/workflows/nex-m00-smoke.yml").read_text()
        self.assertIn("github.event.pull_request.number || github.ref", source)
        self.assertIn("cancel-in-progress: true", source)

    def test_ubuntu_smoke_not_blocked_by_windows_job(self):
        source = (ROOT / ".github/workflows/nex-m00-smoke.yml").read_text()
        ubuntu = source.split("  ubuntu-headless-smoke:", 1)[1]
        self.assertNotIn("needs: [windows-source-build]", ubuntu)
        self.assertIn("Run M00 integrity and negative tests", ubuntu)

    def test_future_native_core_paths_are_hard_triggers(self):
        source = (ROOT / ".github/workflows/nex-m00-smoke.yml").read_text()
        for path in ("engine/**", "src/native/**", "native/**", "godot/**"):
            self.assertIn("      - '" + path + "'", source)

    def test_batch_sentinel_is_protected_main_only(self):
        source = (ROOT / ".github/workflows/nex-native-batch.yml").read_text()
        self.assertIn("branches: [main]", source)
        self.assertIn("actions: write", source)
        self.assertIn("python3 scripts/ci/native_batch.py", source)


if __name__ == "__main__":
    unittest.main()

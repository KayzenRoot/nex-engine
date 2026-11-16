"""Shared assertions for M07/M08 native lab final gates."""
from __future__ import annotations

import json
from pathlib import Path


def assert_governance(test, paths) -> None:
    for path in paths:
        with test.subTest(path=path.name):
            test.assertTrue(path.is_file())


def assert_manifest(test, evidence: Path, schema: str, source_sha: str, modes) -> None:
    manifest = json.loads((evidence / "runs.v1.json").read_text(encoding="utf-8"))
    test.assertEqual(schema, manifest["schema_version"])
    test.assertEqual(source_sha, manifest["source_sha"])
    test.assertEqual(len(modes), len(manifest["runs"]))
    test.assertEqual(set(modes), {entry["mode"] for entry in manifest["runs"]})
    for entry in manifest["runs"]:
        with test.subTest(run=entry["run_id"]):
            test.assertTrue((evidence / entry["file"]).is_file())
            test.assertTrue((evidence / f"{entry['file']}.validation.json").is_file())


def assert_checkpoint(test, checkpoint: dict, key: str, identifier: str, issues: list[int],
                      admission: str) -> None:
    block = checkpoint[key]
    test.assertEqual(identifier, block["id"])
    test.assertEqual(issues, block["issues"])
    test.assertEqual(admission, block["runtimeAdmission"])
    test.assertFalse(block["ciRelaxation"])
    test.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])


def assert_builder(test, workflow: Path, builder: str) -> None:
    test.assertIn(builder, workflow.read_text(encoding="utf-8"))


def assert_no_false_independent(test, paths) -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    test.assertNotIn("INDEPENDENT_APPROVED", combined)
    test.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)

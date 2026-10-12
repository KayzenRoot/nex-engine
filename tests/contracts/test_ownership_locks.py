"""Ownership lease-manifest tests for the exact six-file implementation scope."""
from __future__ import annotations

import copy
import fnmatch
import json
import re
import unittest
from pathlib import Path
from typing import Any

from test_m01_schema import strict_json_loads

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "contracts" / "m01" / "ownership.v1.json"
ALLOWED_WRITE_PATHS = {
    "contracts/m01/scene_manifest.v1.schema.json",
    "contracts/m01/telemetry_run.v1.schema.json",
    "contracts/m01/ownership.v1.json",
    "contracts/README.md",
    "tests/contracts/test_m01_schema.py",
    "tests/contracts/test_ownership_locks.py",
}


def read_manifest() -> dict[str, Any]:
    return strict_json_loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def normalize_path(path: str) -> str:
    """Normalize Windows separators, case and internal dot segments for lock checks."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError("empty path")
    raw = path.replace("\\", "/")
    if raw.startswith("/") or re.match(r"^[a-zA-Z]:", raw):
        raise ValueError("absolute paths are not allowed")
    parts: list[str] = []
    for part in raw.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise ValueError("path escapes repository root")
            parts.pop()
        else:
            parts.append(part.casefold())
    if not parts:
        raise ValueError("empty normalized path")
    return "/".join(parts)


def _ancestor_or_same(left: str, right: str) -> bool:
    return left == right or right.startswith(left.rstrip("/") + "/")


def _static_glob_prefix(path: str) -> str:
    prefix: list[str] = []
    for part in path.split("/"):
        if any(marker in part for marker in "*?["):
            break
        prefix.append(part)
    return "/".join(prefix)


def paths_overlap(left: str, right: str) -> bool:
    left_key = normalize_path(left)
    right_key = normalize_path(right)
    if (
        fnmatch.fnmatchcase(left_key, right_key)
        or fnmatch.fnmatchcase(right_key, left_key)
    ):
        return True
    left_prefix = _static_glob_prefix(left_key)
    right_prefix = _static_glob_prefix(right_key)
    if not left_prefix or not right_prefix:
        return True
    return _ancestor_or_same(left_prefix, right_prefix) or _ancestor_or_same(
        right_prefix, left_prefix
    )


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != "ownership.v1":
        errors.append("schema_version must be ownership.v1")
    if manifest.get("mode") != "EXCLUSIVE_SINGLE_WRITER":
        errors.append("ownership mode must be EXCLUSIVE_SINGLE_WRITER")

    owners = manifest.get("owners", [])
    owner_by_id: dict[str, dict[str, Any]] = {}
    for owner in owners:
        owner_id = owner.get("owner_id")
        if not isinstance(owner_id, str) or not owner_id:
            errors.append("owner_id must be non-empty")
            continue
        if owner_id in owner_by_id:
            errors.append(f"duplicate owner identity: {owner_id}")
        owner_by_id[owner_id] = owner

    expected_roles = {
        "integration-steward": "SOLE_WRITER",
        "mock-scene-consumer": "MOCK_READ_ONLY_CONSUMER",
        "mock-telemetry-consumer": "MOCK_READ_ONLY_CONSUMER",
    }
    if set(owner_by_id) != set(expected_roles):
        errors.append("owner identities differ from the bounded three-owner roster")
    for owner_id, expected_role in expected_roles.items():
        if owner_by_id.get(owner_id, {}).get("role") != expected_role:
            errors.append(f"owner {owner_id} has the wrong role")
    exclusive = manifest.get("exclusive_writer", {})
    writer_id = exclusive.get("owner_id")
    if exclusive.get("max_concurrent_writers") != 1:
        errors.append("exclusive writer limit must be one")
    if owner_by_id.get(writer_id, {}).get("role") != "SOLE_WRITER":
        errors.append("exclusive writer must reference the sole writer owner")

    write_locks = manifest.get("write_locks", [])
    normalized_rows: list[tuple[str, str]] = []
    for row in write_locks:
        path = row.get("path")
        owner_id = row.get("owner_id")
        if owner_id != writer_id:
            errors.append(f"unapproved writer identity for path: {path}")
        try:
            normalized = normalize_path(path)
        except (TypeError, ValueError) as error:
            errors.append(f"invalid writer path {path!r}: {error}")
            continue
        for prior_path, _ in normalized_rows:
            if paths_overlap(prior_path, normalized):
                errors.append(f"overlapping write paths: {prior_path} and {normalized}")
        normalized_rows.append((normalized, owner_id))

    expected = {normalize_path(path) for path in ALLOWED_WRITE_PATHS}
    actual = {path for path, _ in normalized_rows}
    if actual != expected:
        errors.append(
            f"write lock set differs; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )

    consumers = manifest.get("consumers", [])
    consumer_ids: set[str] = set()
    for consumer in consumers:
        consumer_id = consumer.get("consumer_id")
        if not isinstance(consumer_id, str) or not consumer_id:
            errors.append("consumer_id must be non-empty")
            continue
        if consumer_id in consumer_ids:
            errors.append(f"duplicate consumer identity: {consumer_id}")
        consumer_ids.add(consumer_id)
        if consumer.get("kind") != "MOCK":
            errors.append(f"consumer {consumer_id} must be a MOCK")
        if consumer.get("write_paths") != []:
            errors.append(f"consumer {consumer_id} must be read-only")
        if consumer.get("stale_on_breaking_change") is not True:
            errors.append(f"consumer {consumer_id} must become stale on breaking change")
        expected_consumers = {
            "mock-scene-consumer": (
                "contracts/m01/scene_manifest.v1.schema.json",
                ["scene_manifest.v1"],
            ),
            "mock-telemetry-consumer": (
                "contracts/m01/telemetry_run.v1.schema.json",
                ["telemetry_run.v1"],
            ),
        }
        if consumer_id not in expected_consumers:
            errors.append(f"unapproved consumer identity: {consumer_id}")
        else:
            expected_path, expected_versions = expected_consumers[consumer_id]
            if consumer.get("read_paths") != [expected_path]:
                errors.append(f"consumer {consumer_id} has an unexpected read set")
            if consumer.get("schema_versions") != expected_versions:
                errors.append(f"consumer {consumer_id} has an unexpected schema version")
        for path in consumer.get("read_paths", []):
            try:
                if normalize_path(path) not in expected:
                    errors.append(f"consumer {consumer_id} reads an unapproved path")
            except (TypeError, ValueError):
                errors.append(f"consumer {consumer_id} has invalid read path")

    if len(consumers) != 2 or len(consumer_ids) != 2:
        errors.append("exactly two independent mock consumers are required")

    dag = manifest.get("dependency_dag", {})
    nodes = dag.get("nodes", [])
    dependency_map: dict[str, list[str]] = {}
    for node in nodes:
        node_id = node.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            errors.append("dependency node id must be non-empty")
            continue
        if node_id in dependency_map:
            errors.append(f"duplicate dependency node: {node_id}")
        dependency_map[node_id] = node.get("depends_on", [])
    for node_id, dependencies in dependency_map.items():
        for dependency in dependencies:
            if dependency not in dependency_map:
                errors.append(f"unknown dependency {dependency} in {node_id}")

    expected_nodes = {
        "scene_manifest_contract",
        "telemetry_run_contract",
        "mock_scene_consumer",
        "mock_telemetry_consumer",
    }
    if set(dependency_map) != expected_nodes:
        errors.append("dependency DAG nodes differ from the bounded contract/consumer set")
    state: dict[str, int] = {}

    def visit(node_id: str) -> None:
        if state.get(node_id) == 1:
            errors.append(f"dependency cycle includes {node_id}")
            return
        if state.get(node_id) == 2:
            return
        state[node_id] = 1
        for dependency in dependency_map.get(node_id, []):
            if dependency in dependency_map:
                visit(dependency)
        state[node_id] = 2

    for node_id in dependency_map:
        visit(node_id)
    return errors


class OwnershipLockTests(unittest.TestCase):
    def test_canonical_manifest_has_one_writer_and_two_mock_consumers(self) -> None:
        manifest = read_manifest()
        self.assertEqual([], validate_manifest(manifest))
        wrong_mode = copy.deepcopy(manifest)
        wrong_mode["mode"] = "SHARED"
        self.assertTrue(validate_manifest(wrong_mode))
        paths = {row["path"] for row in manifest["write_locks"]}
        self.assertEqual(ALLOWED_WRITE_PATHS, paths)
        self.assertEqual(
            {"integration-steward"},
            {row["owner_id"] for row in manifest["write_locks"]},
        )
        self.assertEqual(2, len(manifest["consumers"]))
        self.assertTrue(all(item["kind"] == "MOCK" for item in manifest["consumers"]))

    def test_duplicate_owner_and_duplicate_path_identity_are_rejected(self) -> None:
        manifest = read_manifest()
        duplicate_owner = copy.deepcopy(manifest)
        duplicate_owner["owners"].append(
            {"owner_id": "integration-steward", "role": "SOLE_WRITER"}
        )
        self.assertTrue(validate_manifest(duplicate_owner))

        duplicate_path = copy.deepcopy(manifest)
        duplicate_path["write_locks"].append(
            {
                "path": "CONTRACTS\\M01\\SCENE_MANIFEST.V1.SCHEMA.JSON",
                "owner_id": "integration-steward",
            }
        )
        self.assertTrue(validate_manifest(duplicate_path))

    def test_windows_alias_traversal_and_ancestor_or_glob_overlap_are_rejected(self) -> None:
        manifest = read_manifest()
        for alias in (
            "contracts/m01/../README.md",
            "contracts",
            "contracts/**",
        ):
            with self.subTest(alias=alias):
                candidate = copy.deepcopy(manifest)
                candidate["write_locks"].append(
                    {"path": alias, "owner_id": "integration-steward"}
                )
                errors = validate_manifest(candidate)
                self.assertTrue(errors)
                self.assertTrue(
                    any("overlapping write paths" in error for error in errors),
                    errors,
                )

        backslash_alias = "TESTS\\CONTRACTS\\TEST_M01_SCHEMA.PY"
        self.assertEqual(
            normalize_path("tests/contracts/test_m01_schema.py"),
            normalize_path(backslash_alias),
        )

    def test_dependency_cycles_and_unknown_nodes_are_rejected(self) -> None:
        manifest = read_manifest()
        cycle = copy.deepcopy(manifest)
        nodes = {node["node_id"]: node for node in cycle["dependency_dag"]["nodes"]}
        nodes["scene_manifest_contract"]["depends_on"] = ["mock_scene_consumer"]
        self.assertTrue(
            any("dependency cycle" in error for error in validate_manifest(cycle))
        )

        unknown = copy.deepcopy(manifest)
        unknown["dependency_dag"]["nodes"][0]["depends_on"] = ["unlisted_contract"]
        self.assertTrue(
            any("unknown dependency" in error for error in validate_manifest(unknown))
        )


if __name__ == "__main__":
    unittest.main()

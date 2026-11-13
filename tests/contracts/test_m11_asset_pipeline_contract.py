"""M11 asset pipeline contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import itertools
import unittest
from typing import Any

from _contract_support import (
    global_unavailable_errors,
    provenance_evidence_errors,
    read_manifest,
    read_schema,
    unavailable_performance,
    unavailable_provenance,
)
from test_m01_schema import limited_schema_errors
from test_ownership_locks import normalize_path

STAGE_ORDER = ("raw", "imported", "cooked", "validated")


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "asset_pipeline.v1",
        "observation_id": "m11-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "assets": [
            {
                "asset_id": "stone-albedo",
                "kind": "texture",
                "source_uri": "res://art/stone_albedo.png",
                "source_sha256": "a" * 64,
                "cooked_bytes": 22369621,
                "stages": [
                    {"stage": "raw", "status": "pass"},
                    {"stage": "imported", "status": "pass"},
                    {"stage": "cooked", "status": "pass", "artifact_sha256": "b" * 64, "tool_id": "cook-texture"},
                    {"stage": "validated", "status": "pass"},
                ],
                "license": {
                    "spdx_id": "MIT",
                    "source_uri": "https://example.invalid/license",
                    "attribution": "NEX fixture",
                    "verification": "verified",
                    "evidence_uri": "evidence://license",
                },
                "import_settings": {"compression": "lossy", "max_dimension_px": 2048, "lod_count": 3},
                "dependencies": [],
            },
            {
                "asset_id": "hero-mesh",
                "kind": "model",
                "source_uri": "res://art/hero.glb",
                "source_sha256": "c" * 64,
                "cooked_bytes": 1048576,
                "stages": [
                    {"stage": "raw", "status": "pass"},
                    {"stage": "imported", "status": "pass"},
                    {"stage": "cooked", "status": "pass", "artifact_sha256": "d" * 64, "tool_id": "cook-mesh"},
                ],
                "license": {
                    "spdx_id": "CC0-1.0",
                    "source_uri": "https://example.invalid/cc0",
                    "attribution": "NEX fixture",
                    "verification": "verified",
                },
                "import_settings": {"compression": "lossless", "lod_count": 4},
                "dependencies": ["stone-albedo"],
            },
        ],
        "policy": {
            "allowed_spdx_ids": ["MIT", "CC0-1.0", "Apache-2.0"],
            "require_attribution": True,
            "require_verified_license": True,
            "allow_unverified": False,
            "require_cooked_artifact": True,
        },
        "budget": {
            "max_assets": 100,
            "max_total_bytes": 104857600,
            "max_texture_bytes": 52428800,
            "max_unverified_licenses": 0,
        },
        "performance": unavailable_performance(),
        "provenance": unavailable_provenance(),
    }


def _stage_status(asset: dict[str, Any], stage: str) -> str | None:
    for entry in asset.get("stages", []):
        if isinstance(entry, dict) and entry.get("stage") == stage:
            return entry.get("status")
    return None


def _has_cycle(assets: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for child in assets.get(node, []):
            if child in assets and visit(child):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in assets)


def mock_asset_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus asset-pipeline invariants."""
    errors = limited_schema_errors(document, read_schema("m11", "asset_pipeline.v1.schema.json"))
    assets = document.get("assets")
    policy = document.get("policy", {})
    budget = document.get("budget", {})
    if isinstance(assets, list) and all(isinstance(asset, dict) for asset in assets):
        ids = [asset.get("asset_id") for asset in assets]
        if len(ids) != len(set(ids)):
            errors.append("$.assets: duplicate asset_id")
        id_set = set(ids)
        dependency_map: dict[str, list[str]] = {}
        total_bytes = 0
        texture_bytes = 0
        unverified = 0
        for asset in assets:
            asset_id = asset.get("asset_id")
            stages = asset.get("stages", [])
            if isinstance(stages, list) and all(isinstance(stage, dict) for stage in stages):
                names = [stage.get("stage") for stage in stages]
                if len(names) != len(set(names)):
                    errors.append(f"$.assets[{asset_id}]: duplicate stage")
                for name in names:
                    if name not in STAGE_ORDER:
                        continue
                    if stage_status_pass(stages, name):
                        for earlier in STAGE_ORDER[: STAGE_ORDER.index(name)]:
                            if _stage_status(asset, earlier) != "pass":
                                errors.append(f"$.assets[{asset_id}]: stage {name} passes before {earlier}")
                                break
                if policy.get("require_cooked_artifact"):
                    cooked = next((stage for stage in stages if stage.get("stage") == "cooked"), None)
                    if not cooked or cooked.get("status") != "pass" or not cooked.get("artifact_sha256"):
                        errors.append(f"$.assets[{asset_id}]: cooked artifact is required")
            license_info = asset.get("license", {})
            if isinstance(license_info, dict):
                if license_info.get("verification") == "rejected":
                    errors.append(f"$.assets[{asset_id}]: rejected license")
                if policy.get("require_verified_license") and license_info.get("verification") != "verified":
                    errors.append(f"$.assets[{asset_id}]: verified license is required")
                if not policy.get("allow_unverified", True) and license_info.get("verification") == "unverified":
                    errors.append(f"$.assets[{asset_id}]: unverified license is not allowed")
                if license_info.get("verification") == "unverified":
                    unverified += 1
                allowed = policy.get("allowed_spdx_ids", [])
                if allowed and license_info.get("spdx_id") not in allowed:
                    errors.append(f"$.assets[{asset_id}]: spdx_id is not allowed")
                if policy.get("require_attribution") and not license_info.get("attribution"):
                    errors.append(f"$.assets[{asset_id}]: attribution is required")
            dependencies = asset.get("dependencies", [])
            if isinstance(dependencies, list):
                dependency_map[str(asset_id)] = [str(dep) for dep in dependencies]
                for dependency in dependencies:
                    if dependency == asset_id:
                        errors.append(f"$.assets[{asset_id}]: self dependency")
                    elif dependency not in id_set:
                        errors.append(f"$.assets[{asset_id}]: dangling dependency {dependency}")
            total_bytes += int(asset.get("cooked_bytes", 0))
            if asset.get("kind") == "texture":
                texture_bytes += int(asset.get("cooked_bytes", 0))
        if _has_cycle(dependency_map):
            errors.append("$.assets: dependency cycle")
        if isinstance(budget, dict):
            if len(assets) > int(budget.get("max_assets", 0)):
                errors.append("$.budget: asset count exceeds max_assets")
            if total_bytes > int(budget.get("max_total_bytes", 0)):
                errors.append("$.budget: total bytes exceed max_total_bytes")
            if texture_bytes > int(budget.get("max_texture_bytes", 0)):
                errors.append("$.budget: texture bytes exceed max_texture_bytes")
            if unverified > int(budget.get("max_unverified_licenses", 0)):
                errors.append("$.budget: unverified licenses exceed max_unverified_licenses")
    errors.extend(global_unavailable_errors(document))
    errors.extend(provenance_evidence_errors(document))
    return errors


def stage_status_pass(stages: list[dict[str, Any]], name: str) -> bool:
    return any(stage.get("stage") == name and stage.get("status") == "pass" for stage in stages)


class AssetPipelineContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m11", "asset_pipeline.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("asset_pipeline.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_asset_consumer(valid_observation()))

    def test_missing_assets_is_rejected(self) -> None:
        document = valid_observation()
        del document["assets"]
        self.assertIn(
            "$: missing required property assets",
            limited_schema_errors(document, read_schema("m11", "asset_pipeline.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(any("unexpected property fps" in error for error in mock_asset_consumer(document)))

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertEqual([], mock_asset_consumer(document))

        zero = valid_observation()
        zero["performance"]["measurement_status"] = "MEASURED"
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_asset_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider", "value": 0}
        self.assertTrue(mock_asset_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["draw_calls"] = {"status": "MEASURED", "value": 12}
        self.assertTrue(any("global UNAVAILABLE forbids MEASURED metric" in error for error in mock_asset_consumer(document)))

    def test_duplicate_asset_and_stage_are_rejected(self) -> None:
        duplicate = valid_observation()
        duplicate["assets"][1]["asset_id"] = "stone-albedo"
        self.assertTrue(any("duplicate asset_id" in error for error in mock_asset_consumer(duplicate)))

        duplicate_stage = valid_observation()
        duplicate_stage["assets"][0]["stages"][1]["stage"] = "raw"
        self.assertTrue(any("duplicate stage" in error for error in mock_asset_consumer(duplicate_stage)))

    def test_stage_order_is_enforced(self) -> None:
        document = valid_observation()
        document["assets"][1]["stages"] = [
            {"stage": "raw", "status": "pending"},
            {"stage": "imported", "status": "pass"},
        ]
        self.assertTrue(any("passes before" in error for error in mock_asset_consumer(document)))

    def test_cooked_artifact_is_required(self) -> None:
        document = valid_observation()
        document["assets"][1]["stages"][2].pop("artifact_sha256")
        self.assertTrue(any("cooked artifact is required" in error for error in mock_asset_consumer(document)))

    def test_license_policies(self) -> None:
        rejected = valid_observation()
        rejected["assets"][0]["license"]["verification"] = "rejected"
        self.assertTrue(any("rejected license" in error for error in mock_asset_consumer(rejected)))

        unverified = valid_observation()
        unverified["assets"][0]["license"]["verification"] = "unverified"
        self.assertTrue(any("verified license is required" in error for error in mock_asset_consumer(unverified)))

        not_allowed = valid_observation()
        not_allowed["assets"][0]["license"]["spdx_id"] = "GPL-3.0-only"
        self.assertTrue(any("spdx_id is not allowed" in error for error in mock_asset_consumer(not_allowed)))

        no_attribution = valid_observation()
        no_attribution["assets"][0]["license"]["attribution"] = ""
        self.assertTrue(any("attribution is required" in error for error in mock_asset_consumer(no_attribution)))

    def test_dependencies_are_validated(self) -> None:
        dangling = valid_observation()
        dangling["assets"][1]["dependencies"] = ["missing-asset"]
        self.assertTrue(any("dangling dependency" in error for error in mock_asset_consumer(dangling)))

        self_dependency = valid_observation()
        self_dependency["assets"][1]["dependencies"] = ["hero-mesh"]
        self.assertTrue(any("self dependency" in error for error in mock_asset_consumer(self_dependency)))

        cycle = valid_observation()
        cycle["assets"][0]["dependencies"] = ["hero-mesh"]
        self.assertTrue(any("dependency cycle" in error for error in mock_asset_consumer(cycle)))

    def test_budgets(self) -> None:
        count = valid_observation()
        count["budget"]["max_assets"] = 1
        self.assertTrue(any("asset count exceeds" in error for error in mock_asset_consumer(count)))

        total = valid_observation()
        total["budget"]["max_total_bytes"] = 1024
        self.assertTrue(any("total bytes exceed" in error for error in mock_asset_consumer(total)))

        texture = valid_observation()
        texture["budget"]["max_texture_bytes"] = 1024
        self.assertTrue(any("texture bytes exceed" in error for error in mock_asset_consumer(texture)))

        unverified = valid_observation()
        unverified["assets"][0]["license"]["verification"] = "unverified"
        unverified["policy"]["require_verified_license"] = False
        unverified["policy"]["allow_unverified"] = True
        unverified["budget"]["max_unverified_licenses"] = 0
        self.assertTrue(any("unverified licenses exceed" in error for error in mock_asset_consumer(unverified)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_asset_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m11-fixture"
        self.assertEqual([], mock_asset_consumer(document))

    def test_invalid_ids_and_digests_are_rejected(self) -> None:
        document = valid_observation()
        document["assets"][0]["asset_id"] = "Stone Albedo"
        self.assertTrue(mock_asset_consumer(document))

        document = valid_observation()
        document["assets"][0]["source_sha256"] = "A" * 64
        self.assertTrue(mock_asset_consumer(document))

        document = valid_observation()
        document["assets"][0]["kind"] = "shader"
        self.assertTrue(mock_asset_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["assets"][0]["cooked_bytes"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["assets"][0]["stages"][0]["status"] = "unknown"; perturbations.append(doc)
        doc = valid_observation(); doc["policy"]["allowed_spdx_ids"] = []; perturbations.append(doc)
        doc = valid_observation(); doc["budget"]["max_assets"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["provenance"]["base_sha"] = "A" * 40; perturbations.append(doc)
        doc = valid_observation(); doc["assets"][0]["import_settings"]["lod_count"] = 9; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_asset_consumer(document))


class M11OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m11")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m11")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m11")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m11")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

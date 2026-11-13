"""M04 PBR material contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import itertools
import unittest
from typing import Any

from _contract_support import (
    estimated_texture_bytes,
    global_unavailable_errors,
    provenance_evidence_errors,
    read_manifest,
    read_schema,
    unavailable_performance,
    unavailable_provenance,
)
from test_m01_schema import limited_schema_errors
from test_ownership_locks import normalize_path


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "material.v1",
        "observation_id": "m04-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "materials": [
            {
                "material_id": "stone-floor",
                "shader_id": "pbr-standard",
                "surface": {
                    "albedo_rgba": [0.42, 0.40, 0.36, 1.0],
                    "metallic": 0.0,
                    "roughness": 0.85,
                    "emission_rgba": [0.0, 0.0, 0.0, 1.0],
                    "emission_energy": 0.0,
                    "normal_strength": 1.0,
                    "occlusion_strength": 0.8,
                },
                "alpha_mode": "opaque",
                "cull_mode": "back",
                "quality_variant": "high",
                "textures": [
                    {"slot": "albedo", "uri": "res://textures/stone_albedo.png", "sha256": "a" * 64,
                     "width_px": 2048, "height_px": 2048, "mipmaps": True, "srgb": True},
                    {"slot": "normal", "uri": "res://textures/stone_normal.png", "sha256": "b" * 64,
                     "width_px": 2048, "height_px": 2048, "mipmaps": True, "srgb": False},
                    {"slot": "orm", "uri": "res://textures/stone_orm.png", "sha256": "c" * 64,
                     "width_px": 1024, "height_px": 1024, "mipmaps": True, "srgb": False},
                ],
            }
        ],
        "texture_budget": {
            "max_texture_count": 64,
            "max_texture_bytes": 268435456,
            "atlas_size": 4096,
            "orm_packed": True,
        },
        "performance": unavailable_performance(),
        "provenance": unavailable_provenance(),
    }


def mock_material_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus cross-field material invariants."""
    errors = limited_schema_errors(document, read_schema("m04", "material.v1.schema.json"))
    materials = document.get("materials")
    budget = document.get("texture_budget")
    if isinstance(materials, list) and all(isinstance(item, dict) for item in materials):
        ids = [material.get("material_id") for material in materials]
        if len(ids) != len(set(ids)):
            errors.append("$.materials: duplicate material_id")
        all_textures: list[dict[str, Any]] = []
        for material in materials:
            material_id = material.get("material_id")
            textures = material.get("textures", [])
            if not isinstance(textures, list):
                continue
            slots = [texture.get("slot") for texture in textures if isinstance(texture, dict)]
            if len(slots) != len(set(slots)):
                errors.append(f"$.materials[{material_id}]: duplicate texture slot")
            alpha_mode = material.get("alpha_mode")
            if alpha_mode == "mask" and "alpha_cutoff" not in material:
                errors.append(f"$.materials[{material_id}]: mask requires alpha_cutoff")
            if alpha_mode == "opaque" and "alpha_cutoff" in material:
                errors.append(f"$.materials[{material_id}]: opaque forbids alpha_cutoff")
            for texture in textures:
                if isinstance(texture, dict) and texture.get("slot") and texture.get("width_px"):
                    all_textures.append(texture)
        if isinstance(budget, dict):
            if len(all_textures) > int(budget.get("max_texture_count", 0)):
                errors.append("$.texture_budget: texture count exceeds max_texture_count")
            if estimated_texture_bytes(all_textures) > int(budget.get("max_texture_bytes", 0)):
                errors.append("$.texture_budget: estimated bytes exceed max_texture_bytes")
    errors.extend(global_unavailable_errors(document))
    errors.extend(provenance_evidence_errors(document))
    return errors


class MaterialContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m04", "material.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("material.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_material_consumer(valid_observation()))

    def test_missing_required_materials_is_rejected(self) -> None:
        document = valid_observation()
        del document["materials"]
        self.assertIn(
            "$: missing required property materials",
            limited_schema_errors(document, read_schema("m04", "material.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_material_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertEqual([], mock_material_consumer(document))

        zero = valid_observation()
        zero["performance"]["measurement_status"] = "MEASURED"
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_material_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 0,
        }
        self.assertTrue(mock_material_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["draw_calls"] = {"status": "MEASURED", "value": 12}
        self.assertTrue(
            any("global UNAVAILABLE forbids MEASURED metric" in error for error in mock_material_consumer(document))
        )

    def test_duplicate_material_and_slot_are_rejected(self) -> None:
        duplicate = valid_observation()
        duplicate["materials"].append(dict(duplicate["materials"][0]))
        self.assertTrue(any("duplicate material_id" in error for error in mock_material_consumer(duplicate)))

        same_slot = valid_observation()
        same_slot["materials"][0]["textures"][1]["slot"] = "albedo"
        self.assertTrue(any("duplicate texture slot" in error for error in mock_material_consumer(same_slot)))

    def test_alpha_mode_coherence(self) -> None:
        mask_without_cutoff = valid_observation()
        mask_without_cutoff["materials"][0]["alpha_mode"] = "mask"
        self.assertTrue(
            any("mask requires alpha_cutoff" in error for error in mock_material_consumer(mask_without_cutoff))
        )

        mask_ok = valid_observation()
        mask_ok["materials"][0]["alpha_mode"] = "mask"
        mask_ok["materials"][0]["alpha_cutoff"] = 0.5
        self.assertEqual([], mock_material_consumer(mask_ok))

        opaque_with_cutoff = valid_observation()
        opaque_with_cutoff["materials"][0]["alpha_cutoff"] = 0.5
        self.assertTrue(
            any("opaque forbids alpha_cutoff" in error for error in mock_material_consumer(opaque_with_cutoff))
        )

    def test_texture_budget_invariants(self) -> None:
        count = valid_observation()
        count["texture_budget"]["max_texture_count"] = 1
        self.assertTrue(
            any("texture count exceeds" in error for error in mock_material_consumer(count))
        )

        size = valid_observation()
        size["texture_budget"]["max_texture_bytes"] = 1024
        self.assertTrue(
            any("estimated bytes exceed" in error for error in mock_material_consumer(size))
        )

        self.assertGreater(estimated_texture_bytes(valid_observation()["materials"][0]["textures"]), 0)

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_material_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m04-fixture"
        self.assertEqual([], mock_material_consumer(document))

    def test_invalid_sha_and_material_id_are_rejected(self) -> None:
        document = valid_observation()
        document["materials"][0]["textures"][0]["sha256"] = "A" * 64
        self.assertTrue(mock_material_consumer(document))

        document = valid_observation()
        document["materials"][0]["material_id"] = "Stone Floor"
        self.assertTrue(mock_material_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["materials"][0]["surface"]["metallic"] = 1.5; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["surface"]["roughness"] = -0.1; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["surface"]["albedo_rgba"] = [0.0, 0.0, 0.0]; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["alpha_mode"] = "cutout"; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["cull_mode"] = "both"; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["quality_variant"] = "ultra"; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["textures"][0]["width_px"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["materials"][0]["textures"][0]["slot"] = "roughness"; perturbations.append(doc)
        doc = valid_observation(); doc["texture_budget"]["atlas_size"] = 128; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_material_consumer(document))


class M04OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m04")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])
        self.assertTrue(manifest["rules"]["single_writer_per_path"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m04")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m04")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m04")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

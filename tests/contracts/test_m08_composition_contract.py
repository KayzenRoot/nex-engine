"""M08 2.5D composition contract tests using the repository's limited stdlib checker."""
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


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "composition.v1",
        "observation_id": "m08-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "base_3d_plan": {
            "plan_schema": "depth_composition.plan.v1",
            "plan_sha256": "a" * 64,
            "opaque_count": 12,
            "alpha_count": 4,
            "overlay_count": 2,
            "z_fight_risks": 1,
            "alpha_over_critical": 0,
            "overlay_gameplay_conflicts": 0,
        },
        "layer_stack": [
            {"layer_id": "sky", "role": "background", "parallax": 0.2, "blend_mode": "normal",
             "alpha": 1.0, "gameplay_critical": False, "may_cover_gameplay": False},
            {"layer_id": "world", "role": "gameplay", "parallax": 1.0, "blend_mode": "normal",
             "alpha": 1.0, "gameplay_critical": True, "may_cover_gameplay": False},
            {"layer_id": "dust", "role": "foreground", "parallax": 1.4, "blend_mode": "add",
             "alpha": 0.35, "gameplay_critical": False, "may_cover_gameplay": True},
            {"layer_id": "hud", "role": "hud", "parallax": 0.0, "blend_mode": "normal",
             "alpha": 1.0, "gameplay_critical": False, "may_cover_gameplay": False},
        ],
        "depth_policy": "hybrid",
        "alpha_policy": {"sort": "back_to_front", "critical_guard": True, "max_alpha_over_gameplay": 0.5},
        "overlay_safety": {"hud_layer_id": "hud", "may_cover_gameplay": False, "conflict_policy": "report"},
        "critical_entities": [
            {"entity_id": "player", "role": "player", "must_remain_visible": True},
            {"entity_id": "threat-01", "role": "threat", "must_remain_visible": True},
        ],
        "performance": unavailable_performance(),
        "provenance": unavailable_provenance(),
    }


def mock_composition_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus 2.5D composition invariants."""
    errors = limited_schema_errors(document, read_schema("m08", "composition.v1.schema.json"))
    layers = document.get("layer_stack")
    if isinstance(layers, list) and all(isinstance(layer, dict) for layer in layers):
        layer_ids = [layer.get("layer_id") for layer in layers]
        if len(layer_ids) != len(set(layer_ids)):
            errors.append("$.layer_stack: duplicate layer_id")
        hud_layers = [layer for layer in layers if layer.get("role") == "hud"]
        if not hud_layers:
            errors.append("$.layer_stack: at least one hud layer is required")
        for layer in hud_layers:
            if "depth_override_m" in layer:
                errors.append(f"$.layer_stack[{layer.get('layer_id')}]: hud forbids depth_override_m")
        overlay = document.get("overlay_safety")
        if isinstance(overlay, dict):
            hud_id = overlay.get("hud_layer_id")
            referenced = [layer for layer in layers if layer.get("layer_id") == hud_id]
            if not referenced or referenced[0].get("role") != "hud":
                errors.append("$.overlay_safety.hud_layer_id: must reference a hud layer")
            if overlay.get("may_cover_gameplay") and document.get("critical_entities"):
                if overlay.get("conflict_policy") != "report":
                    errors.append("$.overlay_safety.conflict_policy: must be report when overlays may cover gameplay")
        if document.get("depth_policy") == "inherit_3d":
            for layer in layers:
                if "depth_override_m" in layer:
                    errors.append(f"$.layer_stack[{layer.get('layer_id')}]: inherit_3d forbids depth_override_m")
    entities = document.get("critical_entities")
    if isinstance(entities, list) and all(isinstance(entity, dict) for entity in entities):
        entity_ids = [entity.get("entity_id") for entity in entities]
        if len(entity_ids) != len(set(entity_ids)):
            errors.append("$.critical_entities: duplicate entity_id")
        must_remain = any(entity.get("must_remain_visible") for entity in entities)
        alpha_policy = document.get("alpha_policy")
        if must_remain and isinstance(alpha_policy, dict) and not alpha_policy.get("critical_guard"):
            errors.append("$.alpha_policy.critical_guard: required when a critical entity must remain visible")
    plan = document.get("base_3d_plan")
    if isinstance(plan, dict):
        counts = ("opaque_count", "alpha_count", "overlay_count", "z_fight_risks", "alpha_over_critical", "overlay_gameplay_conflicts")
        if plan.get("plan_schema") == "none":
            for key in counts:
                if int(plan.get(key, 0)) != 0:
                    errors.append(f"$.base_3d_plan.{key}: must be zero when plan_schema is none")
        elif not plan.get("plan_sha256"):
            errors.append("$.base_3d_plan.plan_sha256: required for a real 3D plan")
    errors.extend(global_unavailable_errors(document))
    errors.extend(provenance_evidence_errors(document))
    return errors


class CompositionContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m08", "composition.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("composition.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_composition_consumer(valid_observation()))

    def test_missing_layer_stack_is_rejected(self) -> None:
        document = valid_observation()
        del document["layer_stack"]
        self.assertIn(
            "$: missing required property layer_stack",
            limited_schema_errors(document, read_schema("m08", "composition.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_composition_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertEqual([], mock_composition_consumer(document))

        zero = valid_observation()
        zero["performance"]["measurement_status"] = "MEASURED"
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_composition_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 0,
        }
        self.assertTrue(mock_composition_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["draw_calls"] = {"status": "MEASURED", "value": 12}
        self.assertTrue(
            any("global UNAVAILABLE forbids MEASURED metric" in error for error in mock_composition_consumer(document))
        )

    def test_duplicate_layer_and_entity_ids_are_rejected(self) -> None:
        duplicate_layer = valid_observation()
        duplicate_layer["layer_stack"][1]["layer_id"] = "sky"
        self.assertTrue(any("duplicate layer_id" in error for error in mock_composition_consumer(duplicate_layer)))

        duplicate_entity = valid_observation()
        duplicate_entity["critical_entities"][1]["entity_id"] = "player"
        self.assertTrue(any("duplicate entity_id" in error for error in mock_composition_consumer(duplicate_entity)))

    def test_hud_reference_and_depth_override(self) -> None:
        missing = valid_observation()
        missing["overlay_safety"]["hud_layer_id"] = "missing"
        self.assertTrue(any("must reference a hud layer" in error for error in mock_composition_consumer(missing)))

        wrong_role = valid_observation()
        wrong_role["overlay_safety"]["hud_layer_id"] = "world"
        self.assertTrue(any("must reference a hud layer" in error for error in mock_composition_consumer(wrong_role)))

        override = valid_observation()
        override["layer_stack"][3]["depth_override_m"] = 1.0
        self.assertTrue(any("hud forbids depth_override_m" in error for error in mock_composition_consumer(override)))

    def test_inherit_3d_forbids_layer_overrides(self) -> None:
        document = valid_observation()
        document["depth_policy"] = "inherit_3d"
        document["layer_stack"][1]["depth_override_m"] = 2.0
        self.assertTrue(any("inherit_3d forbids" in error for error in mock_composition_consumer(document)))

        hybrid = valid_observation()
        hybrid["layer_stack"][1]["depth_override_m"] = 2.0
        self.assertEqual([], mock_composition_consumer(hybrid))

    def test_critical_visibility_requires_guard(self) -> None:
        document = valid_observation()
        document["alpha_policy"]["critical_guard"] = False
        self.assertTrue(any("critical_guard" in error for error in mock_composition_consumer(document)))

        no_visible = valid_observation()
        no_visible["alpha_policy"]["critical_guard"] = False
        for entity in no_visible["critical_entities"]:
            entity["must_remain_visible"] = False
        self.assertEqual([], mock_composition_consumer(no_visible))

    def test_overlay_safety_requires_report_when_covering(self) -> None:
        document = valid_observation()
        document["overlay_safety"]["may_cover_gameplay"] = True
        document["overlay_safety"]["conflict_policy"] = "block"
        self.assertTrue(any("must be report" in error for error in mock_composition_consumer(document)))

        document["overlay_safety"]["conflict_policy"] = "report"
        self.assertEqual([], mock_composition_consumer(document))

    def test_base_plan_none_requires_zero_counts(self) -> None:
        document = valid_observation()
        document["base_3d_plan"]["plan_schema"] = "none"
        document["base_3d_plan"]["opaque_count"] = 1
        self.assertTrue(any("must be zero" in error for error in mock_composition_consumer(document)))

        clean = valid_observation()
        clean["base_3d_plan"] = {
            "plan_schema": "none",
            "opaque_count": 0,
            "alpha_count": 0,
            "overlay_count": 0,
            "z_fight_risks": 0,
            "alpha_over_critical": 0,
            "overlay_gameplay_conflicts": 0,
        }
        self.assertEqual([], mock_composition_consumer(clean))

    def test_real_plan_requires_digest(self) -> None:
        document = valid_observation()
        del document["base_3d_plan"]["plan_sha256"]
        self.assertTrue(any("plan_sha256" in error for error in mock_composition_consumer(document)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_composition_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m08-fixture"
        self.assertEqual([], mock_composition_consumer(document))

    def test_invalid_ids_roles_and_values_are_rejected(self) -> None:
        document = valid_observation()
        document["layer_stack"][0]["layer_id"] = "Sky Layer"
        self.assertTrue(mock_composition_consumer(document))

        document = valid_observation()
        document["layer_stack"][0]["role"] = "midground"
        self.assertTrue(mock_composition_consumer(document))

        document = valid_observation()
        document["layer_stack"][0]["parallax"] = 5.0
        self.assertTrue(mock_composition_consumer(document))

        document = valid_observation()
        document["alpha_policy"]["max_alpha_over_gameplay"] = 1.5
        self.assertTrue(mock_composition_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["depth_policy"] = "screen_space"; perturbations.append(doc)
        doc = valid_observation(); doc["alpha_policy"]["sort"] = "front_to_back"; perturbations.append(doc)
        doc = valid_observation(); doc["layer_stack"][0]["blend_mode"] = "overlay"; perturbations.append(doc)
        doc = valid_observation(); doc["layer_stack"][0]["alpha"] = -0.1; perturbations.append(doc)
        doc = valid_observation(); doc["base_3d_plan"]["plan_sha256"] = "A" * 64; perturbations.append(doc)
        doc = valid_observation(); doc["critical_entities"][0]["role"] = "npc"; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["provenance"]["base_sha"] = "A" * 40; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_composition_consumer(document))


class M08OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m08")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m08")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m08")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m08")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

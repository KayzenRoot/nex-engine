"""M03 lighting contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import itertools
import unittest
from pathlib import Path
from typing import Any

from test_m01_schema import limited_schema_errors, strict_json_loads
from test_m02_render_contract import _resolve_refs
from test_ownership_locks import normalize_path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "contracts" / "m03"


def read_schema(filename: str) -> dict[str, Any]:
    raw = strict_json_loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
    return _resolve_refs(raw, raw.get("$defs", {}))


def read_manifest() -> dict[str, Any]:
    return strict_json_loads((SCHEMA_DIR / "ownership.v1.json").read_text(encoding="utf-8"))


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "lighting.v1",
        "observation_id": "m03-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "environment": {
            "ambient_source": "color",
            "ambient_color_rgba": [0.05, 0.07, 0.1, 1.0],
            "ambient_energy": 0.6,
            "tonemap": "filmic",
            "glow": True,
            "fog": {"enabled": False, "density": 0.0, "light_energy": 0.0},
            "gi": {"mode": "sdfgi", "energy": 1.0},
        },
        "lights": [
            {
                "light_id": "moon-key",
                "light_type": "directional",
                "color_rgba": [0.6, 0.7, 1.0, 1.0],
                "energy": 1.2,
                "shadow_enabled": True,
                "shadow_bias": 0.05,
                "shadow_softness": 0.2,
                "cull_mask": 1,
                "cascades": 2,
            },
            {
                "light_id": "brazier-fill",
                "light_type": "omni",
                "color_rgba": [1.0, 0.55, 0.2, 1.0],
                "energy": 3.0,
                "shadow_enabled": True,
                "shadow_bias": 0.1,
                "shadow_softness": 0.4,
                "cull_mask": 3,
                "range_m": 8.0,
            },
            {
                "light_id": "gate-spot",
                "light_type": "spot",
                "color_rgba": [0.4, 0.9, 0.7, 1.0],
                "energy": 2.0,
                "shadow_enabled": False,
                "shadow_bias": 0.05,
                "shadow_softness": 0.1,
                "cull_mask": 1,
                "range_m": 24.0,
                "spot_angle_degrees": 35.0,
            },
        ],
        "shadow_budget": {
            "max_shadowed_lights": 4,
            "directional_cascades": 4,
            "atlas_size": 4096,
        },
        "performance": {
            "measurement_status": "UNAVAILABLE",
            "frame_interval": {
                "status": "UNAVAILABLE",
                "provider": "SceneTree._process(delta)",
                "unavailable_reason": "contract fixture has no runtime",
            },
            "gpu_render_time": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
            "cpu_render_time": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
            "draw_calls": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
            "renderer_allocation_bytes": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
        },
        "provenance": {
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "godot_version": "4.7.2-stable",
            "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
            "capture_mode": "windowed",
            "measurement_status": "UNAVAILABLE",
        },
    }


def mock_lighting_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus cross-field lighting invariants."""
    errors = limited_schema_errors(document, read_schema("lighting.v1.schema.json"))
    lights = document.get("lights")
    budget = document.get("shadow_budget")
    if isinstance(lights, list) and all(isinstance(light, dict) for light in lights):
        light_ids = [light.get("light_id") for light in lights]
        if len(light_ids) != len(set(light_ids)):
            errors.append("$.lights: duplicate light_id")
        for light in lights:
            light_type = light.get("light_type")
            if light_type == "directional" and (
                "range_m" in light or "spot_angle_degrees" in light
            ):
                errors.append(
                    f"$.lights[{light.get('light_id')}]: directional light forbids range/spot angle"
                )
            if light_type == "omni" and "spot_angle_degrees" in light:
                errors.append(
                    f"$.lights[{light.get('light_id')}]: omni light forbids spot angle"
                )
            if light.get("shadow_enabled") and light.get("energy") == 0:
                errors.append(
                    f"$.lights[{light.get('light_id')}]: shadow caster requires energy > 0"
                )
        if isinstance(budget, dict):
            shadowed = sum(1 for light in lights if light.get("shadow_enabled"))
            max_shadowed = budget.get("max_shadowed_lights")
            if isinstance(max_shadowed, int) and shadowed > max_shadowed:
                errors.append("$.shadow_budget: shadowed lights exceed max_shadowed_lights")
            directional_cascades = budget.get("directional_cascades")
            for light in lights:
                cascades = light.get("cascades")
                if (
                    light.get("light_type") == "directional"
                    and isinstance(cascades, int)
                    and isinstance(directional_cascades, int)
                    and cascades > directional_cascades
                ):
                    errors.append(
                        f"$.lights[{light.get('light_id')}]: cascades exceed directional budget"
                    )
    performance = document.get("performance")
    if isinstance(performance, dict) and performance.get("measurement_status") == "UNAVAILABLE":
        for key in (
            "gpu_render_time",
            "cpu_render_time",
            "draw_calls",
            "renderer_allocation_bytes",
        ):
            metric = performance.get(key)
            if isinstance(metric, dict) and metric.get("status") == "MEASURED":
                errors.append(f"$.performance.{key}: global UNAVAILABLE forbids MEASURED metric")
    provenance = document.get("provenance")
    if isinstance(provenance, dict):
        if provenance.get("measurement_status") == "MEASURED" and not provenance.get("evidence_uri"):
            errors.append("$.provenance.evidence_uri: required when provenance is MEASURED")
    return errors


class LightingContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("lighting.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("lighting.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_lighting_consumer(valid_observation()))

    def test_missing_required_environment_is_rejected(self) -> None:
        document = valid_observation()
        del document["environment"]
        self.assertIn(
            "$: missing required property environment",
            limited_schema_errors(document, read_schema("lighting.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_lighting_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no GPU provider",
        }
        self.assertEqual([], mock_lighting_consumer(document))

        zero = valid_observation()
        zero["performance"]["measurement_status"] = "MEASURED"
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_lighting_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 0,
        }
        self.assertTrue(mock_lighting_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["draw_calls"] = {"status": "MEASURED", "value": 12}
        self.assertTrue(
            any(
                "global UNAVAILABLE forbids MEASURED metric" in error
                for error in mock_lighting_consumer(document)
            )
        )

    def test_duplicate_light_id_is_rejected(self) -> None:
        document = valid_observation()
        document["lights"][1]["light_id"] = document["lights"][0]["light_id"]
        self.assertTrue(any("duplicate light_id" in error for error in mock_lighting_consumer(document)))

    def test_light_type_field_coherence(self) -> None:
        directional_range = valid_observation()
        directional_range["lights"][0]["range_m"] = 12.0
        self.assertTrue(
            any(
                "directional light forbids range/spot angle" in error
                for error in mock_lighting_consumer(directional_range)
            )
        )

        directional_angle = valid_observation()
        directional_angle["lights"][0]["spot_angle_degrees"] = 20.0
        self.assertTrue(
            any(
                "directional light forbids range/spot angle" in error
                for error in mock_lighting_consumer(directional_angle)
            )
        )

        omni_angle = valid_observation()
        omni_angle["lights"][1]["spot_angle_degrees"] = 20.0
        self.assertTrue(
            any("omni light forbids spot angle" in error for error in mock_lighting_consumer(omni_angle))
        )

        spot_ok = valid_observation()
        spot_ok["lights"][2]["shadow_enabled"] = True
        self.assertEqual([], mock_lighting_consumer(spot_ok))

    def test_shadow_budget_invariants(self) -> None:
        over_budget = valid_observation()
        over_budget["shadow_budget"]["max_shadowed_lights"] = 1
        self.assertTrue(
            any(
                "shadowed lights exceed max_shadowed_lights" in error
                for error in mock_lighting_consumer(over_budget)
            )
        )

        too_many_cascades = valid_observation()
        too_many_cascades["lights"][0]["cascades"] = 3
        too_many_cascades["shadow_budget"]["directional_cascades"] = 2
        self.assertTrue(
            any(
                "cascades exceed directional budget" in error
                for error in mock_lighting_consumer(too_many_cascades)
            )
        )

        dark_caster = valid_observation()
        dark_caster["lights"][1]["energy"] = 0
        self.assertTrue(
            any("shadow caster requires energy > 0" in error for error in mock_lighting_consumer(dark_caster))
        )

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        document["performance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_lighting_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m03-fixture"
        self.assertEqual([], mock_lighting_consumer(document))

    def test_invalid_sha_and_observation_id_are_rejected(self) -> None:
        document = valid_observation()
        document["provenance"]["base_sha"] = "A" * 40
        self.assertTrue(mock_lighting_consumer(document))

        document = valid_observation()
        document["observation_id"] = "M03 Fixture"
        self.assertTrue(mock_lighting_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["environment"]["tonemap"] = "nearest"; perturbations.append(doc)
        doc = valid_observation(); doc["environment"]["glow"] = "yes"; perturbations.append(doc)
        doc = valid_observation(); doc["lights"][0]["light_type"] = "area"; perturbations.append(doc)
        doc = valid_observation(); doc["lights"][1]["range_m"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["lights"][2]["spot_angle_degrees"] = 91.0; perturbations.append(doc)
        doc = valid_observation(); doc["lights"][0]["cull_mask"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["lights"][0]["cascades"] = 5; perturbations.append(doc)
        doc = valid_observation(); doc["shadow_budget"]["atlas_size"] = 128; perturbations.append(doc)
        doc = valid_observation(); doc["shadow_budget"]["max_shadowed_lights"] = 17; perturbations.append(doc)
        doc = valid_observation(); doc["environment"]["fog"]["density"] = 1.5; perturbations.append(doc)
        doc = valid_observation(); doc["environment"]["gi"]["mode"] = "baked"; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["frame_interval"]["samples_ms"] = [0]; perturbations.append(doc)
        doc = valid_observation(); doc["captured_at_utc"] = "2026-11-13 12:00:00"; perturbations.append(doc)
        doc = valid_observation(); doc["lights"] = []; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_lighting_consumer(document))


class M03OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest()
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])
        self.assertTrue(manifest["rules"]["single_writer_per_path"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest()["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertFalse(entry["path"].startswith(("/", "\\")))
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest()["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        manifest = read_manifest()
        owners = {entry["owner"] for entry in manifest["paths"]}
        self.assertIn("integration-steward", owners)
        for entry in manifest["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

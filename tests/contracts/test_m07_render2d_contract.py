"""M07 advanced 2D pipeline contract tests using the limited stdlib checker."""
from __future__ import annotations

import itertools
import re
import unittest
from pathlib import Path
from typing import Any

from test_m01_schema import limited_schema_errors, strict_json_loads
from test_m02_render_contract import _resolve_refs
from test_ownership_locks import normalize_path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "contracts" / "m07"


def read_schema(filename: str) -> dict[str, Any]:
    raw = strict_json_loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
    return _resolve_refs(raw, raw.get("$defs", {}))


def read_manifest() -> dict[str, Any]:
    return strict_json_loads((SCHEMA_DIR / "ownership.v1.json").read_text(encoding="utf-8"))


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "render2d.v1",
        "frame_id": "m07-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "viewport": {"width_px": 1280, "height_px": 720, "unit": "px"},
        "render_settings": {
            "renderer_id": "godot.forward_plus",
            "driver_id": "vulkan",
            "vsync_mode": 1,
            "max_fps": 0,
            "pixel_snap": True,
            "default_filter": "nearest",
        },
        "canvas": {
            "layers": [
                {
                    "layer_id": "background",
                    "z_index": -10,
                    "blend_mode": "mix",
                    "material_id": "bg-material",
                    "transform": {"position_px": [0.0, 0.0], "scale": [1.0, 1.0], "rotation_deg": 0.0},
                    "visible": True,
                },
                {
                    "layer_id": "spell-glow",
                    "z_index": 20,
                    "blend_mode": "add",
                    "material_id": "glow-material",
                    "transform": {"position_px": [640.0, 360.0], "scale": [2.0, 2.0], "rotation_deg": -15.0},
                    "visible": True,
                },
            ],
            "materials": [
                {"material_id": "bg-material", "shader_id": "canvas-texture", "lighting_mode": "unshaded"},
                {"material_id": "glow-material", "shader_id": "canvas-glow", "lighting_mode": "canvas_light"},
            ],
            "lights": [
                {
                    "light_id": "spell-light",
                    "light_type": "point",
                    "color_rgba": [0.4, 0.7, 1.0, 1.0],
                    "energy": 1.4,
                    "texture_scale": 2.0,
                }
            ],
            "particles": [
                {"emitter_id": "sparks", "amount": 64, "lifetime_s": 1.2, "emitting": True}
            ],
            "batching": {"max_draw_calls": 128, "batch_groups": 24, "state_changes": 12},
        },
        "performance": {
            "measurement_status": "MEASURED",
            "frame_interval": {
                "status": "MEASURED",
                "provider": "SceneTree._process(delta)",
                "samples_ms": [16.6, 16.7, 16.8],
            },
            "gpu_render_time": {"status": "MEASURED", "value": 1.2},
            "cpu_render_time": {"status": "MEASURED", "value": 0.9},
            "draw_calls": {"status": "MEASURED", "value": 96},
            "objects_rendered": {"status": "MEASURED", "value": 420},
            "renderer_allocation_bytes": {"status": "MEASURED", "value": 524288},
        },
        "provenance": {
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "godot_version": "4.7.2-stable",
            "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
            "capture_mode": "windowed",
            "measurement_status": "MEASURED",
            "evidence_uri": "evidence://m07-fixture",
        },
    }


def mock_render2d_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus cross-field invariants."""
    errors = limited_schema_errors(document, read_schema("render2d.v1.schema.json"))
    canvas = document.get("canvas")
    if isinstance(canvas, dict):
        layers = canvas.get("layers")
        materials = canvas.get("materials")
        if isinstance(layers, list) and layers and all(isinstance(item, dict) for item in layers):
            layer_ids = [layer.get("layer_id") for layer in layers]
            if len(layer_ids) != len(set(layer_ids)):
                errors.append("$.canvas.layers: duplicate layer_id")
            z_indices = [layer.get("z_index") for layer in layers]
            if len(z_indices) != len(set(z_indices)):
                errors.append("$.canvas.layers: duplicate z_index")
            if isinstance(materials, list) and all(isinstance(item, dict) for item in materials):
                material_ids = {material.get("material_id") for material in materials}
                for layer in layers:
                    if layer.get("material_id") not in material_ids:
                        errors.append(
                            f"$.canvas.layers[{layer.get('layer_id')}]: dangling material_id"
                        )
        particles = canvas.get("particles")
        if isinstance(particles, list):
            for particle in particles:
                if not isinstance(particle, dict):
                    continue
                if particle.get("emitting") and int(particle.get("amount", 0)) < 1:
                    errors.append("$.canvas.particles: emitting emitter requires amount >= 1")
        batching = canvas.get("batching")
        if isinstance(batching, dict):
            max_draw_calls = batching.get("max_draw_calls")
            batch_groups = batching.get("batch_groups")
            if (
                isinstance(max_draw_calls, int)
                and isinstance(batch_groups, int)
                and batch_groups > max_draw_calls
            ):
                errors.append("$.canvas.batching: batch_groups must not exceed max_draw_calls")
    performance = document.get("performance")
    if isinstance(performance, dict) and performance.get("measurement_status") == "UNAVAILABLE":
        for key in (
            "gpu_render_time",
            "cpu_render_time",
            "draw_calls",
            "objects_rendered",
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


class Render2DContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("render2d.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("render2d.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_render2d_consumer(valid_observation()))

    def test_missing_required_canvas_is_rejected(self) -> None:
        document = valid_observation()
        del document["canvas"]
        self.assertIn(
            "$: missing required property canvas",
            limited_schema_errors(document, read_schema("render2d.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_render2d_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
        }
        self.assertEqual([], mock_render2d_consumer(document))

        zero = valid_observation()
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_render2d_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 0,
        }
        self.assertTrue(mock_render2d_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["measurement_status"] = "UNAVAILABLE"
        self.assertTrue(
            any(
                "global UNAVAILABLE forbids MEASURED metric" in error
                for error in mock_render2d_consumer(document)
            )
        )

    def test_duplicate_layer_and_z_index_are_rejected(self) -> None:
        duplicate = valid_observation()
        duplicate["canvas"]["layers"][1]["layer_id"] = duplicate["canvas"]["layers"][0]["layer_id"]
        self.assertTrue(any("duplicate layer_id" in error for error in mock_render2d_consumer(duplicate)))

        same_z = valid_observation()
        same_z["canvas"]["layers"][1]["z_index"] = same_z["canvas"]["layers"][0]["z_index"]
        self.assertTrue(any("duplicate z_index" in error for error in mock_render2d_consumer(same_z)))

    def test_dangling_material_is_rejected(self) -> None:
        document = valid_observation()
        document["canvas"]["layers"][0]["material_id"] = "missing-material"
        self.assertTrue(any("dangling material_id" in error for error in mock_render2d_consumer(document)))

    def test_particle_and_batching_invariants(self) -> None:
        document = valid_observation()
        document["canvas"]["particles"][0]["amount"] = 0
        self.assertTrue(any("amount >= 1" in error for error in mock_render2d_consumer(document)))

        document = valid_observation()
        document["canvas"]["batching"]["batch_groups"] = 200
        self.assertTrue(any("must not exceed max_draw_calls" in error for error in mock_render2d_consumer(document)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        del document["provenance"]["evidence_uri"]
        self.assertTrue(any("evidence_uri" in error for error in mock_render2d_consumer(document)))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["render_settings"]["vsync_mode"] = 3; perturbations.append(doc)
        doc = valid_observation(); doc["canvas"]["layers"][0]["blend_mode"] = "screen"; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["viewport"]["width_px"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["canvas"]["layers"][0]["transform"]["scale"] = [0.0, 1.0]; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_render2d_consumer(document))


class M07OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest()
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest()["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest()["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )


if __name__ == "__main__":
    unittest.main()

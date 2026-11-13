"""M02 render core contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import copy
import re
import unittest
from pathlib import Path
from typing import Any

from test_m01_schema import limited_schema_errors, strict_json_loads
from test_ownership_locks import normalize_path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "contracts" / "m02"


def _resolve_refs(node: Any, definitions: dict[str, Any], seen: tuple[str, ...] = ()) -> Any:
    """Expand local $ref nodes so the limited checker can evaluate the schema."""
    if isinstance(node, dict):
        if "$ref" in node:
            name = str(node["$ref"]).rsplit("/", 1)[-1]
            if name not in definitions or name in seen:
                raise ValueError(f"unresolvable schema reference: {node['$ref']}")
            return _resolve_refs(definitions[name], definitions, seen + (name,))
        return {key: _resolve_refs(value, definitions, seen) for key, value in node.items()}
    if isinstance(node, list):
        return [_resolve_refs(value, definitions, seen) for value in node]
    return node


def read_schema(filename: str) -> dict[str, Any]:
    raw = strict_json_loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
    return _resolve_refs(raw, raw.get("$defs", {}))


def read_manifest() -> dict[str, Any]:
    return strict_json_loads((SCHEMA_DIR / "ownership.v1.json").read_text(encoding="utf-8"))


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "render_core.v1",
        "frame_id": "m02-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "camera": {
            "preset_id": "isometric-orbit",
            "projection": "isometric_perspective",
            "position_m": [0.0, 12.0, 12.0],
            "target_m": [0.0, 0.0, 0.0],
            "view_rotation_degrees": {"yaw_deg": 45.0, "pitch_deg": -35.264},
            "vertical_fov_degrees": 40.0,
            "near_clip_m": 0.1,
            "far_clip_m": 500.0,
            "stability": {"snap_to_pixel": True, "anchor_offset_px": [0, 0]},
            "viewport": {"width_px": 1280, "height_px": 720, "unit": "px"},
        },
        "render_settings": {
            "renderer_id": "godot.forward_plus",
            "driver_id": "vulkan",
            "vsync_mode": 1,
            "max_fps": 0,
            "resolution_scale": 1.0,
            "msaa": "4x",
            "shadow_quality": "high",
            "directional_shadow_cascades": 4,
            "glow_enabled": True,
            "ssao_enabled": True,
            "sdfgi_enabled": False,
        },
        "performance": {
            "measurement_status": "MEASURED",
            "frame_interval": {
                "status": "MEASURED",
                "provider": "SceneTree._process(delta)",
                "samples_ms": [16.6, 16.7, 16.8],
            },
            "gpu_render_time": {"status": "MEASURED", "value": 4.2},
            "cpu_render_time": {"status": "MEASURED", "value": 2.1},
            "draw_calls": {"status": "MEASURED", "value": 240},
            "objects_rendered": {"status": "MEASURED", "value": 1200},
            "renderer_allocation_bytes": {"status": "MEASURED", "value": 1048576},
        },
        "provenance": {
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "godot_version": "4.7.2-stable",
            "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
            "capture_mode": "windowed",
            "measurement_status": "MEASURED",
            "evidence_uri": "evidence://m02-fixture",
        },
    }


def mock_render_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus cross-field invariants."""
    errors = limited_schema_errors(document, read_schema("render_core.v1.schema.json"))
    camera = document.get("camera")
    if isinstance(camera, dict):
        near = camera.get("near_clip_m")
        far = camera.get("far_clip_m")
        if (
            isinstance(near, (int, float))
            and not isinstance(near, bool)
            and isinstance(far, (int, float))
            and not isinstance(far, bool)
            and far <= near
        ):
            errors.append("$.camera.far_clip_m: must exceed near_clip_m")
        projection = camera.get("projection")
        if projection == "isometric_orthographic" and "ortho_size_m" not in camera:
            errors.append("$.camera.ortho_size_m: required for isometric_orthographic")
        if projection == "isometric_perspective" and "vertical_fov_degrees" not in camera:
            errors.append("$.camera.vertical_fov_degrees: required for isometric_perspective")
    performance = document.get("performance")
    if isinstance(performance, dict):
        if performance.get("measurement_status") == "UNAVAILABLE":
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


class RenderCoreContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("render_core.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))  # refs are expanded by read_schema
        self.assertEqual("render_core.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes_and_consumer_invariants_hold(self) -> None:
        self.assertEqual([], mock_render_consumer(valid_observation()))

    def test_missing_required_top_level_field_is_rejected(self) -> None:
        document = valid_observation()
        del document["camera"]
        self.assertIn(
            "$: missing required property camera",
            limited_schema_errors(document, read_schema("render_core.v1.schema.json")),
        )

    def test_unexpected_properties_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_render_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertEqual([], mock_render_consumer(document))

        zero = valid_observation()
        zero["performance"]["gpu_render_time"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_render_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["gpu_render_time"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 4.2,
        }
        self.assertTrue(mock_render_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["measurement_status"] = "UNAVAILABLE"
        errors = mock_render_consumer(document)
        self.assertTrue(any("global UNAVAILABLE forbids MEASURED metric" in error for error in errors))

    def test_camera_invariants(self) -> None:
        inverted = valid_observation()
        inverted["camera"]["far_clip_m"] = 0.05
        self.assertTrue(any("must exceed near_clip_m" in error for error in mock_render_consumer(inverted)))

        ortho_without_size = valid_observation()
        ortho_without_size["camera"]["projection"] = "isometric_orthographic"
        del ortho_without_size["camera"]["vertical_fov_degrees"]
        self.assertTrue(
            any("required for isometric_orthographic" in error for error in mock_render_consumer(ortho_without_size))
        )

        perspective_without_fov = valid_observation()
        del perspective_without_fov["camera"]["vertical_fov_degrees"]
        self.assertTrue(
            any("required for isometric_perspective" in error for error in mock_render_consumer(perspective_without_fov))
        )

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        del document["provenance"]["evidence_uri"]
        self.assertTrue(any("evidence_uri" in error for error in mock_render_consumer(document)))

    def test_invalid_sha_and_frame_id_are_rejected(self) -> None:
        document = valid_observation()
        document["provenance"]["base_sha"] = "A" * 40
        self.assertTrue(mock_render_consumer(document))
        document = valid_observation()
        document["frame_id"] = "M02 Fixture"
        self.assertTrue(mock_render_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["render_settings"]["vsync_mode"] = 3; perturbations.append(doc)
        doc = valid_observation(); doc["render_settings"]["max_fps"] = 300; perturbations.append(doc)
        doc = valid_observation(); doc["camera"]["viewport"]["width_px"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["frame_interval"]["samples_ms"] = [0]; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_render_consumer(document))


class M02OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest()
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertTrue(manifest["rules"]["single_writer_per_path"])

    def test_paths_are_relative_and_normalized(self) -> None:
        manifest = read_manifest()
        for entry in manifest["paths"]:
            normalized = normalize_path(entry["path"])
            self.assertEqual(normalized, entry["path"].casefold())
            self.assertFalse(entry["path"].startswith(("/", "\\")))
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        manifest = read_manifest()
        bases: list[str] = []
        for entry in manifest["paths"]:
            base = normalize_path(entry["path"]).removesuffix("/**")
            for existing in bases:
                self.assertFalse(
                    base == existing
                    or base.startswith(existing + "/")
                    or existing.startswith(base + "/"),
                    f"overlapping write paths: {base!r} and {existing!r}",
                )
            bases.append(base)

    def test_every_path_has_owner_and_consumers(self) -> None:
        manifest = read_manifest()
        owners = {entry["owner"] for entry in manifest["paths"]}
        self.assertEqual("integration-steward", manifest["writer"])
        self.assertIn("integration-steward", owners)
        for entry in manifest["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)

    def test_absolute_and_traversal_paths_are_rejected(self) -> None:
        for path in ("/etc/passwd", "C:/Windows/system32", "../outside", "a/../../outside"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    normalize_path(path)


if __name__ == "__main__":
    unittest.main()

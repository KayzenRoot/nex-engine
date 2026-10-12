"""Contract examples plus a LIMITED subset validator; not standards-complete."""
from __future__ import annotations

import copy
import json
import math
import re
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "contracts" / "m01"


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_non_finite(token: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {token}")


def strict_json_loads(raw: str) -> Any:
    """Load JSON while rejecting duplicate keys and NaN/Infinity."""
    return json.loads(
        raw,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_non_finite,
    )


def read_schema(filename: str) -> dict[str, Any]:
    return strict_json_loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        try:
            return math.isfinite(value)
        except OverflowError:
            return False
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def limited_schema_errors(
    value: Any, schema: dict[str, Any], location: str = "$"
) -> list[str]:
    """Check only the schema keywords exercised here, not all of JSON Schema."""
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(value, expected_type):
        return [f"{location}: expected {expected_type}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: value does not match const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value is not in enum")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{location}: string is too short")
        if len(value) > schema.get("maxLength", math.inf):
            errors.append(f"{location}: string is too long")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{location}: string does not match pattern")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", -math.inf):
            errors.append(f"{location}: number is below minimum")
        if value > schema.get("maximum", math.inf):
            errors.append(f"{location}: number is above maximum")
        if value <= schema.get("exclusiveMinimum", -math.inf):
            errors.append(f"{location}: number is not above exclusive minimum")
        if value >= schema.get("exclusiveMaximum", math.inf):
            errors.append(f"{location}: number is not below exclusive maximum")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: array has too few items")
        if len(value) > schema.get("maxItems", math.inf):
            errors.append(f"{location}: array has too many items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    limited_schema_errors(item, item_schema, f"{location}[{index}]")
                )

    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{location}: missing required property {required}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"{location}: unexpected property {key}")
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(
                    limited_schema_errors(value[key], child_schema, f"{location}.{key}")
                )

    if "oneOf" in schema:
        matches = sum(
            not limited_schema_errors(value, candidate, location)
            for candidate in schema["oneOf"]
        )
        if matches != 1:
            errors.append(f"{location}: expected exactly one oneOf branch")
    return errors


def valid_scene_manifest() -> dict[str, Any]:
    return {
        "schema_version": "scene_manifest.v1",
        "scene_id": "synthetic-scene-001",
        "scene_revision": 1,
        "seed": 314159,
        "scene_sha256": "a" * 64,
        "scene_unit_scale_m": 1.0,
        "camera": {
            "preset_id": "fixture-orbit",
            "projection": "perspective",
            "position_m": [0.0, 3.0, 8.0],
            "target_m": [0.0, 1.0, 0.0],
            "vertical_fov_degrees": 60.0,
            "near_clip_m": 0.05,
            "far_clip_m": 1000.0,
        },
        "renderer_id": "godot.forward_plus",
        "quality_preset": "high",
        "resolution": {"width_px": 1280, "height_px": 720, "unit": "px"},
        "assets": [
            {
                "asset_id": "synthetic-mesh",
                "sha256": "b" * 64,
                "source_uri": "https://example.invalid/synthetic-mesh",
                "creator": "NEX contract test fixture",
                "license_id": "CC0-1.0",
                "license_uri": "https://spdx.org/licenses/CC0-1.0.html",
                "verification": {"status": "UNVERIFIED"},
            }
        ],
    }


def mock_scene_consumer(scene_manifest: dict[str, Any]) -> list[str]:
    """Independent mock consumer that accepts only a scene manifest contract."""
    errors = limited_schema_errors(
        scene_manifest, read_schema("scene_manifest.v1.schema.json")
    )
    camera = scene_manifest.get("camera", {})
    near_clip = camera.get("near_clip_m")
    far_clip = camera.get("far_clip_m")
    if (
        isinstance(near_clip, (int, float))
        and not isinstance(near_clip, bool)
        and isinstance(far_clip, (int, float))
        and not isinstance(far_clip, bool)
        and far_clip <= near_clip
    ):
        errors.append("$.camera.far_clip_m: must exceed near_clip_m")
    return errors

class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_and_non_finite_numbers_are_rejected(self) -> None:
        for raw in (
            '{"a": 1, "a": 2}',
            '{"sample": NaN}',
            '{"sample": Infinity}',
            '{"sample": -Infinity}',
        ):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    strict_json_loads(raw)


class SceneManifestContractTests(unittest.TestCase):
    def test_synthetic_manifest_and_negative_perturbations(self) -> None:
        schema = read_schema("scene_manifest.v1.schema.json")
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema", schema.get("$schema")
        )
        self.assertEqual([], mock_scene_consumer(valid_scene_manifest()))

        invalid_documents = []
        document = valid_scene_manifest()
        document["schema_version"] = "scene_manifest.v2"
        invalid_documents.append(("schema version", document))

        document = valid_scene_manifest()
        document["scene_sha256"] = "not-a-sha256"
        invalid_documents.append(("scene digest", document))

        document = valid_scene_manifest()
        document["seed"] = -1
        invalid_documents.append(("negative seed", document))

        document = valid_scene_manifest()
        document["scene_unit_scale_m"] = 0
        invalid_documents.append(("zero scale", document))

        document = valid_scene_manifest()
        document["camera"]["vertical_fov_degrees"] = 180
        invalid_documents.append(("camera bounds", document))

        document = valid_scene_manifest()
        document["resolution"]["width_px"] = 0
        invalid_documents.append(("resolution bounds", document))

        document = valid_scene_manifest()
        del document["assets"][0]["license_id"]
        invalid_documents.append(("missing license", document))

        document = valid_scene_manifest()
        del document["assets"][0]["source_uri"]
        invalid_documents.append(("missing source provenance", document))

        document = valid_scene_manifest()
        document["assets"][0]["verification"]["status"] = "VERIFIED"
        document["assets"][0]["verification"].pop("evidence_uri", None)
        invalid_documents.append(("verified asset without evidence", document))


        document = valid_scene_manifest()
        del document["assets"][0]["creator"]
        invalid_documents.append(("missing creator", document))

        document = valid_scene_manifest()
        del document["assets"][0]["sha256"]
        invalid_documents.append(("missing asset digest", document))

        document = valid_scene_manifest()
        del document["assets"][0]["license_uri"]
        invalid_documents.append(("missing license provenance", document))

        document = valid_scene_manifest()
        document["assets"][0]["verification"]["status"] = "UNKNOWN"
        invalid_documents.append(("unknown verification status", document))

        document = valid_scene_manifest()
        document["camera"]["position_m"] = [0.0, 1.0]
        invalid_documents.append(("camera vector length", document))

        document = valid_scene_manifest()
        document["resolution"]["height_px"] = 16385
        invalid_documents.append(("resolution upper bound", document))

        document = valid_scene_manifest()
        document["unexpected_claim"] = True
        invalid_documents.append(("unknown property", document))

        for case, document in invalid_documents:
            with self.subTest(case=case):
                self.assertTrue(
                    limited_schema_errors(document, schema),
                    f"{case} unexpectedly passed the limited schema check",
                )

        unverified = copy.deepcopy(valid_scene_manifest())
        self.assertEqual(
            "UNVERIFIED", unverified["assets"][0]["verification"]["status"]
        )



def valid_telemetry_run(
    scene_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scene = scene_manifest or valid_scene_manifest()
    return {
        "schema_version": "telemetry_run.v1",
        "run_id": "synthetic-run-001",
        "git_sha": "c" * 40,
        "scene_id": scene["scene_id"],
        "scene_sha256": scene["scene_sha256"],
        "renderer_id": scene["renderer_id"],
        "toolchain": {
            "engine_version": "mock-engine-0",
            "toolchain_id": "stdlib-fixture",
            "platform": "synthetic-test",
        },
        "execution_mode": "synthetic",
        "clock": {"domain": "monotonic", "timestamp_unit": "ms"},
        "frame_time_unit": "ms",
        "warmup_count": 2,
        "sample_count": 2,
        "samples": [
            {"timestamp_ms": 1000.0, "frame_time_ms": 16.7},
            {"timestamp_ms": 1016.7, "frame_time_ms": 16.6},
        ],
        "gpu": {
            "availability": "UNAVAILABLE",
            "source": "not measured by the synthetic fixture",
        },
        "vram": {
            "availability": "UNAVAILABLE",
            "source": "not measured by the synthetic fixture",
        },
    }


def telemetry_contract_errors(
    run: dict[str, Any],
    schema: dict[str, Any],
    scene_manifest: dict[str, Any] | None = None,
) -> list[str]:
    errors = limited_schema_errors(run, schema)
    samples = run.get("samples", [])
    if run.get("sample_count") != len(samples):
        errors.append("$.sample_count: does not equal samples length")
    timestamps = [sample.get("timestamp_ms") for sample in samples]
    if any(
        isinstance(left, (int, float))
        and isinstance(right, (int, float))
        and right <= left
        for left, right in zip(timestamps, timestamps[1:])
    ):
        errors.append("$.samples: monotonic timestamps must strictly increase")
    if scene_manifest is not None:
        if run.get("scene_id") != scene_manifest.get("scene_id"):
            errors.append("$.scene_id: does not match manifest")
        if run.get("scene_sha256") != scene_manifest.get("scene_sha256"):
            errors.append("$.scene_sha256: does not match manifest")
    return errors



def mock_telemetry_consumer(
    run: dict[str, Any], scene_manifest: dict[str, Any]
) -> list[str]:
    """Independent mock consumer that binds a telemetry run to its scene manifest."""
    return telemetry_contract_errors(
        run, read_schema("telemetry_run.v1.schema.json"), scene_manifest
    )

class TelemetryRunContractTests(unittest.TestCase):
    def test_synthetic_run_is_bound_to_its_manifest(self) -> None:
        schema = read_schema("telemetry_run.v1.schema.json")
        scene = valid_scene_manifest()
        run = valid_telemetry_run(scene)
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema", schema.get("$schema")
        )
        self.assertEqual([], mock_telemetry_consumer(run, scene))

        wrong_digest = copy.deepcopy(run)
        wrong_digest["scene_sha256"] = "d" * 64
        self.assertTrue(mock_telemetry_consumer(wrong_digest, scene))

    def test_invalid_versions_hashes_units_counts_and_clock_are_rejected(self) -> None:
        schema = read_schema("telemetry_run.v1.schema.json")
        scene = valid_scene_manifest()
        invalid_runs = []

        run = valid_telemetry_run(scene)
        run["schema_version"] = "telemetry_run.v2"
        invalid_runs.append(("schema version", run))

        run = valid_telemetry_run(scene)
        run["git_sha"] = "c" * 39
        invalid_runs.append(("git sha", run))

        run = valid_telemetry_run(scene)
        run["clock"]["domain"] = "wall"
        invalid_runs.append(("clock domain", run))

        run = valid_telemetry_run(scene)
        run["frame_time_unit"] = "us"
        invalid_runs.append(("frame time unit", run))

        run = valid_telemetry_run(scene)
        run["sample_count"] = -1
        invalid_runs.append(("negative sample count", run))

        run = valid_telemetry_run(scene)
        run["sample_count"] = 3
        invalid_runs.append(("sample count mismatch", run))

        run = valid_telemetry_run(scene)
        run["warmup_count"] = -1
        invalid_runs.append(("negative warmup count", run))

        run = valid_telemetry_run(scene)
        run["samples"][0]["frame_time_ms"] = -0.1
        invalid_runs.append(("negative frame time", run))

        run = valid_telemetry_run(scene)
        run["samples"][1]["timestamp_ms"] = run["samples"][0]["timestamp_ms"]
        invalid_runs.append(("non-monotonic timestamps", run))

        run = valid_telemetry_run(scene)
        run["fps"] = 60
        invalid_runs.append(("unsupported fps assertion", run))


        run = valid_telemetry_run(scene)
        run["clock"]["timestamp_unit"] = "s"
        invalid_runs.append(("timestamp unit", run))

        run = valid_telemetry_run(scene)
        run["samples"][0]["timestamp_ms"] = -1
        invalid_runs.append(("negative timestamp", run))

        run = valid_telemetry_run(scene)
        run["samples"][0]["frame_time_ms"] = math.nan
        invalid_runs.append(("NaN frame time", run))

        run = valid_telemetry_run(scene)
        run["samples"][0]["frame_time_ms"] = math.inf
        invalid_runs.append(("infinite frame time", run))
        for case, run in invalid_runs:
            with self.subTest(case=case):
                self.assertTrue(telemetry_contract_errors(run, schema, scene))

    def test_unavailable_metrics_need_sources_and_measured_zero_stays_zero(self) -> None:
        schema = read_schema("telemetry_run.v1.schema.json")
        scene = valid_scene_manifest()
        unavailable = valid_telemetry_run(scene)
        del unavailable["gpu"]["source"]
        self.assertTrue(telemetry_contract_errors(unavailable, schema, scene))

        unavailable = valid_telemetry_run(scene)
        unavailable["gpu"]["utilization_percent"] = 0
        self.assertTrue(telemetry_contract_errors(unavailable, schema, scene))

        unavailable = valid_telemetry_run(scene)
        del unavailable["vram"]["source"]
        self.assertTrue(telemetry_contract_errors(unavailable, schema, scene))

        measured_zero = valid_telemetry_run(scene)
        measured_zero["gpu"] = {
            "availability": "AVAILABLE",
            "source": "synthetic zero-valued instrument fixture",
            "utilization_percent": 0,
        }
        measured_zero["vram"] = {
            "availability": "AVAILABLE",
            "source": "synthetic zero-valued instrument fixture",
            "used_bytes": 0,
        }
        self.assertEqual([], mock_telemetry_consumer(measured_zero, scene))

if __name__ == "__main__":
    unittest.main()

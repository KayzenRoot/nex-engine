"""M06 performance contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import itertools
import unittest
from typing import Any

from _contract_support import (
    global_unavailable_errors,
    provenance_evidence_errors,
    read_manifest,
    read_schema,
)
from test_m01_schema import limited_schema_errors
from test_ownership_locks import normalize_path


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "performance.v1",
        "observation_id": "m06-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "workload": {
            "scene_id": "dense-city",
            "proxy_count": 200,
            "effect_mode": "lights",
            "resolution": {"width_px": 1920, "height_px": 1080, "unit": "px"},
            "vsync": False,
            "max_fps": 0,
        },
        "frame_interval": {
            "status": "MEASURED",
            "provider": "SceneTree._process(delta)",
            "samples_ms": [8.2, 8.3, 8.4],
        },
        "timings": {
            "gpu_render_ms": {"status": "MEASURED", "value": 1.2},
            "cpu_render_ms": {"status": "UNAVAILABLE", "unavailable_reason": "no CPU provider"},
            "frame_pacing_ms": {"status": "UNAVAILABLE", "unavailable_reason": "no pacing provider"},
        },
        "resources": {
            "draw_calls": {"status": "MEASURED", "value": 240},
            "objects_rendered": {"status": "MEASURED", "value": 1200},
            "renderer_allocation_bytes": {"status": "UNAVAILABLE", "unavailable_reason": "not sampled"},
            "vram_used_bytes": {"status": "UNAVAILABLE", "unavailable_reason": "not sampled"},
        },
        "bottleneck": {
            "classification": "gpu",
            "evidence": "measured",
            "confidence": "medium",
            "rationale": "GPU render time dominates the measured frame interval.",
        },
        "provenance": {
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "godot_version": "4.7.2-stable",
            "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
            "capture_mode": "windowed",
            "measurement_status": "MEASURED",
            "evidence_uri": "evidence://m06-fixture",
        },
    }


def _metric(document: dict[str, Any], group: str, key: str) -> str:
    value = document.get(group, {}).get(key)
    return value.get("status", "") if isinstance(value, dict) else ""


def mock_performance_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus bottleneck coherence."""
    errors = limited_schema_errors(document, read_schema("m06", "performance.v1.schema.json"))
    bottleneck = document.get("bottleneck")
    if isinstance(bottleneck, dict):
        classification = bottleneck.get("classification")
        evidence = bottleneck.get("evidence")
        if classification == "gpu" and evidence != "unavailable" and _metric(document, "timings", "gpu_render_ms") != "MEASURED":
            errors.append("$.bottleneck: gpu classification requires MEASURED gpu_render_ms")
        if classification == "cpu" and evidence != "unavailable" and _metric(document, "timings", "cpu_render_ms") != "MEASURED":
            errors.append("$.bottleneck: cpu classification requires MEASURED cpu_render_ms")
        if classification == "pacing" and evidence != "unavailable" and _metric(document, "timings", "frame_pacing_ms") != "MEASURED":
            errors.append("$.bottleneck: pacing classification requires MEASURED frame_pacing_ms")
        if classification == "memory" and evidence != "unavailable" and _metric(document, "resources", "vram_used_bytes") != "MEASURED":
            errors.append("$.bottleneck: memory classification requires MEASURED vram_used_bytes")
        if evidence == "unavailable" and classification not in ("unknown", "insufficient_data"):
            errors.append("$.bottleneck: unavailable evidence requires unknown or insufficient_data")
        if classification == "insufficient_data":
            for group, key in (
                ("timings", "gpu_render_ms"),
                ("timings", "cpu_render_ms"),
                ("timings", "frame_pacing_ms"),
                ("resources", "draw_calls"),
                ("resources", "objects_rendered"),
                ("resources", "renderer_allocation_bytes"),
                ("resources", "vram_used_bytes"),
            ):
                if _metric(document, group, key) == "MEASURED":
                    errors.append(f"$.bottleneck: insufficient_data forbids MEASURED {key}")
    errors.extend(global_unavailable_errors(document))
    errors.extend(provenance_evidence_errors(document))
    return errors


class PerformanceContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m06", "performance.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("performance.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_performance_consumer(valid_observation()))

    def test_missing_workload_is_rejected(self) -> None:
        document = valid_observation()
        del document["workload"]
        self.assertIn(
            "$: missing required property workload",
            limited_schema_errors(document, read_schema("m06", "performance.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 120
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_performance_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["timings"]["gpu_render_ms"] = {"status": "UNAVAILABLE", "unavailable_reason": "no GPU provider"}
        document["bottleneck"] = {
            "classification": "unknown",
            "evidence": "unavailable",
            "confidence": "low",
            "rationale": "GPU timing is unavailable.",
        }
        self.assertEqual([], mock_performance_consumer(document))

        zero = valid_observation()
        zero["timings"]["gpu_render_ms"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_performance_consumer(zero))

        fabricated = valid_observation()
        fabricated["timings"]["gpu_render_ms"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 1.2,
        }
        self.assertTrue(mock_performance_consumer(fabricated))

    def test_gpu_and_cpu_classification_require_metrics(self) -> None:
        document = valid_observation()
        document["timings"]["gpu_render_ms"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertTrue(
            any("gpu classification requires" in error for error in mock_performance_consumer(document))
        )

        document = valid_observation()
        document["bottleneck"]["classification"] = "cpu"
        self.assertTrue(
            any("cpu classification requires" in error for error in mock_performance_consumer(document))
        )

    def test_pacing_and_memory_classification_require_metrics(self) -> None:
        document = valid_observation()
        document["bottleneck"]["classification"] = "pacing"
        self.assertTrue(
            any("pacing classification requires" in error for error in mock_performance_consumer(document))
        )

        document = valid_observation()
        document["bottleneck"]["classification"] = "memory"
        self.assertTrue(
            any("memory classification requires" in error for error in mock_performance_consumer(document))
        )

        measured_memory = valid_observation()
        measured_memory["bottleneck"]["classification"] = "memory"
        measured_memory["resources"]["vram_used_bytes"] = {"status": "MEASURED", "value": 4194304}
        self.assertEqual([], mock_performance_consumer(measured_memory))

    def test_insufficient_data_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["bottleneck"] = {
            "classification": "insufficient_data",
            "evidence": "unavailable",
            "confidence": "low",
            "rationale": "No metric provider was available.",
        }
        self.assertTrue(
            any("insufficient_data forbids MEASURED" in error for error in mock_performance_consumer(document))
        )

        all_unavailable = valid_observation()
        all_unavailable["frame_interval"] = {
            "status": "UNAVAILABLE",
            "provider": "SceneTree._process(delta)",
            "unavailable_reason": "no runtime",
        }
        for group in ("timings", "resources"):
            for key in all_unavailable[group]:
                all_unavailable[group][key] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        all_unavailable["bottleneck"] = {
            "classification": "insufficient_data",
            "evidence": "unavailable",
            "confidence": "low",
            "rationale": "No metric provider was available.",
        }
        self.assertEqual([], mock_performance_consumer(all_unavailable))

    def test_unavailable_evidence_requires_unknown(self) -> None:
        document = valid_observation()
        document["bottleneck"]["evidence"] = "unavailable"
        self.assertTrue(
            any("unavailable evidence requires" in error for error in mock_performance_consumer(document))
        )

        unknown = valid_observation()
        unknown["bottleneck"] = {
            "classification": "unknown",
            "evidence": "unavailable",
            "confidence": "low",
            "rationale": "Insufficient evidence to classify.",
        }
        self.assertEqual([], mock_performance_consumer(unknown))

    def test_comparison_is_optional_and_bounded(self) -> None:
        document = valid_observation()
        document["comparison"] = {
            "baseline_observation_id": "m06-baseline-001",
            "delta_gpu_ms": -0.4,
            "delta_cpu_ms": 0.2,
        }
        self.assertEqual([], mock_performance_consumer(document))

        document["comparison"]["delta_gpu_ms"] = 20000
        self.assertTrue(mock_performance_consumer(document))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        del document["provenance"]["evidence_uri"]
        self.assertTrue(any("evidence_uri" in error for error in mock_performance_consumer(document)))

    def test_invalid_workload_is_rejected(self) -> None:
        document = valid_observation()
        document["workload"]["scene_id"] = "Dense City"
        self.assertTrue(mock_performance_consumer(document))

        document = valid_observation()
        document["workload"]["resolution"]["width_px"] = 0
        self.assertTrue(mock_performance_consumer(document))

        document = valid_observation()
        document["workload"]["effect_mode"] = "magic"
        self.assertTrue(mock_performance_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["timings"]["gpu_render_ms"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["frame_interval"]["samples_ms"] = [0]; perturbations.append(doc)
        doc = valid_observation(); doc["resources"]["draw_calls"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["bottleneck"]["confidence"] = "certain"; perturbations.append(doc)
        doc = valid_observation(); doc["workload"]["max_fps"] = 1001; perturbations.append(doc)
        doc = valid_observation(); doc["provenance"]["base_sha"] = "A" * 40; perturbations.append(doc)
        doc = valid_observation(); doc["workload"]["proxy_count"] = 1000001; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_performance_consumer(document))


class M06OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m06")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m06")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m06")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m06")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

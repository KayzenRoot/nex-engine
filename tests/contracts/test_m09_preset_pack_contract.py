"""M09 preset pack contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import itertools
import unittest
from typing import Any

from _contract_support import (
    provenance_evidence_errors,
    read_manifest,
    read_schema,
    unavailable_provenance,
)
from test_m01_schema import limited_schema_errors
from test_ownership_locks import normalize_path

TIER_ORDER = ("low", "medium", "high", "ultra")
SHADOW_RANK = {"off": 0, "low": 1, "medium": 2, "high": 3, "ultra": 4}


def _preset(preset_id: str, tier: str, resolution: float, shadow: str, atlas: int, target_fps: int,
            reduced_motion: bool = False, shake: float = 1.0, hit_stop: float = 1.0) -> dict[str, Any]:
    return {
        "preset_id": preset_id,
        "label": preset_id.title(),
        "tier": tier,
        "settings": {
            "rendering": {
                "renderer_id": "godot.forward_plus",
                "driver_id": "vulkan",
                "resolution_scale": resolution,
                "msaa": "4x",
                "shadow_quality": shadow,
            },
            "lighting": {
                "tonemap": "filmic",
                "glow": True,
                "shadow_atlas_size": atlas,
                "max_shadowed_lights": 8,
            },
            "performance": {
                "target_fps": target_fps,
                "max_draw_calls": 8000,
                "lod_bias": 0.5,
            },
            "feedback": {
                "hit_stop_scale": hit_stop,
                "shake_scale": shake,
                "reduced_motion": reduced_motion,
            },
        },
    }


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "preset_pack.v1",
        "observation_id": "m09-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "pack_id": "nex-quality-pack",
        "presets": [
            _preset("quality-low", "low", 0.5, "low", 1024, 60),
            _preset("quality-medium", "medium", 0.75, "medium", 2048, 60),
            _preset("quality-high", "high", 1.0, "high", 4096, 120),
            _preset("quality-ultra", "ultra", 1.0, "ultra", 8192, 120),
            _preset("accessibility-reduced-motion", "custom", 1.0, "high", 4096, 60,
                    reduced_motion=True, shake=0.25, hit_stop=0.5),
        ],
        "compatibility": {
            "contract_versions": ["render_core.v1", "lighting.v1", "performance.v1", "composition.v1", "feedback.v1"],
            "godot_version_range": "4.7.x",
            "hardware_tier": "desktop",
        },
        "provenance": unavailable_provenance(),
    }


def mock_preset_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus tier/accessibility invariants."""
    errors = limited_schema_errors(document, read_schema("m09", "preset_pack.v1.schema.json"))
    presets = document.get("presets")
    if isinstance(presets, list) and all(isinstance(preset, dict) for preset in presets):
        ids = [preset.get("preset_id") for preset in presets]
        if len(ids) != len(set(ids)):
            errors.append("$.presets: duplicate preset_id")
        tiers = [preset.get("tier") for preset in presets if preset.get("tier") in TIER_ORDER]
        if len(tiers) != len(set(tiers)):
            errors.append("$.presets: duplicate standard tier")
        for preset in presets:
            if not preset.get("settings"):
                errors.append(f"$.presets[{preset.get('preset_id')}]: settings are empty")
            feedback = preset.get("settings", {}).get("feedback", {})
            if isinstance(feedback, dict) and feedback.get("reduced_motion"):
                if float(feedback.get("shake_scale", 1.0)) > 0.5:
                    errors.append(f"$.presets[{preset.get('preset_id')}]: reduced motion requires shake_scale <= 0.5")
                if float(feedback.get("hit_stop_scale", 1.0)) > 1.0:
                    errors.append(f"$.presets[{preset.get('preset_id')}]: reduced motion requires hit_stop_scale <= 1.0")
        by_tier = {preset["tier"]: preset for preset in presets if preset.get("tier") in TIER_ORDER}
        for lower, higher in zip(TIER_ORDER, TIER_ORDER[1:]):
            if lower not in by_tier or higher not in by_tier:
                continue
            low_settings = by_tier[lower].get("settings", {})
            high_settings = by_tier[higher].get("settings", {})
            low_rendering = low_settings.get("rendering", {})
            high_rendering = high_settings.get("rendering", {})
            if "resolution_scale" in low_rendering and "resolution_scale" in high_rendering:
                if float(high_rendering["resolution_scale"]) < float(low_rendering["resolution_scale"]):
                    errors.append(f"$.presets: {higher} resolution_scale below {lower}")
            if "shadow_quality" in low_rendering and "shadow_quality" in high_rendering:
                if SHADOW_RANK[high_rendering["shadow_quality"]] < SHADOW_RANK[low_rendering["shadow_quality"]]:
                    errors.append(f"$.presets: {higher} shadow_quality below {lower}")
            low_lighting = low_settings.get("lighting", {})
            high_lighting = high_settings.get("lighting", {})
            if "shadow_atlas_size" in low_lighting and "shadow_atlas_size" in high_lighting:
                if int(high_lighting["shadow_atlas_size"]) < int(low_lighting["shadow_atlas_size"]):
                    errors.append(f"$.presets: {higher} shadow_atlas_size below {lower}")
            low_perf = low_settings.get("performance", {})
            high_perf = high_settings.get("performance", {})
            if "target_fps" in low_perf and "target_fps" in high_perf:
                if int(high_perf["target_fps"]) < int(low_perf["target_fps"]):
                    errors.append(f"$.presets: {higher} target_fps below {lower}")
    compatibility = document.get("compatibility", {})
    if isinstance(compatibility, dict):
        versions = compatibility.get("contract_versions", [])
        if isinstance(versions, list) and len(versions) != len(set(versions)):
            errors.append("$.compatibility.contract_versions: duplicate version")
    errors.extend(provenance_evidence_errors(document))
    return errors


class PresetPackContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m09", "preset_pack.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("preset_pack.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_preset_consumer(valid_observation()))

    def test_missing_presets_is_rejected(self) -> None:
        document = valid_observation()
        del document["presets"]
        self.assertIn(
            "$: missing required property presets",
            limited_schema_errors(document, read_schema("m09", "preset_pack.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(any("unexpected property fps" in error for error in mock_preset_consumer(document)))

    def test_duplicate_preset_and_tier_are_rejected(self) -> None:
        duplicate = valid_observation()
        duplicate["presets"][1]["preset_id"] = "quality-low"
        self.assertTrue(any("duplicate preset_id" in error for error in mock_preset_consumer(duplicate)))

        duplicate_tier = valid_observation()
        duplicate_tier["presets"][1]["tier"] = "low"
        self.assertTrue(any("duplicate standard tier" in error for error in mock_preset_consumer(duplicate_tier)))

    def test_empty_settings_is_rejected(self) -> None:
        document = valid_observation()
        document["presets"][0]["settings"] = {}
        self.assertTrue(any("settings are empty" in error for error in mock_preset_consumer(document)))

    def test_tier_monotonicity(self) -> None:
        resolution = valid_observation()
        resolution["presets"][1]["settings"]["rendering"]["resolution_scale"] = 0.4
        self.assertTrue(any("resolution_scale below" in error for error in mock_preset_consumer(resolution)))

        shadow = valid_observation()
        shadow["presets"][2]["settings"]["rendering"]["shadow_quality"] = "low"
        self.assertTrue(any("shadow_quality below" in error for error in mock_preset_consumer(shadow)))

        atlas = valid_observation()
        atlas["presets"][2]["settings"]["lighting"]["shadow_atlas_size"] = 1024
        self.assertTrue(any("shadow_atlas_size below" in error for error in mock_preset_consumer(atlas)))

        fps = valid_observation()
        fps["presets"][2]["settings"]["performance"]["target_fps"] = 30
        self.assertTrue(any("target_fps below" in error for error in mock_preset_consumer(fps)))

    def test_reduced_motion_limits(self) -> None:
        shake = valid_observation()
        shake["presets"][4]["settings"]["feedback"]["shake_scale"] = 0.75
        self.assertTrue(any("shake_scale <= 0.5" in error for error in mock_preset_consumer(shake)))

        hit_stop = valid_observation()
        hit_stop["presets"][4]["settings"]["feedback"]["hit_stop_scale"] = 1.5
        self.assertTrue(any("hit_stop_scale <= 1.0" in error for error in mock_preset_consumer(hit_stop)))

    def test_compatibility_versions_are_unique(self) -> None:
        document = valid_observation()
        document["compatibility"]["contract_versions"] = ["lighting.v1", "lighting.v1"]
        self.assertTrue(any("duplicate version" in error for error in mock_preset_consumer(document)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_preset_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m09-fixture"
        self.assertEqual([], mock_preset_consumer(document))

    def test_invalid_vocabulary_is_rejected(self) -> None:
        document = valid_observation()
        document["presets"][0]["tier"] = "potato"
        self.assertTrue(mock_preset_consumer(document))

        document = valid_observation()
        document["presets"][0]["settings"]["rendering"]["driver_id"] = "metal"
        self.assertTrue(mock_preset_consumer(document))

        document = valid_observation()
        document["compatibility"]["hardware_tier"] = "server"
        self.assertTrue(mock_preset_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["presets"][0]["settings"]["rendering"]["resolution_scale"] = 0.1; perturbations.append(doc)
        doc = valid_observation(); doc["presets"][0]["settings"]["lighting"]["shadow_atlas_size"] = 128; perturbations.append(doc)
        doc = valid_observation(); doc["presets"][0]["settings"]["performance"]["target_fps"] = 10; perturbations.append(doc)
        doc = valid_observation(); doc["presets"][0]["settings"]["feedback"]["shake_scale"] = 2.5; perturbations.append(doc)
        doc = valid_observation(); doc["presets"][0]["settings"]["accessibility"] = {"min_text_contrast_ratio": 2, "focus_ring_px": 0}; perturbations.append(doc)
        doc = valid_observation(); doc["provenance"]["base_sha"] = "A" * 40; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_preset_consumer(document))


class M09OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m09")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m09")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m09")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m09")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

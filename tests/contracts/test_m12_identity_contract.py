"""M12 visual identity contract tests using the repository's limited stdlib checker."""
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


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255.0 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    high = max(_luminance(first), _luminance(second))
    low = min(_luminance(first), _luminance(second))
    return (high + 0.05) / (low + 0.05)


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "identity.v1",
        "observation_id": "m12-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "palette": [
            {"token": "nex-primary", "hex": "#1f6feb", "role": "primary"},
            {"token": "nex-background", "hex": "#0b0f14", "role": "background"},
            {"token": "nex-foreground", "hex": "#f0f4f8", "role": "foreground"},
            {"token": "nex-accent", "hex": "#35d0ff", "role": "accent"},
            {"token": "nex-surface", "hex": "#161b22", "role": "surface"},
            {"token": "nex-error", "hex": "#ff5c5c", "role": "error"},
            {"token": "nex-success", "hex": "#3fb950", "role": "success"},
            {"token": "nex-warning", "hex": "#d29922", "role": "warning"},
        ],
        "typography": {
            "font_family": "Inter",
            "display_size_px": 48,
            "body_size_px": 16,
            "line_height_ratio": 1.5,
            "weights": [400, 600, 700],
        },
        "logo": {
            "mark_svg_uri": "res://brand/nex_mark.svg",
            "mark_sha256": "a" * 64,
            "mark_view_box": [0, 0, 64, 64],
            "wordmark_svg_uri": "res://brand/nex_wordmark.svg",
            "wordmark_sha256": "b" * 64,
            "wordmark_view_box": [0, 0, 240, 64],
            "monochrome_sha256": "c" * 64,
            "clear_space_ratio": 0.25,
        },
        "spacing": {
            "base_px": 4,
            "scale": [4, 8, 12, 16, 24, 32, 48, 64],
            "max_content_width_px": 1440,
        },
        "accessibility": {
            "min_text_contrast_ratio": 4.5,
            "min_large_text_contrast_ratio": 3.0,
            "requires_focus_indicator": True,
            "min_focus_ring_px": 2,
        },
        "provenance": unavailable_provenance(),
    }


def _roles(document: dict[str, Any]) -> dict[str, str]:
    return {entry["role"]: entry["hex"] for entry in document.get("palette", []) if isinstance(entry, dict)}


def mock_identity_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus identity/contrast invariants."""
    errors = limited_schema_errors(document, read_schema("m12", "identity.v1.schema.json"))
    palette = document.get("palette", [])
    if isinstance(palette, list) and all(isinstance(entry, dict) for entry in palette):
        tokens = [entry.get("token") for entry in palette]
        if len(tokens) != len(set(tokens)):
            errors.append("$.palette: duplicate token")
        roles = _roles(document)
        for required in ("primary", "background", "foreground"):
            if required not in roles:
                errors.append(f"$.palette: missing required role {required}")
        accessibility = document.get("accessibility", {})
        if isinstance(accessibility, dict) and "background" in roles:
            background = roles["background"]
            text_threshold = float(accessibility.get("min_text_contrast_ratio", 4.5))
            large_threshold = float(accessibility.get("min_large_text_contrast_ratio", 3.0))
            if "foreground" in roles and contrast_ratio(roles["foreground"], background) < text_threshold:
                errors.append("$.palette: foreground/background contrast below text threshold")
            for role in ("primary", "error"):
                if role in roles and contrast_ratio(roles[role], background) < large_threshold:
                    errors.append(f"$.palette: {role}/background contrast below large-text threshold")
            for role in ("success", "warning"):
                if role in roles and contrast_ratio(roles[role], background) < large_threshold:
                    errors.append(f"$.palette: {role}/background contrast below large-text threshold")
    typography = document.get("typography", {})
    if isinstance(typography, dict):
        if int(typography.get("display_size_px", 0)) <= int(typography.get("body_size_px", 0)):
            errors.append("$.typography: display_size_px must exceed body_size_px")
        weights = typography.get("weights", [])
        if isinstance(weights, list):
            if len(weights) != len(set(weights)):
                errors.append("$.typography.weights: duplicate weight")
            if any(int(weight) % 100 != 0 for weight in weights):
                errors.append("$.typography.weights: weights must be multiples of 100")
    logo = document.get("logo", {})
    if isinstance(logo, dict):
        for key in ("mark_view_box", "wordmark_view_box"):
            box = logo.get(key)
            if isinstance(box, list) and len(box) == 4:
                if float(box[2]) <= 0 or float(box[3]) <= 0:
                    errors.append(f"$.logo.{key}: width and height must be positive")
    spacing = document.get("spacing", {})
    if isinstance(spacing, dict):
        scale = spacing.get("scale", [])
        base = int(spacing.get("base_px", 0))
        if isinstance(scale, list):
            if any(float(scale[index]) >= float(scale[index + 1]) for index in range(len(scale) - 1)):
                errors.append("$.spacing.scale: must be strictly ascending")
            if any(float(value) < base for value in scale):
                errors.append("$.spacing.scale: values must be at least base_px")
    accessibility = document.get("accessibility", {})
    if isinstance(accessibility, dict):
        if float(accessibility.get("min_large_text_contrast_ratio", 0)) > float(accessibility.get("min_text_contrast_ratio", 0)):
            errors.append("$.accessibility: large-text threshold exceeds text threshold")
        if accessibility.get("requires_focus_indicator") and int(accessibility.get("min_focus_ring_px", 0)) < 1:
            errors.append("$.accessibility: focus ring must be at least 1 px")
    errors.extend(provenance_evidence_errors(document))
    return errors


class IdentityContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m12", "identity.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("identity.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_identity_consumer(valid_observation()))

    def test_missing_palette_is_rejected(self) -> None:
        document = valid_observation()
        del document["palette"]
        self.assertIn(
            "$: missing required property palette",
            limited_schema_errors(document, read_schema("m12", "identity.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(any("unexpected property fps" in error for error in mock_identity_consumer(document)))

    def test_duplicate_token_is_rejected(self) -> None:
        document = valid_observation()
        document["palette"][1]["token"] = "nex-primary"
        self.assertTrue(any("duplicate token" in error for error in mock_identity_consumer(document)))

    def test_required_roles_are_enforced(self) -> None:
        document = valid_observation()
        document["palette"] = [entry for entry in document["palette"] if entry["role"] != "foreground"]
        self.assertTrue(any("missing required role foreground" in error for error in mock_identity_consumer(document)))

    def test_contrast_thresholds_are_enforced(self) -> None:
        low_foreground = valid_observation()
        low_foreground["palette"][2]["hex"] = "#777777"
        self.assertTrue(any("foreground/background contrast" in error for error in mock_identity_consumer(low_foreground)))

        low_primary = valid_observation()
        low_primary["palette"][0]["hex"] = "#111827"
        self.assertTrue(any("primary/background contrast" in error for error in mock_identity_consumer(low_primary)))

    def test_typography_invariants(self) -> None:
        small_display = valid_observation()
        small_display["typography"]["display_size_px"] = 16
        self.assertTrue(any("display_size_px" in error for error in mock_identity_consumer(small_display)))

        duplicate_weight = valid_observation()
        duplicate_weight["typography"]["weights"] = [400, 400]
        self.assertTrue(any("duplicate weight" in error for error in mock_identity_consumer(duplicate_weight)))

        bad_weight = valid_observation()
        bad_weight["typography"]["weights"] = [450]
        self.assertTrue(any("multiples of 100" in error for error in mock_identity_consumer(bad_weight)))

    def test_logo_view_box_must_be_positive(self) -> None:
        document = valid_observation()
        document["logo"]["mark_view_box"] = [0, 0, 0, 64]
        self.assertTrue(any("width and height must be positive" in error for error in mock_identity_consumer(document)))

    def test_spacing_scale_invariants(self) -> None:
        unsorted = valid_observation()
        unsorted["spacing"]["scale"] = [4, 8, 4]
        self.assertTrue(any("strictly ascending" in error for error in mock_identity_consumer(unsorted)))

        below_base = valid_observation()
        below_base["spacing"]["scale"] = [2, 4, 8]
        self.assertTrue(any("at least base_px" in error for error in mock_identity_consumer(below_base)))

    def test_accessibility_threshold_order(self) -> None:
        document = valid_observation()
        document["accessibility"]["min_large_text_contrast_ratio"] = 7.0
        self.assertTrue(any("large-text threshold exceeds" in error for error in mock_identity_consumer(document)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_identity_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m12-fixture"
        self.assertEqual([], mock_identity_consumer(document))

    def test_invalid_ids_and_colors_are_rejected(self) -> None:
        document = valid_observation()
        document["palette"][0]["token"] = "NEX Primary"
        self.assertTrue(mock_identity_consumer(document))

        document = valid_observation()
        document["palette"][0]["hex"] = "#ABCDEF"
        self.assertTrue(mock_identity_consumer(document))

        document = valid_observation()
        document["palette"][0]["role"] = "brand"
        self.assertTrue(mock_identity_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["typography"]["line_height_ratio"] = 0.5; perturbations.append(doc)
        doc = valid_observation(); doc["logo"]["mark_sha256"] = "A" * 64; perturbations.append(doc)
        doc = valid_observation(); doc["logo"]["clear_space_ratio"] = 1.5; perturbations.append(doc)
        doc = valid_observation(); doc["spacing"]["base_px"] = 1; perturbations.append(doc)
        doc = valid_observation(); doc["accessibility"]["min_focus_ring_px"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["provenance"]["base_sha"] = "A" * 40; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_identity_consumer(document))


class M12OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m12")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m12")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m12")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m12")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

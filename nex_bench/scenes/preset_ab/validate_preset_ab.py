#!/usr/bin/env python3
"""NEX M09 preset A/B/A validator.

Validates the harness provenance for the built-in grid and the three M01
scene modes, then delegates structural/aggregate checks to the shared lab
validation helper and the canonical GPU profile validator.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gpu_profile"))

import lab_validation  # noqa: E402 - path bootstrap above

EXPECTED_SCENE = "Preset A/B/A"
EXPECTED_LAYOUT = "built-in deterministic grid"
EXPECTED_PROXY_COUNTS = (25, 50, 100, 200)
M01_SCENE_SPECS = {
    "M01 Corridor A/B/A": ("M01 corridor_static + deterministic fillers", (50, 100, 200)),
    "M01 Arena A/B/A": ("M01 arena_combat + deterministic fillers", (50, 100, 200)),
    "M01 City A/B/A": ("M01 dense_city + deterministic fillers", (50, 100, 200)),
}
EXPECTED_EFFECT_MODE = "lights"
EXPECTED_MAX_FPS = 240
EXPECTED_VSYNC = 0
SCENE_SPECS = {EXPECTED_SCENE: (EXPECTED_LAYOUT, EXPECTED_PROXY_COUNTS), **M01_SCENE_SPECS}


def _loads(raw: bytes):
    return lab_validation.loads(raw)


def validate_document(document):
    """Validate harness provenance and delegate to canonical.validate_report."""
    return lab_validation.validate_document(
        document, SCENE_SPECS, EXPECTED_EFFECT_MODE, EXPECTED_MAX_FPS, EXPECTED_VSYNC)


def main() -> int:
    return lab_validation.run_cli(SCENE_SPECS, EXPECTED_EFFECT_MODE, EXPECTED_MAX_FPS, EXPECTED_VSYNC)


if __name__ == "__main__":
    sys.exit(main())

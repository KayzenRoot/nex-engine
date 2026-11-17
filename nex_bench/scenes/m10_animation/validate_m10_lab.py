#!/usr/bin/env python3
"""NEX M10 animation lab validator.

Delegates lab provenance and canonical profile checks to the shared
`lab_validation` helper. It never suppresses a check or fabricates metrics.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gpu_profile"))

import lab_validation  # noqa: E402 - path bootstrap above

EXPECTED_SCENE = "M10 Animation Lab"
EXPECTED_LAYOUT = "M10 animation and feedback lab"
EXPECTED_PROXY_COUNTS = (100,)
EXPECTED_EFFECT_MODE = "lights"
EXPECTED_MAX_FPS = 240
EXPECTED_VSYNC = 0
SCENE_SPECS = {EXPECTED_SCENE: (EXPECTED_LAYOUT, EXPECTED_PROXY_COUNTS)}


def validate_document(document):
    return lab_validation.validate_document(
        document, SCENE_SPECS, EXPECTED_EFFECT_MODE, EXPECTED_MAX_FPS, EXPECTED_VSYNC)


def main() -> int:
    return lab_validation.run_cli(SCENE_SPECS, EXPECTED_EFFECT_MODE, EXPECTED_MAX_FPS, EXPECTED_VSYNC)


if __name__ == "__main__":
    sys.exit(main())

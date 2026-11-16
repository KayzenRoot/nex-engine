#!/usr/bin/env python3
"""NEX M08 2.5D lab validator.

Delegates lab provenance and canonical profile checks to the shared
`lab_validation` helper. It never suppresses a check or fabricates metrics.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gpu_profile"))

import lab_validation  # noqa: E402 - path bootstrap above

EXPECTED_SCENE = "M08 Hybrid 2.5D Lab"
EXPECTED_LAYOUT = "M08 hybrid 2.5D lab"
EXPECTED_PROXY_COUNTS = (100,)
EXPECTED_EFFECT_MODE = "lights"
EXPECTED_MAX_FPS = 240
EXPECTED_VSYNC = 0
SCENE_SPECS = {EXPECTED_SCENE: (EXPECTED_LAYOUT, EXPECTED_PROXY_COUNTS)}


def validate_document(document):
    return lab_validation.validate_document(
        document, SCENE_SPECS, EXPECTED_EFFECT_MODE, EXPECTED_MAX_FPS, EXPECTED_VSYNC)


def main() -> int:
    payload = sys.stdin.buffer.read(lab_validation.canonical.MAX_BYTES + 1)
    if len(payload) > lab_validation.canonical.MAX_BYTES:
        print(json.dumps({"status": "FAIL", "reason": "profile input exceeds 8 MB limit"}))
        return 1
    try:
        result = validate_document(lab_validation.loads(payload))
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

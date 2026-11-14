#!/usr/bin/env python3
"""NEX M09 preset A/B/A validator.

Validates the harness provenance for the built-in grid and the three M01
scene modes, then delegates every structural/aggregate check to the canonical
GPU profile validator with only the scene/layout labels substituted. It never
suppresses a check and never fabricates metrics.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gpu_profile"))

import validate_gpu_profile as canonical  # noqa: E402 - path bootstrap above

EXPECTED_SCENE = "Preset A/B/A"
EXPECTED_LAYOUT = "built-in deterministic grid"
EXPECTED_PROXY_COUNTS = (25, 50, 100, 200)
M01_SCENE_SPECS = {
    "M01 Corridor A/B/A": ("M01 corridor_static + deterministic fillers", 100),
    "M01 Arena A/B/A": ("M01 arena_combat + deterministic fillers", 100),
    "M01 City A/B/A": ("M01 dense_city + deterministic fillers", 100),
}
EXPECTED_EFFECT_MODE = "lights"
EXPECTED_MAX_FPS = 240
EXPECTED_VSYNC = 0


def _loads(raw: bytes):
    try:
        return json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=canonical._pairs_no_duplicates,
            parse_constant=canonical._reject_constant,
        )
    except ValueError as exc:
        raise ValueError("invalid JSON: " + str(exc)) from None


def validate_document(document):
    """Validate harness provenance, then delegate to the canonical validator."""
    if not isinstance(document, dict):
        raise ValueError("document must be a JSON object")
    workload = document.get("workload")
    if not isinstance(workload, dict):
        raise ValueError("workload must be an object")
    scene = workload.get("scene")
    if scene == EXPECTED_SCENE:
        if workload.get("layout") != EXPECTED_LAYOUT:
            raise ValueError("workload.layout must be " + EXPECTED_LAYOUT)
        if workload.get("proxy_count") not in EXPECTED_PROXY_COUNTS:
            raise ValueError("workload.proxy_count must be one of 25/50/100/200")
    elif scene in M01_SCENE_SPECS:
        layout, count = M01_SCENE_SPECS[scene]
        if workload.get("layout") != layout:
            raise ValueError("workload.layout must be " + layout)
        if workload.get("proxy_count") != count:
            raise ValueError(f"workload.proxy_count must be {count} for {scene}")
    else:
        raise ValueError("workload.scene is not a supported harness scene")
    if workload.get("effect_mode") != EXPECTED_EFFECT_MODE:
        raise ValueError("workload.effect_mode must be " + EXPECTED_EFFECT_MODE)
    settings = document.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("settings must be an object")
    if settings.get("max_fps") != EXPECTED_MAX_FPS:
        raise ValueError(f"settings.max_fps must be {EXPECTED_MAX_FPS}")
    if settings.get("vsync_mode") != EXPECTED_VSYNC:
        raise ValueError(f"settings.vsync_mode must be {EXPECTED_VSYNC}")

    delegated = dict(document)
    delegated["workload"] = dict(workload, scene="Density Ladder", layout=EXPECTED_LAYOUT)
    try:
        result = canonical.validate_report(delegated)
    except canonical.ProfileError as exc:
        raise ValueError(str(exc)) from exc

    return {"status": "PASS", **result}


def main() -> int:
    payload = sys.stdin.buffer.read(canonical.MAX_BYTES + 1)
    if len(payload) > canonical.MAX_BYTES:
        print(json.dumps({"status": "FAIL", "reason": "profile input exceeds 8 MB limit"}))
        return 1
    try:
        result = validate_document(_loads(payload))
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

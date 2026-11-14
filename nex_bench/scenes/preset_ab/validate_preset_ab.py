#!/usr/bin/env python3
"""NEX M09 preset A/B/A validator.

Validates the harness provenance, then delegates every structural/aggregate
check to the canonical GPU profile validator with only the scene label
substituted. It never suppresses a check and never fabricates metrics.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gpu_profile"))

import validate_gpu_profile as canonical  # noqa: E402 - path bootstrap above

EXPECTED_SCENE = "Preset A/B/A"
EXPECTED_LAYOUT = "built-in deterministic grid"
EXPECTED_PROXY_COUNT = 200
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
    if workload.get("scene") != EXPECTED_SCENE:
        raise ValueError("workload.scene must be " + EXPECTED_SCENE)
    if workload.get("layout") != EXPECTED_LAYOUT:
        raise ValueError("workload.layout must be " + EXPECTED_LAYOUT)
    if workload.get("proxy_count") != EXPECTED_PROXY_COUNT:
        raise ValueError(f"workload.proxy_count must be {EXPECTED_PROXY_COUNT}")
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
    delegated["workload"] = dict(workload, scene="Density Ladder")
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

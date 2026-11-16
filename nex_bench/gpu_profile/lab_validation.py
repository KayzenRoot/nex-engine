"""Shared validation for NEX native lab profiles.

Both the M01/M09 preset harness and the M07 2D lab use the canonical
`nex_gpu_render_profile.v2` validator. This module owns only the lab-specific
provenance checks; structural and aggregate checks stay in the canonical
validator.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_gpu_profile as canonical  # noqa: E402 - path bootstrap above


def loads(raw: bytes):
    try:
        return json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=canonical._pairs_no_duplicates,
            parse_constant=canonical._reject_constant,
        )
    except ValueError as exc:
        raise ValueError("invalid JSON: " + str(exc)) from None


def validate_document(document, scene_specs, expected_effect_mode: str,
                      expected_max_fps: int, expected_vsync: int):
    if not isinstance(document, dict):
        raise ValueError("document must be a JSON object")
    workload = document.get("workload")
    if not isinstance(workload, dict):
        raise ValueError("workload must be an object")
    scene = workload.get("scene")
    if scene not in scene_specs:
        raise ValueError("workload.scene is not a supported harness scene")
    layout, counts = scene_specs[scene]
    if workload.get("layout") != layout:
        raise ValueError("workload.layout must be " + layout)
    if workload.get("proxy_count") not in counts:
        raise ValueError(f"workload.proxy_count must be one of {counts} for {scene}")
    if workload.get("effect_mode") != expected_effect_mode:
        raise ValueError("workload.effect_mode must be " + expected_effect_mode)
    settings = document.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("settings must be an object")
    if settings.get("max_fps") != expected_max_fps:
        raise ValueError(f"settings.max_fps must be {expected_max_fps}")
    if settings.get("vsync_mode") != expected_vsync:
        raise ValueError(f"settings.vsync_mode must be {expected_vsync}")
    delegated = dict(document)
    delegated["workload"] = dict(workload, scene="Density Ladder", layout="built-in deterministic grid")
    try:
        result = canonical.validate_report(delegated)
    except canonical.ProfileError as exc:
        raise ValueError(str(exc)) from exc
    return {"status": "PASS", **result}

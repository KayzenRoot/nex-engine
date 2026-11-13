#!/usr/bin/env python3
"""NEX M01-S05 Lighting Matrix validator.

The canonical v2 validator is intentionally scoped to the S04 Density Ladder
scene. This entry point validates the Lighting Matrix provenance and then
delegates every remaining structural/aggregate check to the same canonical
validator (single source of truth), substituting only the scene label for the
delegated call. It never suppresses a check and never fabricates metrics.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gpu_profile"))

import validate_gpu_profile as canonical  # noqa: E402 - path bootstrap above

EXPECTED_SCENE = "Lighting Matrix"
EXPECTED_LAYOUT = "built-in deterministic grid"


class LightingMatrixError(ValueError):
    """Raised when the document is not a valid Lighting Matrix observation."""


def _loads(raw: bytes):
    try:
        return json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=canonical._pairs_no_duplicates,
            parse_constant=canonical._reject_constant,
        )
    except (UnicodeDecodeError, ValueError) as exc:
        if isinstance(exc, LightingMatrixError):
            raise
        raise LightingMatrixError("invalid JSON: " + str(exc)) from None


def validate_document(document):
    """Validate Lighting Matrix provenance, then delegate to the canonical validator."""
    if not isinstance(document, dict):
        raise LightingMatrixError("document must be a JSON object")
    workload = document.get("workload")
    if not isinstance(workload, dict):
        raise LightingMatrixError("workload must be an object")
    if workload.get("scene") != EXPECTED_SCENE:
        raise LightingMatrixError("workload.scene must be " + EXPECTED_SCENE)
    if workload.get("layout") != EXPECTED_LAYOUT:
        raise LightingMatrixError("workload.layout must be " + EXPECTED_LAYOUT)

    delegated = dict(document)
    delegated["workload"] = dict(workload, scene="Density Ladder")
    try:
        result = canonical.validate_report(delegated)
    except canonical.ProfileError as exc:
        raise LightingMatrixError(str(exc)) from exc

    return {
        "status": "PASS",
        "run_id": result.get("run_id"),
        "run_status": result.get("run_status"),
        "source_sha": document.get("source_sha"),
        "workload": {
            "proxy_count": result.get("workload", {}).get("proxy_count"),
            "effect_mode": result.get("workload", {}).get("effect_mode"),
        },
        "observed_seconds": result.get("observed_seconds"),
        "one_percent_low_fps": result.get("one_percent_low_fps"),
        "series": result.get("series"),
    }


def main() -> int:
    payload = sys.stdin.buffer.read(canonical.MAX_BYTES + 1)
    if len(payload) > canonical.MAX_BYTES:
        print(json.dumps({"status": "FAIL", "reason": "profile input exceeds 8 MB limit"}))
        return 1
    try:
        result = validate_document(_loads(payload))
    except (LightingMatrixError, canonical.ProfileError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

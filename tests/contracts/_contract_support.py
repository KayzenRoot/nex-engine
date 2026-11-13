"""Shared helpers for the M04/M05 contract tests.

Kept private to the contract test package to avoid copying availability and
provenance fixtures into each new module test.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from test_m01_schema import strict_json_loads
from test_m02_render_contract import _resolve_refs

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "contracts"

METRIC_KEYS = (
    "gpu_render_time",
    "cpu_render_time",
    "draw_calls",
    "renderer_allocation_bytes",
)


def read_schema(module: str, filename: str) -> dict[str, Any]:
    raw = strict_json_loads((CONTRACTS / module / filename).read_text(encoding="utf-8"))
    return _resolve_refs(raw, raw.get("$defs", {}))


def read_manifest(module: str) -> dict[str, Any]:
    return strict_json_loads((CONTRACTS / module / "ownership.v1.json").read_text(encoding="utf-8"))


def unavailable_performance() -> dict[str, Any]:
    return {
        "measurement_status": "UNAVAILABLE",
        "frame_interval": {
            "status": "UNAVAILABLE",
            "provider": "SceneTree._process(delta)",
            "unavailable_reason": "contract fixture has no runtime",
        },
        "gpu_render_time": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
        "cpu_render_time": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
        "draw_calls": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
        "renderer_allocation_bytes": {"status": "UNAVAILABLE", "unavailable_reason": "no provider"},
    }


def unavailable_provenance() -> dict[str, Any]:
    return {
        "base_sha": "a" * 40,
        "head_sha": "b" * 40,
        "godot_version": "4.7.2-stable",
        "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
        "capture_mode": "windowed",
        "measurement_status": "UNAVAILABLE",
    }


def global_unavailable_errors(document: dict[str, Any]) -> list[str]:
    """Reject a MEASURED metric when the document-level status is UNAVAILABLE."""
    performance = document.get("performance")
    if not isinstance(performance, dict) or performance.get("measurement_status") != "UNAVAILABLE":
        return []
    errors: list[str] = []
    for key in METRIC_KEYS:
        metric = performance.get(key)
        if isinstance(metric, dict) and metric.get("status") == "MEASURED":
            errors.append(f"$.performance.{key}: global UNAVAILABLE forbids MEASURED metric")
    return errors


def provenance_evidence_errors(document: dict[str, Any]) -> list[str]:
    provenance = document.get("provenance")
    if not isinstance(provenance, dict):
        return []
    if provenance.get("measurement_status") == "MEASURED" and not provenance.get("evidence_uri"):
        return ["$.provenance.evidence_uri: required when provenance is MEASURED"]
    return []


def estimated_texture_bytes(textures: list[dict[str, Any]]) -> int:
    total = 0
    for texture in textures:
        pixels = int(texture["width_px"]) * int(texture["height_px"])
        size = pixels * 4
        if texture.get("mipmaps"):
            size = size * 4 // 3
        total += size
    return total

"""Shared helpers for NEX native runtime report builders."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "m09" / "tools"))

from common import load_json  # noqa: E402 - shared local tool module
from png_image import compare, read_png  # noqa: E402 - shared local tool module
from preset_report import load_capture, transform_run  # noqa: E402 - shared local tool module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pct(new: float, old: float) -> float:
    return round((new - old) / old * 100.0, 2)


def diff(first: Path, second: Path) -> dict:
    return compare(read_png(first), read_png(second), 2)


def load_manifest(path: Path, schema: str, source_sha: str, expected: int,
                  modes: tuple[str, ...] | None = None) -> dict:
    manifest = load_json(path)
    if manifest.get("schema_version") != schema:
        raise ValueError("runs manifest schema is invalid")
    if manifest.get("source_sha") != source_sha:
        raise ValueError("runs manifest source SHA is stale")
    runs = manifest.get("runs", [])
    if len(runs) != expected:
        raise ValueError(f"runs manifest must contain {expected} runs")
    if [entry.get("sequence") for entry in runs] != list(range(1, expected + 1)):
        raise ValueError("runs manifest sequence is invalid")
    if modes is not None and {entry.get("mode") for entry in runs} != set(modes):
        raise ValueError("runs manifest modes are incomplete")
    return manifest


def metrics(evidence: Path, manifest: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for entry in manifest["runs"]:
        capture = load_capture(evidence, entry["run_id"], entry["scene"], entry["layout"],
                               int(entry["proxy_count"]), include_allocation=True)
        result[entry["mode"]] = transform_run(entry, capture, include_allocation=True)
    return result


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

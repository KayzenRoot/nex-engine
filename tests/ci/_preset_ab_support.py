"""Shared helpers for the NEX M09 benchmark test modules."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def load_builder(module_name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_sha256sums(case: Any, evidence: Path, expected_count: int) -> None:
    lines = [line for line in (evidence / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    case.assertEqual(expected_count, len(lines))
    for line in lines:
        digest, name = line.split(" *", 1)
        path = evidence / name
        with case.subTest(name=name):
            case.assertTrue(path.is_file())
            case.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())


def assert_no_fabricated(case: Any, text: str, forbidden: tuple[str, ...]) -> None:
    for phrase in forbidden:
        with case.subTest(phrase=phrase):
            case.assertNotIn(phrase, text)


def assert_captures(case: Any, evidence: Path, manifest: dict[str, Any], default_count: int | None = None) -> None:
    for entry in manifest["runs"]:
        with case.subTest(run=entry["run_id"]):
            document = json.loads((evidence / f"gpu_profile_{entry['run_id']}.json").read_text(encoding="utf-8"))
            case.assertEqual("COMPLETE", document["run_status"])
            case.assertEqual(manifest["source_sha"], document["source_sha"])
            case.assertEqual("Preset A/B/A", document["workload"]["scene"])
            expected_count = entry.get("proxy_count", default_count)
            if expected_count is not None:
                case.assertEqual(expected_count, document["workload"]["proxy_count"])
            case.assertEqual("lights", document["workload"]["effect_mode"])
            case.assertEqual(240, document["settings"]["max_fps"])
            case.assertEqual(0, document["settings"]["vsync_mode"])


def assert_validations(case: Any, evidence: Path, manifest: dict[str, Any]) -> None:
    for entry in manifest["runs"]:
        with case.subTest(run=entry["run_id"]):
            validation = json.loads((evidence / f"gpu_profile_{entry['run_id']}.json.validation.json").read_text(encoding="utf-8"))
            case.assertEqual("PASS", validation["status"])

"""Shared helpers for the NEX M09 benchmark test modules."""
from __future__ import annotations

import hashlib
import importlib.util
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

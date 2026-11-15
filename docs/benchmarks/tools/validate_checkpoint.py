#!/usr/bin/env python3
"""Validate the canonical checkpoint schema and provenance coherence."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKPOINT = REPO_ROOT / ".engineering" / "CHECKPOINT.json"
INDEX = REPO_ROOT / "docs" / "benchmarks" / "provenance-index.v1.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_TOP = ("schemaVersion", "project", "status", "mainObservedSha", "phase", "nextLegalAction")
ADMISSION_BLOCKS = (
    "m01M02BoundedAdmission",
    "m03BoundedAdmission",
    "m04M05BoundedAdmission",
    "m06M09BoundedAdmission",
)


def _load(path: Path) -> Any:
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)

    def constant(token):
        raise ValueError("non-finite JSON: " + token)

    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def _provenance_blocks(checkpoint: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        value for value in checkpoint.values()
        if isinstance(value, dict)
        and isinstance(value.get("pr"), int)
        and isinstance(value.get("protectedMergeSha"), str)
    ]


def validate(checkpoint: dict[str, Any], index: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in checkpoint:
            errors.append(f"missing top-level field: {key}")
    if checkpoint.get("project") != "KayzenRoot/nex-engine":
        errors.append("project must be KayzenRoot/nex-engine")
    if not SHA.match(str(checkpoint.get("mainObservedSha", ""))):
        errors.append("mainObservedSha must be a 40-hex Git SHA")
    status = str(checkpoint.get("status", ""))
    if "BOUNDED_ADMITTED" not in status or ("NOT_ADMITTED" not in status and "ALL_PARENTS" not in status):
        errors.append("status must record BOUNDED_ADMITTED and either NOT_ADMITTED or ALL_PARENTS")
    for key, value in checkpoint.items():
        if not isinstance(value, dict):
            continue
        if "INDEPENDENT_APPROVED" in str(value.get("audit", "")):
            errors.append(f"{key}: false independent approval")
        if isinstance(value.get("pr"), int):
            merge = value.get("protectedMergeSha", value.get("mergeSha"))
            if not isinstance(merge, str) or not SHA.match(merge):
                errors.append(f"{key}: pr without a valid merge SHA")
        elif "protectedMergeSha" in value:
            if not isinstance(value.get("implementationPr"), int):
                errors.append(f"{key}: protectedMergeSha without pr")
    blocks = _provenance_blocks(checkpoint)
    merges = [block["protectedMergeSha"] for block in blocks]
    if len(merges) != len(set(merges)):
        errors.append("protectedMergeSha values must be unique")
    for key in ADMISSION_BLOCKS:
        block = checkpoint.get(key)
        if not isinstance(block, dict):
            errors.append(f"missing admission block: {key}")
            continue
        not_admitted = block.get("notAdmitted")
        if not isinstance(not_admitted, list) or not all(isinstance(item, str) for item in not_admitted):
            errors.append(f"{key}: notAdmitted must be a string list")
        statuses = [value for name, value in block.items() if "Status" in name or name == "status"]
        if not statuses or not all("BOUNDED_ADMITTED" in str(value) for value in statuses):
            errors.append(f"{key}: admitted statuses must contain BOUNDED_ADMITTED")
    if index is not None:
        summary = index.get("summary", {})
        if summary.get("entries") != len(blocks):
            errors.append("provenance index entry count does not match the checkpoint")
        if blocks and summary.get("max_pr") != max(block["pr"] for block in blocks):
            errors.append("provenance index max PR does not match the checkpoint")
        if len({block["pr"] for block in blocks}) != len(blocks):
            errors.append("checkpoint PR numbers must be unique")
    return errors


def main(argv: list[str]) -> int:
    if argv != ["--check"]:
        print("usage: validate_checkpoint.py --check")
        return 2
    checkpoint = _load(CHECKPOINT)
    index = _load(INDEX)
    errors = validate(checkpoint, index)
    if errors:
        for error in errors:
            print("CHECKPOINT_SCHEMA_FAIL: " + error)
        return 1
    print(f"CHECKPOINT_SCHEMA_OK: {len(_provenance_blocks(checkpoint))} provenance blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

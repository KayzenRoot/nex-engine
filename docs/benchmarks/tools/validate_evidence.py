#!/usr/bin/env python3
"""Validate every committed SHA256SUMS.txt evidence bundle.

The validator hashes the committed working-tree bytes and accepts the LF and
CRLF variants of the same content, because historical Windows bundles were
generated with CRLF before Git normalized the files to LF.

Usage:
  python validate_evidence.py --check
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKIP_PARTS = {".git", "node_modules", ".godot"}
HEX = set("0123456789abcdef")


def _digests(path: Path) -> set[str]:
    data = path.read_bytes()
    digests = {hashlib.sha256(data).hexdigest()}
    if b"\r\n" in data:
        digests.add(hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest())
    else:
        digests.add(hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest())
    return digests


def _parse(line: str) -> tuple[str, str] | None:
    for separator in (" *", "  "):
        if separator in line:
            digest, name = line.split(separator, 1)
            if len(digest) == 64 and set(digest) <= HEX and name:
                return digest, name
    return None


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    bundles = sorted(path for path in root.rglob("SHA256SUMS.txt") if not (set(path.parts) & SKIP_PARTS))
    entries = 0
    for sums in bundles:
        for number, line in enumerate(sums.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            parsed = _parse(line)
            if parsed is None:
                errors.append(f"{sums.relative_to(root)}:{number}: malformed line")
                continue
            digest, name = parsed
            entries += 1
            target = next((path for path in (sums.parent / name, root / name) if path.is_file()), None)
            if target is None:
                errors.append(f"{sums.relative_to(root)}:{number}: missing {name}")
                continue
            if digest not in _digests(target):
                errors.append(f"{sums.relative_to(root)}:{number}: digest mismatch {name}")
    print(f"EVIDENCE_SUMS_SCAN: {len(bundles)} bundles / {entries} entries")
    return errors


def main(argv: list[str]) -> int:
    if argv not in ([], ["--check"]):
        print("usage: validate_evidence.py [--check]")
        return 2
    errors = validate(REPO)
    if errors:
        for error in errors[:50]:
            print("ERROR: " + error)
        if len(errors) > 50:
            print(f"... {len(errors) - 50} more")
        return 1
    print("EVIDENCE_SUMS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

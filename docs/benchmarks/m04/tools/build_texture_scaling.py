#!/usr/bin/env python3
"""Measure deterministic texture scaling for the M04 stone_wet material.

1K is generated natively; 2K/4K are nearest-neighbour upscales of the 1K
reference so the report stays reproducible without multi-minute pixel loops.
Textures are generated in memory only; the report records bytes and SHA-256.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_material_kit as kit  # noqa: E402 - shared deterministic primitives

REPO = Path(__file__).resolve().parents[4]
OUTPUT = REPO / "docs" / "benchmarks" / "m04"
REPORT_JSON = OUTPUT / "texture-scaling.v1.json"
REPORT_MD = OUTPUT / "TEXTURE-SCALING.md"
SPEC = {"id": "stone_wet", "base": (0.38, 0.40, 0.43), "roughness": 0.55, "metallic": 0.0,
        "noise": 0.12, "seed": 101, "pattern": "grain", "emission": None, "emission_energy": 0.0}
SOURCE = 1024
SIZES = (1024, 2048, 4096)
SLOTS = ("albedo", "normal", "orm")


def _raw(size: int, slot: str) -> bytes:
    kit.SIZE = size
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            if slot == "albedo":
                rows.extend(kit._albedo_pixel(x, y, SPEC))
            elif slot == "normal":
                rows.extend(kit._normal_pixel(x, y, SPEC))
            else:
                rows.extend(kit._orm_pixel(x, y, SPEC))
    return bytes(rows)


def _encode(size: int, raw: bytes) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + kit._chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) \
        + kit._chunk(b"IDAT", kit._stored_zlib(raw)) + kit._chunk(b"IEND", b"")


def _upscale(raw: bytes, source: int, target: int) -> bytes:
    rows = bytearray()
    for y in range(target):
        source_y = y * source // target
        rows.append(0)
        row_start = source_y * (source * 4 + 1) + 1
        for x in range(target):
            source_x = x * source // target
            offset = row_start + source_x * 4
            rows.extend(raw[offset:offset + 4])
    return bytes(rows)


def _decoded_bytes(size: int) -> int:
    total = 0
    level = size
    while level >= 1:
        total += level * level * 4
        level //= 2
    return total


def build_report() -> dict[str, Any]:
    native = {slot: _raw(SOURCE, slot) for slot in SLOTS}
    cells = []
    for size in SIZES:
        maps = []
        for slot in SLOTS:
            if size == 4096 and slot != "albedo":
                maps.append({"slot": slot, "status": "NOT_GENERATED", "reason": "4K non-albedo omitted to bound memory"})
                continue
            raw = native[slot] if size == SOURCE else _upscale(native[slot], SOURCE, size)
            data = _encode(size, raw)
            maps.append({
                "slot": slot,
                "status": "GENERATED_IN_MEMORY",
                "committed": False,
                "detail": "native" if size == SOURCE else f"nearest_upscale_from_{SOURCE}",
                "width_px": size,
                "height_px": size,
                "png_bytes": len(data),
                "decoded_bytes": _decoded_bytes(size),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        cells.append({"size_px": size, "maps": maps})
    return {
        "schema_version": "m04_texture_scaling.v1",
        "material_id": SPEC["id"],
        "generated_in_memory_only": True,
        "source_size_px": SOURCE,
        "cells": cells,
        "verdict": "SCALING_DERIVED",
        "observations": [
            "1K is generated natively for albedo, normal and ORM",
            "2K is a nearest-neighbour upscale of the 1K reference; 4K albedo is a 4x upscale",
            "decoded bytes include the full mip chain (4/3 of the base level)",
            "PNG uses stored deflate; compression is a separate M11 import concern",
        ],
        "limitations": [
            "2K/4K do not contain native high-frequency detail; they are scaling probes",
            "no BC/BPTC/VRAM compression or GPU sampling is measured",
            "large textures are not committed; only hashes and sizes are evidence",
            "single material; no cross-material atlas packing",
            "no visual quality or FPS claim",
        ],
        "runs": len(cells),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M04 · Texture scaling",
        "",
        "**Status:** `SCALING_DERIVED / IN_MEMORY / NO_VRAM_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte nativa:** {report['source_size_px']}×{report['source_size_px']} · 2K/4K são upscales nearest-neighbour documentados.",
        "",
        "| Resolução | Mapa | Detalhe | PNG bytes | Decodificado | SHA-256 |",
        "|---:|---|---|---:|---:|---|",
    ]
    for cell in report["cells"]:
        for entry in cell["maps"]:
            if entry["status"] != "GENERATED_IN_MEMORY":
                lines.append(f"| {cell['size_px']} | {entry['slot']} | — | — | — | `{entry['status']}` |")
                continue
            lines.append(
                f"| {cell['size_px']} | {entry['slot']} | {entry['detail']} | {entry['png_bytes']} | "
                f"{entry['decoded_bytes']} | `{entry['sha256'][:16]}…` |"
            )
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m04/tools/build_texture_scaling.py`; não é medição de VRAM.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    report = build_report()
    rendered_json = render_json(report)
    rendered_md = render_markdown(report)
    if argv == ["--check"]:
        if not REPORT_JSON.is_file() or REPORT_JSON.read_text(encoding="utf-8") != rendered_json:
            print("M04_TEXTURE_SCALING_CHECK_FAIL: JSON is stale")
            return 1
        if not REPORT_MD.is_file() or REPORT_MD.read_text(encoding="utf-8") != rendered_md:
            print("M04_TEXTURE_SCALING_CHECK_FAIL: Markdown is stale")
            return 1
        print("M04_TEXTURE_SCALING_CHECK_PASS: 3 sizes")
        return 0
    if argv:
        print("usage: builder [--check]")
        return 2
    REPORT_JSON.write_text(rendered_json, encoding="utf-8")
    REPORT_MD.write_text(rendered_md, encoding="utf-8")
    print("M04_TEXTURE_SCALING_WRITE_PASS: 3 sizes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

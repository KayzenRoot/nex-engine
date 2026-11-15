#!/usr/bin/env python3
"""Generate the deterministic M04 procedural material kit.

The kit is data only: 12 PNG reference textures, 4 StandardMaterial3D
resources and one material.v1 observation. Nothing is rendered or decoded by
Godot in this builder; the committed headless-load log is separate evidence.

Usage:
  python build_material_kit.py
  python build_material_kit.py --check
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
KIT = REPO / "nex_modules" / "materials" / "kit"
TEXTURES = KIT / "textures"
MATERIALS = KIT / "materials"
OBSERVATION = KIT / "kit.v1.json"
REPORT = REPO / "docs" / "benchmarks" / "m04" / "MATERIAL-KIT.md"
SIZE = 128
BASE_SHA = "99437b22e94a6494eaef801872bb8fd0c79c0f1a"
CAPTURED_AT = "2026-11-15T00:00:00Z"
EVIDENCE_URI = "nex_modules/materials/kit/evidence/headless-load-2026-11-15.log"

MATERIALS_SPEC = (
    {
        "id": "concrete_floor",
        "base": (0.55, 0.55, 0.57),
        "roughness": 0.85,
        "metallic": 0.0,
        "noise": 0.08,
        "seed": 11,
        "pattern": "grain",
        "emission": None,
        "emission_energy": 0.0,
    },
    {
        "id": "brushed_metal",
        "base": (0.62, 0.64, 0.68),
        "roughness": 0.35,
        "metallic": 1.0,
        "noise": 0.05,
        "seed": 23,
        "pattern": "streak",
        "emission": None,
        "emission_energy": 0.0,
    },
    {
        "id": "oak_wood",
        "base": (0.45, 0.31, 0.18),
        "roughness": 0.70,
        "metallic": 0.0,
        "noise": 0.10,
        "seed": 37,
        "pattern": "bands",
        "emission": None,
        "emission_energy": 0.0,
    },
    {
        "id": "emissive_trim",
        "base": (0.10, 0.10, 0.12),
        "roughness": 0.40,
        "metallic": 0.0,
        "noise": 0.03,
        "seed": 41,
        "pattern": "grain",
        "emission": (0.10, 0.80, 0.90),
        "emission_energy": 2.5,
    },
)
SLOTS = ("albedo", "normal", "orm")


def _hash(x: int, y: int, seed: int) -> float:
    value = (x * 374761393 + y * 668265263 + seed * 1442695040888963407) & 0xFFFFFFFF
    value = ((value ^ (value >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((value ^ (value >> 16)) & 0xFFFFFFFF) / 4294967295.0


def _smooth(value: float) -> float:
    return value * value * (3.0 - 2.0 * value)


def _value_noise(x: int, y: int, seed: int, scale: int) -> float:
    gx, gy = x // scale, y // scale
    fx, fy = (x % scale) / scale, (y % scale) / scale
    sx, sy = _smooth(fx), _smooth(fy)
    top = _hash(gx, gy, seed) * (1.0 - sx) + _hash(gx + 1, gy, seed) * sx
    bottom = _hash(gx, gy + 1, seed) * (1.0 - sx) + _hash(gx + 1, gy + 1, seed) * sx
    return top * (1.0 - sy) + bottom * sy


def _height(x: int, y: int, spec: dict[str, Any]) -> float:
    seed = int(spec["seed"])
    pattern = spec["pattern"]
    noise = _value_noise(x, y, seed, 8) * 0.6 + _value_noise(x, y, seed + 1, 4) * 0.4
    if pattern == "streak":
        noise = noise * 0.35 + _hash(0, y, seed) * 0.65
    elif pattern == "bands":
        noise = noise * 0.55 + _hash(x // 6, 0, seed) * 0.45
    return noise


def _albedo_pixel(x: int, y: int, spec: dict[str, Any]) -> tuple[int, int, int, int]:
    height = _height(x, y, spec)
    delta = (height - 0.5) * float(spec["noise"]) * 2.0
    rgb = []
    for channel in spec["base"]:
        value = max(0.0, min(1.0, float(channel) + delta))
        rgb.append(round(value * 255.0))
    return (rgb[0], rgb[1], rgb[2], 255)


def _normal_pixel(x: int, y: int, spec: dict[str, Any]) -> tuple[int, int, int, int]:
    left = _height((x - 1) % SIZE, y, spec)
    right = _height((x + 1) % SIZE, y, spec)
    up = _height(x, (y - 1) % SIZE, spec)
    down = _height(x, (y + 1) % SIZE, spec)
    nx, ny, nz = (left - right) * 2.0, (up - down) * 2.0, 1.0
    length = max(0.0001, (nx * nx + ny * ny + nz * nz) ** 0.5)
    return (
        round((nx / length * 0.5 + 0.5) * 255.0),
        round((ny / length * 0.5 + 0.5) * 255.0),
        round((nz / length * 0.5 + 0.5) * 255.0),
        255,
    )


def _orm_pixel(x: int, y: int, spec: dict[str, Any]) -> tuple[int, int, int, int]:
    height = _height(x, y, spec)
    occlusion = 1.0 - 0.15 * (1.0 - height)
    roughness = max(0.0, min(1.0, float(spec["roughness"]) + (height - 0.5) * 0.08))
    metallic = float(spec["metallic"])
    return (
        round(occlusion * 255.0),
        round(roughness * 255.0),
        round(metallic * 255.0),
        255,
    )


def _png(width: int, height: int, pixel) -> bytes:
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend(pixel(x, y))
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) \
        + _chunk(b"IDAT", _stored_zlib(bytes(rows))) + _chunk(b"IEND", b"")


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _stored_zlib(raw: bytes) -> bytes:
    """Deflate with stored blocks: byte-identical across platforms and zlib versions."""
    output = bytearray(b"\x78\x01")
    offset = 0
    while offset < len(raw):
        block = raw[offset:offset + 65535]
        final = 1 if offset + len(block) >= len(raw) else 0
        output.append(final)
        output.extend(struct.pack("<HH", len(block), len(block) ^ 0xFFFF))
        output.extend(block)
        offset += len(block)
    output.extend(struct.pack(">I", zlib.adler32(raw) & 0xFFFFFFFF))
    return bytes(output)


def _tres(spec: dict[str, Any]) -> str:
    material_id = spec["id"]
    lines = [
        '[gd_resource type="StandardMaterial3D" load_steps=4 format=3]',
        "",
        f'[ext_resource type="Texture2D" path="res://textures/{material_id}_albedo.png" id="1"]',
        f'[ext_resource type="Texture2D" path="res://textures/{material_id}_normal.png" id="2"]',
        f'[ext_resource type="Texture2D" path="res://textures/{material_id}_orm.png" id="3"]',
        "",
        "[resource]",
        f'resource_name = "{material_id}"',
        'albedo_texture = ExtResource("1")',
        f'metallic = {float(spec["metallic"]):.2f}',
        f'roughness = {float(spec["roughness"]):.2f}',
        "normal_enabled = true",
        'normal_texture = ExtResource("2")',
        'orm_texture = ExtResource("3")',
    ]
    if spec["emission"] is not None:
        red, green, blue = spec["emission"]
        lines.extend([
            "emission_enabled = true",
            f"emission = Color({red:.2f}, {green:.2f}, {blue:.2f}, 1)",
            f'emission_energy_multiplier = {float(spec["emission_energy"]):.2f}',
        ])
    return "\n".join(lines) + "\n"


def _texture_entries(spec: dict[str, Any], payloads: dict[str, bytes]) -> list[dict[str, Any]]:
    entries = []
    for slot in SLOTS:
        data = payloads[f"{spec['id']}_{slot}.png"]
        entries.append({
            "slot": slot,
            "uri": f"res://textures/{spec['id']}_{slot}.png",
            "sha256": hashlib.sha256(data).hexdigest(),
            "width_px": SIZE,
            "height_px": SIZE,
            "mipmaps": True,
            "srgb": slot == "albedo",
        })
    return entries


def build_assets() -> tuple[dict[str, bytes], dict[str, str]]:
    textures: dict[str, bytes] = {}
    materials: dict[str, str] = {}
    for spec in MATERIALS_SPEC:
        textures[f"{spec['id']}_albedo.png"] = _png(SIZE, SIZE, lambda x, y, s=spec: _albedo_pixel(x, y, s))
        textures[f"{spec['id']}_normal.png"] = _png(SIZE, SIZE, lambda x, y, s=spec: _normal_pixel(x, y, s))
        textures[f"{spec['id']}_orm.png"] = _png(SIZE, SIZE, lambda x, y, s=spec: _orm_pixel(x, y, s))
        materials[f"{spec['id']}.tres"] = _tres(spec)
    return textures, materials


def build_observation(textures: dict[str, bytes]) -> dict[str, Any]:
    materials = []
    for spec in MATERIALS_SPEC:
        emission = spec["emission"] or (0.0, 0.0, 0.0)
        materials.append({
            "material_id": spec["id"],
            "shader_id": "StandardMaterial3D",
            "surface": {
                "albedo_rgba": [float(spec["base"][0]), float(spec["base"][1]), float(spec["base"][2]), 1.0],
                "metallic": float(spec["metallic"]),
                "roughness": float(spec["roughness"]),
                "emission_rgba": [float(emission[0]), float(emission[1]), float(emission[2]), 1.0],
                "emission_energy": float(spec["emission_energy"]),
                "normal_strength": 1.0,
                "occlusion_strength": 1.0,
            },
            "alpha_mode": "opaque",
            "cull_mode": "back",
            "quality_variant": "high",
            "textures": _texture_entries(spec, textures),
        })
    unavailable = {"status": "UNAVAILABLE", "unavailable_reason": "kit generation is headless; nothing is rendered"}
    return {
        "schema_version": "material.v1",
        "observation_id": "m04-procedural-kit.v1",
        "captured_at_utc": CAPTURED_AT,
        "materials": materials,
        "texture_budget": {
            "max_texture_count": 512,
            "max_texture_bytes": 268435456,
            "atlas_size": 4096,
            "orm_packed": True,
        },
        "performance": {
            "measurement_status": "UNAVAILABLE",
            "frame_interval": {
                "status": "UNAVAILABLE",
                "provider": "SceneTree._process(delta)",
                "unavailable_reason": "kit generation is headless; nothing is rendered",
            },
            "gpu_render_time": unavailable,
            "cpu_render_time": unavailable,
            "draw_calls": unavailable,
            "renderer_allocation_bytes": unavailable,
        },
        "provenance": {
            "base_sha": BASE_SHA,
            "head_sha": BASE_SHA,
            "godot_version": "4.7.2-stable",
            "hardware": {
                "gpu_model": "NVIDIA GeForce RTX 5050",
                "driver_version": "NVIDIA 617.14",
            },
            "capture_mode": "headless",
            "measurement_status": "UNAVAILABLE",
            "evidence_uri": EVIDENCE_URI,
        },
    }


def render_markdown(observation: dict[str, Any]) -> str:
    lines = [
        "# NEX M04 · Procedural material kit",
        "",
        "**Status:** `REFERENCE_KIT / NON_RENDERING / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Base:** `{BASE_SHA}` · **Godot:** `{observation['provenance']['godot_version']}`",
        "",
        "| Material | Albedo | Metallic | Roughness | Emission | Textures |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for material in observation["materials"]:
        surface = material["surface"]
        emission = surface["emission_energy"]
        lines.append(
            f"| {material['material_id']} | {surface['albedo_rgba'][0]:.2f}/"
            f"{surface['albedo_rgba'][1]:.2f}/{surface['albedo_rgba'][2]:.2f} | "
            f"{surface['metallic']:.2f} | {surface['roughness']:.2f} | {emission:.2f} | "
            f"{len(material['textures'])} |"
        )
    lines.extend([
        "",
        "## O que é",
        "",
        "- 12 texturas PNG determinísticas (albedo, normal, ORM) em 128×128, geradas sem rendering.",
        "- 4 materiais `StandardMaterial3D` em `.tres`, carregados headless por `ResourceLoader`.",
        "- Uma observação `material.v1` com SHA-256 de cada textura e orçamento declarado.",
        "",
        "## Limitações",
        "",
        "- Kit de referência: não é arte de produção nem prova de qualidade visual.",
        "- Sem shader customizado, sem compilação de shader, sem renderer, sem cena ou runtime.",
        "- Texturas não são comprimidas nem importadas para um pipeline de build; o log headless cobre apenas o carregamento local.",
        "- Nenhum FPS, frame-time, VRAM ou ganho é alegado.",
        "",
        "Gerado por `docs/benchmarks/m04/tools/build_material_kit.py`; `--check` reproduz bytes e SHA-256.",
        "",
    ])
    return "\n".join(lines)


def _outputs() -> dict[Path, bytes]:
    textures, materials = build_assets()
    observation = build_observation(textures)
    outputs: dict[Path, bytes] = {}
    for name, data in textures.items():
        outputs[TEXTURES / name] = data
    for name, text in materials.items():
        outputs[MATERIALS / name] = text.encode("utf-8")
    outputs[OBSERVATION] = (json.dumps(observation, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    outputs[REPORT] = render_markdown(observation).encode("utf-8")
    return outputs


def main(argv: list[str]) -> int:
    outputs = _outputs()
    if argv == ["--check"]:
        for path, expected in outputs.items():
            if not path.is_file() or path.read_bytes() != expected:
                print(f"M04_MATERIAL_KIT_CHECK_FAIL: stale or missing {path.relative_to(REPO)}")
                return 1
        print(f"M04_MATERIAL_KIT_CHECK_PASS: {len(MATERIALS_SPEC)} materials / {len(MATERIALS_SPEC) * len(SLOTS)} textures")
        return 0
    if argv:
        print("usage: builder [--check]")
        return 2
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"M04_MATERIAL_KIT_WRITE_PASS: {len(MATERIALS_SPEC)} materials / {len(MATERIALS_SPEC) * len(SLOTS)} textures")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

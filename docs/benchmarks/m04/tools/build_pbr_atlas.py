#!/usr/bin/env python3
"""Generate the M04 PBR reference atlas (8 materials, 256x256).

Reuses the deterministic texture primitives from build_material_kit.py. The
atlas is a self-contained Godot project used by the native material gallery.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_material_kit as kit  # noqa: E402 - shared deterministic primitives

REPO = Path(__file__).resolve().parents[4]
ATLAS = REPO / "nex_modules" / "materials" / "atlas"
TEXTURES = ATLAS / "textures"
MATERIALS = ATLAS / "materials"
OBSERVATION = ATLAS / "atlas.v1.json"
REPORT = REPO / "docs" / "benchmarks" / "m04" / "PBR-ATLAS.md"
SIZE = 256
BASE_SHA = "e09cce2f4332e00a0f51eacb346f5763fe228db9"
CAPTURED_AT = "2026-11-15T00:00:00Z"
EVIDENCE_URI = "nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m04-gallery/SESSION-FACTS.txt"
SLOTS = ("albedo", "normal", "orm")
kit.SIZE = SIZE

MATERIALS_SPEC = (
    {"id": "stone_wet", "base": (0.38, 0.40, 0.43), "roughness": 0.55, "metallic": 0.0, "noise": 0.12, "seed": 101, "pattern": "grain", "emission": None, "emission_energy": 0.0},
    {"id": "brushed_metal", "base": (0.62, 0.64, 0.68), "roughness": 0.30, "metallic": 1.0, "noise": 0.05, "seed": 102, "pattern": "streak", "emission": None, "emission_energy": 0.0},
    {"id": "oak_wood", "base": (0.45, 0.31, 0.18), "roughness": 0.70, "metallic": 0.0, "noise": 0.10, "seed": 103, "pattern": "bands", "emission": None, "emission_energy": 0.0},
    {"id": "cloth_crimson", "base": (0.38, 0.08, 0.09), "roughness": 0.90, "metallic": 0.0, "noise": 0.07, "seed": 104, "pattern": "grain", "emission": None, "emission_energy": 0.0},
    {"id": "skin_pale", "base": (0.72, 0.58, 0.50), "roughness": 0.50, "metallic": 0.0, "noise": 0.04, "seed": 105, "pattern": "grain", "emission": None, "emission_energy": 0.0},
    {"id": "terrain_earth", "base": (0.22, 0.17, 0.12), "roughness": 0.95, "metallic": 0.0, "noise": 0.14, "seed": 106, "pattern": "grain", "emission": None, "emission_energy": 0.0},
    {"id": "foliage_deep", "base": (0.12, 0.30, 0.12), "roughness": 0.80, "metallic": 0.0, "noise": 0.10, "seed": 107, "pattern": "grain", "emission": None, "emission_energy": 0.0},
    {"id": "water_clear", "base": (0.08, 0.22, 0.30), "roughness": 0.12, "metallic": 0.15, "noise": 0.03, "seed": 108, "pattern": "grain", "emission": None, "emission_energy": 0.0},
)


def _png(pixel) -> bytes:
    return kit._png(SIZE, SIZE, pixel)


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
        textures[f"{spec['id']}_albedo.png"] = _png(lambda x, y, s=spec: kit._albedo_pixel(x, y, s))
        textures[f"{spec['id']}_normal.png"] = _png(lambda x, y, s=spec: kit._normal_pixel(x, y, s))
        textures[f"{spec['id']}_orm.png"] = _png(lambda x, y, s=spec: kit._orm_pixel(x, y, s))
        materials[f"{spec['id']}.tres"] = kit._tres(spec)
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
            "alpha_mode": "blend" if spec["id"] == "water_clear" else "opaque",
            "cull_mode": "back",
            "quality_variant": "high",
            "textures": _texture_entries(spec, textures),
        })
    unavailable = {"status": "UNAVAILABLE", "unavailable_reason": "atlas generation is headless; nothing is rendered"}
    return {
        "schema_version": "material.v1",
        "observation_id": "m04-pbr-atlas.v1",
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
            "frame_interval": {"status": "UNAVAILABLE", "provider": "SceneTree._process(delta)", "unavailable_reason": "atlas generation is headless"},
            "gpu_render_time": unavailable,
            "cpu_render_time": unavailable,
            "draw_calls": unavailable,
            "renderer_allocation_bytes": unavailable,
        },
        "provenance": {
            "base_sha": BASE_SHA,
            "head_sha": BASE_SHA,
            "godot_version": "4.7.2-stable",
            "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "NVIDIA 617.14"},
            "capture_mode": "headless",
            "measurement_status": "UNAVAILABLE",
            "evidence_uri": EVIDENCE_URI,
        },
    }


def render_markdown(observation: dict[str, Any]) -> str:
    lines = [
        "# NEX M04 · PBR reference atlas",
        "",
        "**Status:** `REFERENCE_ATLAS / NATIVE_GALLERY / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Base:** `{BASE_SHA}` · **Godot:** `{observation['provenance']['godot_version']}` · **Resolução:** {SIZE}×{SIZE}",
        "",
        "| Material | Albedo | Metallic | Roughness | Texturas |",
        "|---|---:|---:|---:|---:|",
    ]
    for material in observation["materials"]:
        surface = material["surface"]
        lines.append(
            f"| {material['material_id']} | {surface['albedo_rgba'][0]:.2f}/"
            f"{surface['albedo_rgba'][1]:.2f}/{surface['albedo_rgba'][2]:.2f} | "
            f"{surface['metallic']:.2f} | {surface['roughness']:.2f} | {len(material['textures'])} |"
        )
    lines.extend([
        "",
        "## O que é",
        "",
        "- 24 texturas PNG determinísticas (albedo, normal, ORM) em 256×256, geradas sem rendering.",
        "- 8 materiais `StandardMaterial3D` em `.tres`, carregados pela galeria nativa.",
        "- Uma observação `material.v1` com SHA-256 de cada textura e orçamento declarado.",
        "",
        "## Limitações",
        "",
        "- Atlas de referência, não arte de produção nem prova de qualidade visual.",
        "- Sem compressão BC/BPTC, atlas packing ou pipeline de import/cook.",
        "- Sem paridade com PoE2; materiais e texturas são originais.",
        "- Nenhum FPS, frame-time, VRAM ou ganho é alegado.",
        "",
        "Gerado por `docs/benchmarks/m04/tools/build_pbr_atlas.py`; `--check` reproduz bytes e SHA-256.",
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
                print(f"M04_PBR_ATLAS_CHECK_FAIL: stale or missing {path.relative_to(REPO)}")
                return 1
        print(f"M04_PBR_ATLAS_CHECK_PASS: {len(MATERIALS_SPEC)} materials / {len(MATERIALS_SPEC) * len(SLOTS)} textures")
        return 0
    if argv:
        print("usage: builder [--check]")
        return 2
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"M04_PBR_ATLAS_WRITE_PASS: {len(MATERIALS_SPEC)} materials / {len(MATERIALS_SPEC) * len(SLOTS)} textures")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

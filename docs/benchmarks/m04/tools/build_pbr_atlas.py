#!/usr/bin/env python3
"""Generate the M04 PBR reference atlas (8 materials, 256x256).

Reuses the deterministic texture primitives, observation builder and Markdown
renderer from build_material_kit.py; only the material specs and paths differ.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

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

kit.SIZE = SIZE
kit.MATERIALS_SPEC = MATERIALS_SPEC
kit.BASE_SHA = BASE_SHA
kit.CAPTURED_AT = CAPTURED_AT
kit.EVIDENCE_URI = EVIDENCE_URI


def _outputs() -> dict[Path, bytes]:
    textures, materials = kit.build_assets()
    observation = kit.build_observation(textures)
    observation["observation_id"] = "m04-pbr-atlas.v1"
    outputs: dict[Path, bytes] = {}
    for name, data in textures.items():
        outputs[TEXTURES / name] = data
    for name, text in materials.items():
        outputs[MATERIALS / name] = text.encode("utf-8")
    outputs[OBSERVATION] = (json.dumps(observation, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    outputs[REPORT] = kit.render_markdown(
        observation,
        title="NEX M04 · PBR reference atlas",
        status="REFERENCE_ATLAS / NATIVE_GALLERY / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT",
        bullets=[
            "- 24 texturas PNG determinísticas (albedo, normal, ORM) em 256×256, geradas sem rendering.",
            "- 8 materiais `StandardMaterial3D` em `.tres`, carregados pela galeria nativa.",
            "- Uma observação `material.v1` com SHA-256 de cada textura e orçamento declarado.",
        ],
        limitations=[
            "- Atlas de referência, não arte de produção nem prova de qualidade visual.",
            "- Sem compressão BC/BPTC, atlas packing ou pipeline de import/cook.",
            "- Sem paridade com PoE2; materiais e texturas são originais.",
            "- Nenhum FPS, frame-time, VRAM ou ganho é alegado.",
        ],
        footer="Gerado por `docs/benchmarks/m04/tools/build_pbr_atlas.py`; `--check` reproduz bytes e SHA-256.",
    ).encode("utf-8")
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

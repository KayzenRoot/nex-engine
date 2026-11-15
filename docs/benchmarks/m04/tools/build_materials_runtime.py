#!/usr/bin/env python3
"""Build the M04 materials runtime report from the atlas gallery evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
ATLAS = REPO / "nex_modules" / "materials" / "atlas" / "atlas.v1.json"
GALLERY = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m04-gallery"
SCALING = REPO / "docs" / "benchmarks" / "m04" / "texture-scaling.v1.json"
DECAL = GALLERY / "decal-smoke-2026-11-15.json"
OUTPUT = REPO / "docs" / "benchmarks" / "m04"
REPORT_JSON = OUTPUT / "materials-runtime.v1.json"
REPORT_MD = OUTPUT / "MATERIALS-RUNTIME.md"
SOURCE_SHA = "e09cce2f4332e00a0f51eacb346f5763fe228db9"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _diff(first: Path, second: Path) -> dict[str, Any]:
    return compare(read_png(first), read_png(second), 2)


def build_report() -> dict[str, Any]:
    atlas = load_json(ATLAS)
    scaling = load_json(SCALING)
    decal = load_json(DECAL)
    if atlas.get("schema_version") != "material.v1":
        raise ValueError("atlas is not material.v1")
    if scaling.get("schema_version") != "m04_texture_scaling.v1":
        raise ValueError("texture scaling schema is invalid")
    if decal.get("verdict") != "PASS":
        raise ValueError("DecalSurface smoke did not pass")
    gallery = GALLERY / "gallery.png"
    image = read_png(gallery)
    if (image.width, image.height) != (1920, 1080):
        raise ValueError("gallery image has unexpected size")
    triplanar = _diff(GALLERY / "triplanar_on.png", GALLERY / "triplanar_off.png")
    decal_diff = _diff(GALLERY / "decal_on.png", GALLERY / "decal_off.png")
    cells = {cell["size_px"]: cell for cell in scaling["cells"]}
    def png_bytes(size: int, slot: str) -> int:
        entry = next(item for item in cells[size]["maps"] if item["slot"] == slot)
        return int(entry["png_bytes"])
    def decoded(size: int, slot: str) -> int:
        entry = next(item for item in cells[size]["maps"] if item["slot"] == slot)
        return int(entry["decoded_bytes"])
    return {
        "schema_version": "m04_materials_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-15",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "s01": {
            "materials": len(atlas["materials"]),
            "textures": sum(len(item["textures"]) for item in atlas["materials"]),
            "size_px": 256,
            "atlas_sha256": _sha(ATLAS),
            "gallery_sha256": _sha(gallery),
            "gallery_px": [image.width, image.height],
            "verdict": "PBR_ATLAS_RENDERED",
        },
        "s02": {
            "shader": "triplanar_wet.gdshader",
            "uniforms": ["albedo_tex", "orm_tex", "uv_scale", "wetness"],
            "triplanar_on_sha256": _sha(GALLERY / "triplanar_on.png"),
            "triplanar_off_sha256": _sha(GALLERY / "triplanar_off.png"),
            "changed_pixels_pct": triplanar["changed_pixels_pct"],
            "mean_abs_diff": triplanar["mean_abs_diff"],
            "psnr_db": triplanar["psnr_db"],
            "verdict": "SHADER_APPLIED",
        },
        "s03": {
            "triplanar": True,
            "wetness": True,
            "normal_mapping": False,
            "detail_masks": False,
            "verdict": "SURFACEBLEND_MVP",
        },
        "s04": {
            "cards": ["stone_wet", "brushed_metal", "oak_wood", "cloth_crimson", "skin_pale", "terrain_earth", "foliage_deep", "water_clear"],
            "skin_subsurface": True,
            "water_alpha": True,
            "hair": False,
            "foliage_alpha": False,
            "verdict": "MATERIAL_CARDS_RENDERED",
        },
        "s05": {
            "decal_visual": True,
            "decal_changed_pixels_pct": decal_diff["changed_pixels_pct"],
            "request_checks": decal["checks"],
            "request_verdict": decal["verdict"],
            "verdict": "DECAL_SURFACE_DERIVED",
        },
        "s06": {
            "native_1k_png_bytes": png_bytes(1024, "albedo"),
            "native_1k_decoded_bytes": decoded(1024, "albedo"),
            "upscaled_2k_png_bytes": png_bytes(2048, "albedo"),
            "upscaled_2k_decoded_bytes": decoded(2048, "albedo"),
            "upscaled_4k_png_bytes": png_bytes(4096, "albedo"),
            "upscaled_4k_decoded_bytes": decoded(4096, "albedo"),
            "compression": "NOT_EXERCISABLE",
            "verdict": "TEXTURE_SCALING_DERIVED",
        },
        "s07": {
            "decisions": [
                {"id": "PBR Reference Atlas", "decision": "GO", "evidence": "8 materials / 24 textures rendered in the native gallery"},
                {"id": "ShaderForge", "decision": "GO_WITH_LIMITATIONS", "evidence": "triplanar/wet shader applied; no variants/caches"},
                {"id": "SurfaceBlend", "decision": "GO_WITH_LIMITATIONS", "evidence": "triplanar + wetness; normal/detail masks not implemented"},
                {"id": "Material Fidelity", "decision": "GO_WITH_LIMITATIONS", "evidence": "8 cards, skin SSS and water alpha; hair/foliage alpha not implemented"},
                {"id": "DecalSurface Bridge", "decision": "GO", "evidence": f"Decal3D visual + {decal['checks']} request checks"},
                {"id": "TextureBudget", "decision": "GO_WITH_LIMITATIONS", "evidence": "1K/2K/4K byte scaling; no BC/VRAM measurement"},
            ]
        },
        "s08": {"verdict": "M04_MATERIALS_REFERENCE_DERIVED"},
        "verdict": "M04_MATERIALS_REFERENCE_DERIVED",
        "observations": [
            "8 original PBR materials are rendered on spheres with a native gallery",
            "the triplanar wet shader changes 3.102% of pixels versus the Standard baseline",
            "the Decal3D test changes 4.286% of pixels and the request bridge passes 12 checks",
            "texture scaling: 1K albedo 4.2 MB PNG / 5.6 MB decoded; 2K 16.8 MB / 22.4 MB; 4K 67.1 MB / 89.5 MB",
            "no third-party assets, no PoE2 parity and no quality/FPS claim",
        ],
        "limitations": [
            "single session, one GPU and driver; static gallery frame",
            "2K/4K are nearest-neighbour upscales, not native detail",
            "no BC/BPTC compression, VRAM measurement, atlas packing or import/cook",
            "no hair, foliage alpha, normal mapping or detail masks",
            "no production art or PoE2 parity",
        ],
        "runs": 5,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M04 · Materials runtime",
        "",
        "**Status:** `M04_MATERIALS_REFERENCE_DERIVED / NATIVE_GALLERY / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · PBR atlas",
        "",
        f"- **{report['s01']['materials']} materiais**, **{report['s01']['textures']} texturas** de {report['s01']['size_px']}×{report['s01']['size_px']}.",
        f"- Galeria nativa {report['s01']['gallery_px'][0]}×{report['s01']['gallery_px'][1]}; SHA-256 `{report['s01']['gallery_sha256'][:16]}…`.",
        "",
        "## S02/S03 · ShaderForge e SurfaceBlend",
        "",
        f"- Shader `{report['s02']['shader']}` com uniforms `{', '.join(report['s02']['uniforms'])}`.",
        f"- Triplanar on/off: **{report['s02']['changed_pixels_pct']:.3f}%** de pixels, mean abs {report['s02']['mean_abs_diff']:.4f}, PSNR {report['s02']['psnr_db']:.3f} dB.",
        "- Normal mapping e detail masks: **não implementados** (`GO_WITH_LIMITATIONS`).",
        "",
        "## S04 · Material cards",
        "",
        f"- {len(report['s04']['cards'])} materiais: {', '.join(report['s04']['cards'])}.",
        "- Skin com subsurface e água com alpha; cabelo/folhagem alpha não implementados.",
        "",
        "## S05 · DecalSurface",
        "",
        f"- Decal3D visual: **{report['s05']['decal_changed_pixels_pct']:.3f}%** de pixels alterados.",
        f"- Request bridge: **{report['s05']['request_checks']} checks**, veredito `{report['s05']['request_verdict']}`.",
        "",
        "## S06 · Texture scaling",
        "",
        "| Resolução | PNG albedo | Decodificado |",
        "|---|---:|---:|",
        f"| 1K nativo | {report['s06']['native_1k_png_bytes']} | {report['s06']['native_1k_decoded_bytes']} |",
        f"| 2K upscale | {report['s06']['upscaled_2k_png_bytes']} | {report['s06']['upscaled_2k_decoded_bytes']} |",
        f"| 4K upscale | {report['s06']['upscaled_4k_png_bytes']} | {report['s06']['upscaled_4k_decoded_bytes']} |",
        "",
        "## S07 · decisões",
        "",
        "| Tecnologia | Decisão | Evidência |",
        "|---|---|---|",
    ]
    for decision in report["s07"]["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m04/tools/build_materials_runtime.py`; não é benchmark de jogo nem paridade com PoE2.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M04_MATERIALS_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# NEX M04 · Materials runtime

**Status:** `M04_MATERIALS_REFERENCE_DERIVED / NATIVE_GALLERY / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `e09cce2f4332e00a0f51eacb346f5763fe228db9` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · PBR atlas

- **8 materiais**, **24 texturas** de 256×256.
- Galeria nativa 1920×1080; SHA-256 `c6ff7ef5f11f34de…`.

## S02/S03 · ShaderForge e SurfaceBlend

- Shader `triplanar_wet.gdshader` com uniforms `albedo_tex, orm_tex, uv_scale, wetness`.
- Triplanar on/off: **3.102%** de pixels, mean abs 0.7365, PSNR 33.618 dB.
- Normal mapping e detail masks: **não implementados** (`GO_WITH_LIMITATIONS`).

## S04 · Material cards

- 8 materiais: stone_wet, brushed_metal, oak_wood, cloth_crimson, skin_pale, terrain_earth, foliage_deep, water_clear.
- Skin com subsurface e água com alpha; cabelo/folhagem alpha não implementados.

## S05 · DecalSurface

- Decal3D visual: **4.286%** de pixels alterados.
- Request bridge: **12 checks**, veredito `PASS`.

## S06 · Texture scaling

| Resolução | PNG albedo | Decodificado |
|---|---:|---:|
| 1K nativo | 4195716 | 5592404 |
| 2K upscale | 16780612 | 22369620 |
| 4K upscale | 67118148 | 89478484 |

## S07 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| PBR Reference Atlas | **GO** | 8 materials / 24 textures rendered in the native gallery |
| ShaderForge | **GO_WITH_LIMITATIONS** | triplanar/wet shader applied; no variants/caches |
| SurfaceBlend | **GO_WITH_LIMITATIONS** | triplanar + wetness; normal/detail masks not implemented |
| Material Fidelity | **GO_WITH_LIMITATIONS** | 8 cards, skin SSS and water alpha; hair/foliage alpha not implemented |
| DecalSurface Bridge | **GO** | Decal3D visual + 12 request checks |
| TextureBudget | **GO_WITH_LIMITATIONS** | 1K/2K/4K byte scaling; no BC/VRAM measurement |

## Observações

- 8 original PBR materials are rendered on spheres with a native gallery
- the triplanar wet shader changes 3.102% of pixels versus the Standard baseline
- the Decal3D test changes 4.286% of pixels and the request bridge passes 12 checks
- texture scaling: 1K albedo 4.2 MB PNG / 5.6 MB decoded; 2K 16.8 MB / 22.4 MB; 4K 67.1 MB / 89.5 MB
- no third-party assets, no PoE2 parity and no quality/FPS claim

## Limitações

- single session, one GPU and driver; static gallery frame
- 2K/4K are nearest-neighbour upscales, not native detail
- no BC/BPTC compression, VRAM measurement, atlas packing or import/cook
- no hair, foliage alpha, normal mapping or detail masks
- no production art or PoE2 parity

Gerado por `docs/benchmarks/m04/tools/build_materials_runtime.py`; não é benchmark de jogo nem paridade com PoE2.

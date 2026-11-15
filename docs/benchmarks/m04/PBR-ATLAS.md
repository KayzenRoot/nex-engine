# NEX M04 · PBR reference atlas

**Status:** `REFERENCE_ATLAS / NATIVE_GALLERY / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Base:** `e09cce2f4332e00a0f51eacb346f5763fe228db9` · **Godot:** `4.7.2-stable` · **Resolução:** 256×256

| Material | Albedo | Metallic | Roughness | Texturas |
|---|---:|---:|---:|---:|
| stone_wet | 0.38/0.40/0.43 | 0.00 | 0.55 | 3 |
| brushed_metal | 0.62/0.64/0.68 | 1.00 | 0.30 | 3 |
| oak_wood | 0.45/0.31/0.18 | 0.00 | 0.70 | 3 |
| cloth_crimson | 0.38/0.08/0.09 | 0.00 | 0.90 | 3 |
| skin_pale | 0.72/0.58/0.50 | 0.00 | 0.50 | 3 |
| terrain_earth | 0.22/0.17/0.12 | 0.00 | 0.95 | 3 |
| foliage_deep | 0.12/0.30/0.12 | 0.00 | 0.80 | 3 |
| water_clear | 0.08/0.22/0.30 | 0.15 | 0.12 | 3 |

## O que é

- 24 texturas PNG determinísticas (albedo, normal, ORM) em 256×256, geradas sem rendering.
- 8 materiais `StandardMaterial3D` em `.tres`, carregados pela galeria nativa.
- Uma observação `material.v1` com SHA-256 de cada textura e orçamento declarado.

## Limitações

- Atlas de referência, não arte de produção nem prova de qualidade visual.
- Sem compressão BC/BPTC, atlas packing ou pipeline de import/cook.
- Sem paridade com PoE2; materiais e texturas são originais.
- Nenhum FPS, frame-time, VRAM ou ganho é alegado.

Gerado por `docs/benchmarks/m04/tools/build_pbr_atlas.py`; `--check` reproduz bytes e SHA-256.

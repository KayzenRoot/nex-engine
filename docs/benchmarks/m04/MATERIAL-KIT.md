# NEX M04 · Procedural material kit

**Status:** `REFERENCE_KIT / NON_RENDERING / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Base:** `99437b22e94a6494eaef801872bb8fd0c79c0f1a` · **Godot:** `4.7.2-stable`

| Material | Albedo | Metallic | Roughness | Emission | Textures |
|---|---:|---:|---:|---:|---:|
| concrete_floor | 0.55/0.55/0.57 | 0.00 | 0.85 | 0.00 | 3 |
| brushed_metal | 0.62/0.64/0.68 | 1.00 | 0.35 | 0.00 | 3 |
| oak_wood | 0.45/0.31/0.18 | 0.00 | 0.70 | 0.00 | 3 |
| emissive_trim | 0.10/0.10/0.12 | 0.00 | 0.40 | 2.50 | 3 |

## O que é

- 12 texturas PNG determinísticas (albedo, normal, ORM) em 128×128, geradas sem rendering.
- 4 materiais `StandardMaterial3D` em `.tres`, carregados headless por `ResourceLoader`.
- Uma observação `material.v1` com SHA-256 de cada textura e orçamento declarado.

## Limitações

- Kit de referência: não é arte de produção nem prova de qualidade visual.
- Sem shader customizado, sem compilação de shader, sem renderer, sem cena ou runtime.
- Texturas não são comprimidas nem importadas para um pipeline de build; o log headless cobre apenas o carregamento local.
- Nenhum FPS, frame-time, VRAM ou ganho é alegado.

Gerado por `docs/benchmarks/m04/tools/build_material_kit.py`; `--check` reproduz bytes e SHA-256.

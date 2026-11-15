# NEX M04 · Kit texture budget

**Status:** `BUDGET_PLANNING_DERIVED / NON_RENDERING / NO_PERFORMANCE_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Kit:** `nex_modules/materials/kit/kit.v1.json` · **SHA-256:** `0e597c6579205f93ebb2afc7c659a58593a759df0bdc4f0bd5574306713a6b08`
**Evidência:** `nex_modules/materials/texturebudget/evidence/kit-budget-2026-11-15.json` · **SHA-256:** `3c3051ab7c1931ee8e77ad34c98ab63bf3d7929e4936bd0be126c17d4e79044d`

| Métrica | Valor |
|---|---:|
| Materiais | 4 |
| Refs de textura | 12 |
| Texturas únicas | 12 |
| Bytes decodificados | 1048572 |
| Bytes deduplicados | 1048572 |
| Refs duplicadas | 0 |
| Pressão de atlas | 0.047 |
| Veredito | FIT |

## Observações

- all 12 kit textures are unique and referenced once
- decoded size is 1,048,572 bytes against a 268,435,456-byte budget
- atlas pressure is 0.047 (12 tiles of 256 available)
- the planner reports no findings and a FIT verdict

## Limitações

- planning only: no texture is loaded, decoded, uploaded or rendered
- decoded size is width*height*4 with a 4/3 mipmap factor, not measured VRAM
- atlas pressure is tile arithmetic (256 px tiles), not an allocator simulation
- downscale steps reduce dimensions by half down to 64 px; no resampling is performed
- visual quality and runtime cost are INCONCLUSIVE_NOT_RUN
- no scene, engine or project.godot integration

Gerado por `docs/benchmarks/m04/tools/build_kit_budget.py`; não é benchmark de hardware.

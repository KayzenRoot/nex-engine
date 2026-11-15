# NEX M04 · Texture scaling

**Status:** `SCALING_DERIVED / IN_MEMORY / NO_VRAM_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte nativa:** 1024×1024 · 2K/4K são upscales nearest-neighbour documentados.

| Resolução | Mapa | Detalhe | PNG bytes | Decodificado | SHA-256 |
|---:|---|---|---:|---:|---|
| 1024 | albedo | native | 4195716 | 5592404 | `c74ac234c5473217…` |
| 1024 | normal | native | 4195716 | 5592404 | `9f3729aea760cf67…` |
| 1024 | orm | native | 4195716 | 5592404 | `36a984d99c8daedb…` |
| 2048 | albedo | nearest_upscale_from_1024 | 16780612 | 22369620 | `99e93dba8305645e…` |
| 2048 | normal | nearest_upscale_from_1024 | 16780612 | 22369620 | `f283ff716674ec64…` |
| 2048 | orm | nearest_upscale_from_1024 | 16780612 | 22369620 | `366a415431915478…` |
| 4096 | albedo | nearest_upscale_from_1024 | 67118148 | 89478484 | `97a7ed3327d1dbf6…` |
| 4096 | normal | — | — | — | `NOT_GENERATED` |
| 4096 | orm | — | — | — | `NOT_GENERATED` |

## Observações

- 1K is generated natively for albedo, normal and ORM
- 2K is a nearest-neighbour upscale of the 1K reference; 4K albedo is a 4x upscale
- decoded bytes include the full mip chain (4/3 of the base level)
- PNG uses stored deflate; compression is a separate M11 import concern

## Limitações

- 2K/4K do not contain native high-frequency detail; they are scaling probes
- no BC/BPTC/VRAM compression or GPU sampling is measured
- large textures are not committed; only hashes and sizes are evidence
- single material; no cross-material atlas packing
- no visual quality or FPS claim

Gerado por `docs/benchmarks/m04/tools/build_texture_scaling.py`; não é medição de VRAM.

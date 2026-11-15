# Checkpoint Delta · NEX-M04-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `e09cce2f4332e00a0f51eacb346f5763fe228db9`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M04 full reference admitido:** `NEX-ADR-0015` / `NEX-D-026`, bounded aos materiais de referência.
2. **PBR Atlas:** 8 materiais originais, 24 texturas 256×256, galeria nativa 1920×1080.
3. **ShaderForge/SurfaceBlend:** triplanar/wet com 3.102% de pixels alterados, mean abs 0.7365, PSNR 33.618 dB.
4. **DecalSurface:** Decal3D com 4.286% de pixels; API com 12/12 checks.
5. **TextureBudget:** 1K 4.2/5.6 MB; 2K 16.8/22.4 MB; 4K albedo 67.1/89.5 MB (2K/4K upscales).
6. **Gate:** `M04-FINAL-GATE.md`; issues #44–#51 e #9 fechadas após squash e checks.
7. **Sem assets/shaders/cenas de PoE2, sem paridade com PoE2, sem arte de produção.**

## O que NÃO muda

- M05–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime de jogo, gameplay ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M04-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_modules/materials/atlas/atlas.v1.json`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m04-gallery/`
- `docs/benchmarks/m04/materials-runtime.v1.json`
- `docs/benchmarks/m04/M04-FINAL-GATE.md`
- `tests/ci/test_m04_final.py`

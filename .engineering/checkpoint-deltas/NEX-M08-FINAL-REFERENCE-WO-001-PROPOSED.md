# Checkpoint Delta · NEX-M08-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `2c7dd515e307086cdd7180577b0c78ad7fb5cf1c`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M08 full reference admitido:** `NEX-ADR-0019` / `NEX-D-030`, bounded à composição 2.5D de referência.
2. **CompositionPlanner:** 69 checks headless.
3. **Câmera híbrida:** ortográfica 0.390 ms e perspectiva 0.332 ms.
4. **Sprite3D billboards:** 40 sprites, +2.56% GPU, 6.463% de pixels.
5. **Depth sorting:** 0.000% de diferença vs sprites → **NO_GO** para sorter customizado.
6. **Sombras 3D:** +27.69% GPU, 15.477% de pixels.
7. **Overlay 2D:** +5.38% GPU, 22.789% de pixels.
8. **Hybrid:** +30.26% GPU, 31.714% de pixels.
9. **Quality profiles:** low/high 0.397/0.497 ms.
10. **Gate:** `M08-FINAL-GATE.md`; issue #13 fechada após squash e checks.

## O que NÃO muda

- M09–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum renderer 2.5D de produção, viewport stacking, shader customizado ou gameplay é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M08-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/scenes/m08_2_5d/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-16-m08/`
- `docs/benchmarks/m08/m08-runtime.v1.json`
- `docs/benchmarks/m08/M08-FINAL-GATE.md`
- `tests/ci/test_m08_final.py`

# Checkpoint Delta · NEX-M03-S01-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `edd3bc3003acae681f46227367d8c11b06cad99f` · **Code SHA:** `9c252e8062141f90f7c30e156b0ff35eee1fb4ab`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03-S01 concluído como protótipo isolado:** planejador determinístico de light rig com ambiente, registro de luzes, coerência por tipo, orçamento de sombras, cascatas e exportação `lighting.v1`.
2. **Parent M03 (#8) permanece NOT_ADMITTED.** Nenhuma implementação de luz/sombra/GI, shader, cena, engine, CI ou `project.godot`.
3. **Contrato `lighting.v1` consumido:** vocabulário e limites espelhados; nenhum contrato alterado.
4. **Performance/qualidade:** `INCONCLUSIVE_NOT_RUN`; `estimated_shadow_maps` é estimativa aritmética.
5. **Próximos incrementos:** integração de iluminação em cena exige WO própria; M04/M05/M06/M08 seguem não admitidos.

## O que NÃO muda

- M01/M02/M07 permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim visual/performance.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-S01-WO-001-EVIDENCE.md`
- `nex_modules/lighting/light_rig/evidence/headless-smoke-2026-11-13.log` (`NEX_M03_S01_SMOKE_PASS: 70 checks`)
- `tests/ci/test_light_rig_planner.py` (10 testes)

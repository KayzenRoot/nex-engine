# Checkpoint Delta · NEX-M05-FXBUDGET-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `6f93034e7557a6cb0a77aa89d6109ffea9d0c3da` · **Code SHA:** `10ecb58afc411f4e5a6e421342dffdd29462c0ab`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M05-FXBUDGET concluído como protótipo isolado:** agregação de emissores/partículas/GPU/decals, achados de orçamento e planos de redução de partículas e conversão GPU→CPU.
2. **Parent M05 (#10) permanece NOT_ADMITTED.** Nenhuma partícula/emissor/luz/decal, cena, engine, CI ou `project.godot`.
3. **Contrato `spellfx.v1` consumido:** vocabulário, autoridade de gameplay, light bridge e orçamento espelhados; nenhum contrato alterado.
4. **Qualidade/performance:** `INCONCLUSIVE_NOT_RUN`; totais e planos são aritméticos.
5. **Próximos incrementos:** validação real de FX e M06/M08/M12 exigem WO própria.

## O que NÃO muda

- M01/M02/M03/M04/M05/M07 permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim visual/performance.

## Evidência de apoio

- `.engineering/evidence/NEX-M05-FXBUDGET-WO-001-EVIDENCE.md`
- `nex_modules/vfx/fxbudget/evidence/headless-smoke-2026-11-13.log` (`NEX_M05_FXBUDGET_SMOKE_PASS: 57 checks`)
- `tests/ci/test_fx_budget_planner.py` (9 testes)

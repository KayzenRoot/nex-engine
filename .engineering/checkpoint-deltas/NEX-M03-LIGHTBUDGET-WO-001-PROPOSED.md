# Checkpoint Delta · NEX-M03-LIGHTBUDGET-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `7205f6cb2af590877c84a7654a58cad01ec9e5cd` · **Code SHA:** `26f6ab9334e406ec9e6b834c9eed7aa204bf01e3`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03-LIGHTBUDGET concluído como protótipo isolado:** projeção determinística de custo GPU a partir dos coeficientes S05, veredito FIT/TIGHT/OVER_BUDGET e escada de degradação ordenada.
2. **Parent M03 (#8) permanece NOT_ADMITTED.** Nenhuma captura nova, rendering, shader, cena, engine, CI ou `project.godot`.
3. **Rastreabilidade:** coeficientes e âncoras S05 documentados; nenhuma generalização para cenas reais.
4. **Performance:** projeção é modelo calibrado, não medição nova; `INCONCLUSIVE_NOT_RUN` para cena real.
5. **Próximos incrementos:** validação em cena real e demais módulos exigem WO própria.

## O que NÃO muda

- M01/M02/M07 e incrementos M03 anteriores permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim de FPS ou benchmark.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-LIGHTBUDGET-WO-001-EVIDENCE.md`
- `nex_modules/lighting/budget/evidence/headless-smoke-2026-11-13.log` (`NEX_M03_LIGHTBUDGET_SMOKE_PASS: 57 checks`)
- `tests/ci/test_light_budget_arbiter.py` (9 testes)

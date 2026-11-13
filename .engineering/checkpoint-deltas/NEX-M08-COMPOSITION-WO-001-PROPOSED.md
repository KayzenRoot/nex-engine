# Checkpoint Delta · NEX-M08-COMPOSITION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `5159d774436015870ab4fec1fe1416d5a8190cd1` · **Code SHA:** `0f1cc07f8175b0f4b17a535721df28a2dcbf3814`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M08-COMPOSITION concluído como protótipo isolado:** stack 2.5D, políticas de profundidade/alpha/HUD, ordem por papel, conflitos e exportação `composition.v1`.
2. **Parent M08 (#13) permanece NOT_ADMITTED.** Nenhuma camada, viewport, shader, cena, engine, CI ou `project.godot`.
3. **Contrato `composition.v1` consumido:** vocabulário e invariantes espelhados; nenhum contrato alterado.
4. **Visual/performance:** `INCONCLUSIVE_NOT_RUN`; conflitos são heurísticos, não pixels.
5. **Próximos incrementos:** integração 2.5D em cena e M09–M12 exigem WO própria.

## O que NÃO muda

- M01–M07 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M08-COMPOSITION-WO-001-EVIDENCE.md`
- `nex_modules/render2_5d/composition/evidence/headless-smoke-2026-11-13.log` (`NEX_M08_COMPOSITION_SMOKE_PASS: 69 checks`)
- `tests/ci/test_composition_planner.py` (9 testes)

# Checkpoint Delta · NEX-M04-TEXTUREBUDGET-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `65afc09666f8e8f5046e471c8a8e37cf71368279` · **Code SHA:** `658ee86f70fea867db1cac0ad46a178d4b350cc0`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M04-TEXTUREBUDGET concluído como protótipo isolado:** deduplicação por SHA-256, bytes decodificados com mips, pressão de atlas, achados e plano de downscale determinístico.
2. **Parent M04 (#9) permanece NOT_ADMITTED.** Nenhum decode/upload/atlas packing, material, shader, cena, engine, CI ou `project.godot`.
3. **Contrato `material.v1` consumido:** slots, padrão de id, SHA-256, dimensões e orçamento espelhados; nenhum contrato alterado.
4. **VRAM/qualidade:** `INCONCLUSIVE_NOT_RUN`; bytes e tiles são aritméticos.
5. **Próximos incrementos:** validação real de texturas e M05 FX budget exigem WO própria.

## O que NÃO muda

- M01/M02/M03/M04/M05/M07 permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim de VRAM ou performance.

## Evidência de apoio

- `.engineering/evidence/NEX-M04-TEXTUREBUDGET-WO-001-EVIDENCE.md`
- `nex_modules/materials/texturebudget/evidence/headless-smoke-2026-11-13.log` (`NEX_M04_TEXTUREBUDGET_SMOKE_PASS: 55 checks`)
- `tests/ci/test_texture_budget_planner.py` (9 testes)

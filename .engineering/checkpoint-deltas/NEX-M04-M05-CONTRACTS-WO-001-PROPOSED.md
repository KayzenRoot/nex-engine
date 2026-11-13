# Checkpoint Delta · NEX-M04-M05-CONTRACTS-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `11d8e61579680166bb36a645502d97e60b23a832` · **Code SHA:** `e1d89adeb6c86507032571987075b75c6ec64b70`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Contratos M04 e M05 v1 definidos:** `material.v1` e `spellfx.v1` cobrem identidade, orçamento, autoridade de gameplay, disponibilidade de performance e proveniência.
2. **Parents M04 (#9) e M05 (#10) permanecem NOT_ADMITTED.** Nenhum material/shader/textura/partícula/VFX, cena, engine, CI ou `project.godot`.
3. **Ownership prospectivo:** paths futuros de `nex_modules/materials/**` e `nex_modules/vfx/**` mapeados sem admissão implícita.
4. **Performance/visual:** `INCONCLUSIVE_NOT_RUN`; nenhum claim.
5. **Próximos incrementos:** implementação M04/M05 e M06/M08/M12 exigem WO própria.

## O que NÃO muda

- M01/M02/M03/M07 permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim visual/performance.

## Evidência de apoio

- `.engineering/evidence/NEX-M04-M05-CONTRACTS-WO-001-EVIDENCE.md`
- `tests/contracts/test_m04_material_contract.py` (16 testes)
- `tests/contracts/test_m05_spellfx_contract.py` (20 testes)
- Suíte de contratos: 93 testes OK.

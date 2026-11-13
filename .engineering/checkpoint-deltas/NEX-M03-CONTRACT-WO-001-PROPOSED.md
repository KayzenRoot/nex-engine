# Checkpoint Delta · NEX-M03-CONTRACT-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `928ea7c14d253778a229e22133b982a0ee2167ef` · **Code SHA:** `38e1d4cb52f8ca8801fc35492ca9afe0d565e419`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Contrato M03 v1 definido:** `lighting.v1` cobre ambiente, rig de luzes, orçamento de sombra, performance com disponibilidade explícita e proveniência.
2. **Parent M03 (#8) permanece NOT_ADMITTED.** Nenhuma implementação de iluminação, shader, cena, engine, CI ou `project.godot`.
3. **Ownership prospectivo:** paths futuros de `nex_modules/lighting/**` mapeados sem admissão implícita; contratos M01/M02/M07 inalterados.
4. **Performance/qualidade:** `INCONCLUSIVE_NOT_RUN`; nenhum claim de FPS, VRAM ou qualidade visual.
5. **Próximos incrementos:** implementação M03 e demais módulos exigem WO própria com admissão.

## O que NÃO muda

- M01/M02/M07 permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim visual/performance.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-CONTRACT-WO-001-EVIDENCE.md`
- `tests/contracts/test_m03_lighting_contract.py` (16 testes; suíte de contratos 57 OK)

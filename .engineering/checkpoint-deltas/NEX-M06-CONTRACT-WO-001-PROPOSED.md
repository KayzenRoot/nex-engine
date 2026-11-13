# Checkpoint Delta · NEX-M06-CONTRACT-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `beab4ac0eab6b57455cde57ff6627b74b46a4cd7` · **Code SHA:** `78af311cdb0e04f94f23f1c1a3d5e33e991fbad8`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Contrato M06 v1 definido:** `performance.v1` cobre workload, frame interval, timings, recursos, gargalo com evidência/confiança e comparação opcional.
2. **Parent M06 (#11) permanece NOT_ADMITTED.** Nenhuma medição, benchmark, engine, CI ou `project.godot`.
3. **Ownership prospectivo:** atlas/LOD/culling/streaming/framepacer mapeados sem admissão implícita.
4. **Performance:** contrato de representação; nenhum claim de FPS/regressão.
5. **Próximos incrementos:** captura real e submódulos M06 exigem WO própria.

## O que NÃO muda

- M01–M05/M07 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-CONTRACT-WO-001-EVIDENCE.md`
- `tests/contracts/test_m06_performance_contract.py` (17 testes)
- Suíte de contratos: 110 testes OK.

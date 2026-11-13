# Checkpoint Delta · NEX-M02-S04-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `bad8b52ea1a408fb9cd06e6dca2d7086d1414b07` · **Code SHA:** `9a1bdde165444b660c2a9b83e0e03234fc3a3657`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** ELEVATED (decisão registrada)

## Delta proposto

1. **M02-S04 concluído como protótipo isolado:** analisador determinístico de defeitos temporais (ghosting/flicker/shimmer/render scale) e gate de decisão (`KEEP_NATIVE` / `EVALUATE_COMPOSITOR` / `NO_GO`), com toggle de postprocess guardado e rollback.
2. **Parent M02 (#7) permanece NOT_ADMITTED.** Nenhuma integração de rendering, thread, compositor, shader, cena, CI ou engine.
3. **Decisão de risco ELEVATED:** análise apenas; operações irreversíveis inexistentes; risco residual `INCONCLUSIVE_NOT_RUN`; compositor/render-thread exigem WO separada do Owner com ABI review.
4. **Próximos incrementos:** M02-S05 (matriz de capacidades/perfis) pode consumir o gate como mock; integração real exige WO própria. M02-S06/S07 e M03–M12 seguem não admitidos.

## O que NÃO muda

- M01 baseline congelado; S01–S03 permanecem read-only.
- Nenhum checkpoint é promovido por este delta.
- Nenhum claim visual/FPS/VRAM; nenhum compositor implementado.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-S04-WO-001-EVIDENCE.md`
- `nex_modules/render3d/temporal/evidence/headless-smoke-2026-11-13.log` (`NEX_M02_S04_SMOKE_PASS: 51 checks`)
- `tests/ci/test_temporal_guard.py` (8 testes)

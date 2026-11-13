# Checkpoint Delta · NEX-M02-S01-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `02f94e62eaed0d70642a94a9495dcffad1aba519` · **Code SHA:** `9f8d4ce7b46d6a2ccebdd2b15ce4c0fe3a5412f3`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M02-S01 concluído como protótipo isolado:** rig de câmera isométrica determinístico (perspectiva e ortográfica), com API de framing, dead zone, bounds, zoom, sincronização mundo↔tela e replay; 32 asserts headless e 10 testes estruturais.
2. **Parent M02 (#7) permanece NOT_ADMITTED.** Nenhuma integração em `nex_bench`/engine, nenhuma mudança de rendering; o protótipo vive em `nex_modules/render3d/camera/`.
3. **Contrato `render_core.v1`:** o estado da câmera usa os labels e campos previstos; o contrato não é alterado.
4. **Performance:** `INCONCLUSIVE_NOT_RUN` por desenho; nenhuma meta do `budget.v1.json` é declarada cumprida.
5. **Próximos incrementos:** M02-S02 (Sightline) e S03 (DepthWeave) podem consumir a API com mocks; exigem WO própria e admissão do Owner. M02-S05/S06/S07 também seguem não admitidos.

## O que NÃO muda

- M01 baseline continua congelado como instrumento; M02–M12 sem admissão de módulo.
- Nenhum checkpoint é promovido por este delta.
- Nenhum claim de FPS, VRAM ou ganho visual.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-S01-WO-001-EVIDENCE.md`
- `nex_modules/render3d/camera/evidence/headless-smoke-2026-11-13.log` (`NEX_M02_S01_SMOKE_PASS: 32 checks`)
- `tests/ci/test_isometric_camera.py` (10 testes)

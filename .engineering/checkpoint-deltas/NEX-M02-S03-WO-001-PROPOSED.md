# Checkpoint Delta · NEX-M02-S03-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `7a9d33f4aab4062b14380828bdcd00035ebaa92a` · **Code SHA:** `68378db625386f3dffc961ed55881c1ddcf5ed12`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M02-S03 concluído como protótipo isolado:** planejador determinístico de profundidade/composição com passes opaco/alfa/overlay, riscos de Z-fight, histerese contra flicker, conflitos alfa×crítico e overlay×gameplay; draft de contrato M08 2.5D anexado.
2. **Parent M02 (#7) permanece NOT_ADMITTED.** Nenhuma integração de rendering, cena, shader, material, M04, 2.5D, CI ou engine.
3. **Visual/performance:** `INCONCLUSIVE_NOT_RUN`; sem screenshots, sem FPS/VRAM; nenhuma meta do budget M01 declarada cumprida.
4. **M08 draft:** `DRAFT_NOT_PROMOTED`; qualquer promoção exige WO do Owner e contrato revisado.
5. **Próximos incrementos:** M02-S04 (TemporalGuard) pode consumir o plano/histerese com mocks; integração real de cenas exige WO própria. M02-S05+ e M03–M12 seguem não admitidos.

## O que NÃO muda

- M01 baseline congelado; câmera S01 e Sightline S02 permanecem read-only.
- Nenhum checkpoint é promovido por este delta.
- Nenhum claim visual/FPS/VRAM.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-S03-WO-001-EVIDENCE.md`
- `nex_modules/render3d/depth_composition/evidence/headless-smoke-2026-11-13.log` (`NEX_M02_S03_SMOKE_PASS: 37 checks`)
- `tests/ci/test_depth_composition.py` (8 testes)

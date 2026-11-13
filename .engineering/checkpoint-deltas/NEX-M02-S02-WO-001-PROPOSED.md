# Checkpoint Delta · NEX-M02-S02-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `a50675bb21cb2a9519e76ec5b4a68c2f4e146d3f` · **Code SHA:** `6057c1da576458767f39d5dd5328ad763da3931d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M02-S02 concluído como protótipo isolado:** política Sightline determinística com AABBs, prioridades jogador→ameaça→decoração, fade/silhueta, histerese, cap, visibilidade de gameplay separada da legibilidade visual e alerta de ameaça.
2. **Parent M02 (#7) permanece NOT_ADMITTED.** Nenhuma integração em cenas, `nex_bench`, shaders, materiais, CI ou engine.
3. **Performance:** `INCONCLUSIVE_NOT_RUN`; nenhuma meta do budget M01 é declarada cumprida.
4. **Próximos incrementos:** M02-S03 (DepthWeave) pode consumir a API/estado com mocks; integração real de cenas/materiais exige WO própria. S04+ e M03–M12 seguem não admitidos.

## O que NÃO muda

- M01 baseline congelado como instrumento; câmera S01 permanece read-only.
- Nenhum checkpoint é promovido por este delta.
- Nenhum claim visual/FPS/VRAM.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-S02-WO-001-EVIDENCE.md`
- `nex_modules/render3d/sightline/evidence/headless-smoke-2026-11-13.log` (`NEX_M02_S02_SMOKE_PASS: 49 checks`)
- `tests/ci/test_sightline.py` (9 testes)

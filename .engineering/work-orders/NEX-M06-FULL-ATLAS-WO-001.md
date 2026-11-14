# NEX-M06-FULL-ATLAS-WO-001 | Dataset completo e atlas de performance M09

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** M06 bounded admitted (`NEX-ADR-0006`) + instrução do Owner de 2026-11-14 para seguir a ordem sugerida.
**Base:** `main` `75bf4811b696e2070475039cd50a2d7ae7913ee8`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (síntese de evidência).
**Lock:** `.engineering/context-locks/NEX-M06-FULL-ATLAS-WO-001-EXECUTION.json`.

## Objetivo

Converter as **144 capturas de performance M09** em observações `performance.v1` e construir um atlas M06 agregado por bundle, cena, preset, resolução e proxy. Sem nova captura e sem mudança de runtime/engine.

## Escopo

- `docs/benchmarks/m06/**`: `observations/m09-observations-full.v1.json`, `m09-performance-atlas.v1.json`, `M09-PERFORMANCE-ATLAS.md`, conversor full e builder.
- `tests/ci/test_m06_full_observations.py` e `tests/ci/test_m06_m09_atlas.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Nova medição, runtime, hub, engine, renderer, shaders, cenas ou CI.
- Alterar o contrato M06 ou os bundles M09.
- Generalização de performance/qualidade ou claims de FPS.
- Admissão de outros parents.

## DoD

- 144 observações válidas, IDs únicos, `evidence_uri` existente e schema/coerência M06.
- Atlas com 7 bundles de performance, contagens 6/18/18/18/24/48/12 e agregados reproduzíveis.
- Nenhum claim de FPS/qualidade; limitações documentadas.
- Suítes completas verdes em worktree LF limpo; PR protegida e checkpoint pós-merge.

## STOP

- Captura ausente, contagem divergir, schema/coerência falhar ou builder não reproduzir → parar e registrar.

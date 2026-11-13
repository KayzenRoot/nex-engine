# NEX-M06-BOTTLENECK-ATLAS-WO-001 | Atlas de gargalos sobre capturas S05

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento que operacionaliza `performance.v1` sobre capturas reais já publicadas.
**Base:** `main` `2a93668c1f72f1bb4e66ab5e35e037937c99c81f`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M06-BOTTLENECK-ATLAS-WO-001-EXECUTION.json` (28 fingerprints).

## Objetivo

Construir um atlas determinístico e reproduzível a partir das 15 capturas S05 do Lighting Matrix: recomputar agregados a partir dos brutos, verificar SHA-256 do bundle, classificar o gargalo no vocabulário `performance.v1`, calcular deltas vs baseline por contagem e documentar limitações. Sem captura nova.

## Escopo

- `docs/benchmarks/m06/`: `atlas.v1.json`, `ATLAS.md`, `tools/build_atlas.py`.
- `tests/ci/test_m06_atlas.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Executar Godot ou novas capturas; alterar `nex_bench`, engine, CI ou `project.godot`.
- Reivindicar benchmark, FPS, regressão ou generalização entre sessões/hardware.
- M06 parent admission; M08/M12.

## DoD

- Builder stdlib determinístico, hashes verificados, 15 runs mapeados e agregados recomputados.
- Atlas JSON + Markdown consistentes com o builder.
- Testes estruturais e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Hash divergente, run ausente, status não-COMPLETE ou necessidade de nova medição → parar e registrar.

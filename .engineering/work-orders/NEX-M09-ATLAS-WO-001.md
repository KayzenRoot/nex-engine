# NEX-M09-ATLAS-WO-001 | Atlas de medições M09

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre a linha M09.
**Base:** `main` `a33655a1ea55508a2d24d688936348a42c9ef10c`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (síntese de evidência).
**Lock:** `.engineering/context-locks/NEX-M09-ATLAS-WO-001-EXECUTION.json`.

## Objetivo

Consolidar os oito bundles M09 já integrados (A/B/A sintético, escala de proxies, A/B/A nas cenas M01, verdade visual, escala de resolução, interação, cross-scene e 200 proxies) em um atlas único, verificável e reproduzível, com contagens, source SHAs, achados e limitações.

## Escopo

- `docs/benchmarks/m09/**`: `measurement-atlas.v1.json`, `MEASUREMENT-ATLAS.md` e builder determinístico.
- `tests/ci/test_measurement_atlas.py`: verificação de contagens, hashes, valores-chave e reprodutibilidade.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Nova captura, novo harness, mudança de engine, cenas, `project.godot`, hub ou CI.
- Claims de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent admission.

## DoD

- Atlas cobre 8 bundles, 144 capturas de performance + 18 imagens, com source SHAs e contagens verificadas.
- Achados sintetizados com referência ao relatório de origem e sem generalização indevida.
- Builder reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Contagem/hash divergir de um bundle, relatório ausente ou builder não reproduzir → parar e registrar.

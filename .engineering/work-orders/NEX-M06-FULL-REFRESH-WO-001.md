# NEX-M06-FULL-REFRESH-WO-001 | Refresh do dataset completo M06

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M06/M09 são `BOUNDED_ADMITTED_EVIDENCE_PIPELINE` desde NEX-ADR-0006.
**Base:** `main` `c7d6f7271b1bf4ef5aa2a7f60fd09a08784b78aa`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (derivação de evidência).
**Lock:** `.engineering/context-locks/NEX-M06-FULL-REFRESH-WO-001-EXECUTION.json`.

## Objetivo

Atualizar a cadeia de evidência M06 para incluir as duas novas medições M09 (`interaction-200-720` e `res-scaling-1440`). O dataset completo passa de **144 para 156 observações** e de 7 para 9 bundles; atlas e advisories são regenerados de forma determinística, sem nova medição.

## Escopo

- `docs/benchmarks/m06/tools/convert_m09_observations.py`: novos bundles em `FULL_BUNDLES`, contagem 156.
- `docs/benchmarks/m06/tools/build_m09_atlas.py`: novos bundles, contagem 156 e observação de pacing.
- `docs/benchmarks/m06/tools/build_advisories.py`: `EXPECTED_OBSERVATIONS_FULL = 156`.
- Artefatos regenerados: `m09-observations-full.v1.json`, `m09-performance-atlas.v1.json`, `M09-PERFORMANCE-ATLAS.md`, `advisories-full.v1.json`, `ADVISORIES-FULL.md`.
- `docs/benchmarks/m06/README.md` e testes `test_m06_full_observations.py`, `test_m06_m09_atlas.py`, `test_m06_full_advisories.py`.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Nova medição, captura, renderização ou mudança de cena/harness.
- Alterar observações curadas, contrato `performance.v1`, bundles M09, modelo M03 ou builders M09.
- Novos parents, runtime, renderer, shaders, hub, `project.godot`.
- Claims de FPS, qualidade, ganho universal ou generalização.

## DoD

- 156 observações/sources, 9 bundles, todas `pacing`.
- Atlas: GPU p95 0.068–1.55 ms (mediana 0.226), pacing 4.199–4.311 ms, maior GPU share 36.29%.
- Advisories: 156, headroom 2.716–4.009 ms, maior GPU share 36.29%, frame alvo 4.167 ms.
- Saída curada de 12 observações/advisórios inalterada.
- `--check-full`, `--check` e testes verdes; suítes CI/contratos/telemetria verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, contagem divergente, observação inválida, alteração da saída curada ou check vermelho → parar e registrar.

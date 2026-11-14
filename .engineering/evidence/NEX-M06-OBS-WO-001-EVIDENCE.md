# Evidence Bundle · NEX-M06-OBS-WO-001 (observações performance.v1)

**Status:** `EVIDENCE_CONVERSION / SINGLE_SESSION / NO_NEW_MEASUREMENT / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** #59 · **Base:** `3aa83afaabbe3a0b65afb3d9250158b66da6dde6`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m06/observations/m09-observations.v1.json`: 12 observações `performance.v1` com IDs únicos, proveniência e `evidence_uri`.
- `docs/benchmarks/m06/tools/convert_m09_observations.py`: conversor determinístico com `--check`.
- `tests/ci/test_m06_observations.py`: 6 testes de schema, coerência, valores e reprodutibilidade.

## Observações selecionadas

| ID | Cena | Proxies | Resolução | GPU p95 | CPU p95 | Pacing p95 | Bottleneck |
|---|---|---:|---|---:|---:|---:|---|
| m09-preset-ab-low | preset-ab | 200 | 1280×720 | 0.147 ms | 0.357 ms | 4.199 ms | pacing |
| m09-preset-ab-high | preset-ab | 200 | 1280×720 | 0.746 ms | 0.467 ms | 4.222 ms | pacing |
| m09-m01-corridor-low | m01-corridor | 100 | 1280×720 | 0.086 ms | 0.328 ms | 4.208 ms | pacing |
| m09-m01-corridor-high | m01-corridor | 100 | 1280×720 | 0.542 ms | 0.475 ms | 4.210 ms | pacing |
| m09-res-960-low | m01-arena | 100 | 960×540 | 0.096 ms | 0.318 ms | 4.225 ms | pacing |
| m09-res-960-high | m01-arena | 100 | 960×540 | 0.317 ms | 0.444 ms | 4.203 ms | pacing |
| m09-res-1920-low | m01-arena | 100 | 1920×1080 | 0.156 ms | 0.344 ms | 4.241 ms | pacing |
| m09-res-1920-high | m01-arena | 100 | 1920×1080 | 0.826 ms | 0.446 ms | 4.273 ms | pacing |
| m09-i200-960-low | m01-arena | 200 | 960×540 | 0.099 ms | 0.357 ms | 4.261 ms | pacing |
| m09-i200-960-high | m01-arena | 200 | 960×540 | 0.322 ms | 0.506 ms | 4.264 ms | pacing |
| m09-i200-1920-low | m01-arena | 200 | 1920×1080 | 0.157 ms | 0.361 ms | 4.275 ms | pacing |
| m09-i200-1920-high | m01-arena | 200 | 1920×1080 | 0.846 ms | 0.518 ms | 4.248 ms | pacing |

## Semântica de campos

- `timings.*`: p95 medido da captura de origem.
- `resources.renderer_allocation_bytes`: p50 da série, histórico da sessão.
- `frame_interval`, `draw_calls`, `objects_rendered`, `vram_used_bytes`: `UNAVAILABLE` com razão explícita.
- `bottleneck`: `pacing` quando o pacing p95 excede o maior render p95 em mais de 1 ms; caso contrário `gpu`, `cpu` ou `unknown` conforme a razão GPU/CPU.
- `provenance.base_sha` e `head_sha`: source SHA medido da captura; `evidence_uri` aponta para a captura de origem.

## Verificação

- 12/12 observações passam `limited_schema_errors` e o consumidor de coerência M06.
- Todos os `evidence_uri` existem; driver `617.14` e GPU `NVIDIA GeForce RTX 5050`.
- `convert_m09_observations.py --check` reproduz o bundle.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma captura nova, mudança de contrato, engine, cenas, `project.godot`, hub ou CI.
- As 12 observações são uma seleção de runs já integrados, não uma amostra estatística completa.
- Nenhum claim de FPS de jogo, qualidade, ganho universal ou generalização.
- M06 parent (#59) permanece `NOT_ADMITTED`.

## Rollback

Remover o bundle de observações, o conversor, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- Ampliar a seleção, medir draw calls/VRAM ou admitir o parent M06 exige WO própria e, no caso de admissão, decisão do Owner.

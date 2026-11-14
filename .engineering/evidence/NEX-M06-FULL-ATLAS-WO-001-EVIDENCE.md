# Evidence Bundle · NEX-M06-FULL-ATLAS-WO-001 (dataset completo M09)

**Status:** `EVIDENCE_SYNTHESIS / SINGLE_SESSION / M09_PERFORMANCE_ATLAS_DERIVED / NO_FPS_CLAIM`
**Issues:** M06 #11 · M09 #14 · **Base:** `75bf4811b696e2070475039cd50a2d7ae7913ee8`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m06/observations/m09-observations-full.v1.json`: 144 observações `performance.v1` dos sete bundles de performance M09.
- `docs/benchmarks/m06/m09-performance-atlas.v1.json`, `M09-PERFORMANCE-ATLAS.md` e builder.
- `tests/ci/test_m06_full_observations.py` (5 testes) e `tests/ci/test_m06_m09_atlas.py` (5 testes).

## Cobertura

| Bundle | Runs |
|---|---:|
| preset-ab | 6 |
| proxy-scaling | 18 |
| m01-ab | 18 |
| res-scaling | 18 |
| interaction | 24 |
| cross-scene | 48 |
| interaction-200 | 12 |
| **Total** | **144** |

## Resultados

- 144/144 observações válidas contra `performance.v1` e o consumidor de coerência.
- Todas classificadas como `pacing` no cap de 240 fps.
- Atlas agrega 7 bundles e suas células de workload; GPU p95 global 0.068–0.887 ms (mediana 0.196 ms); pacing p95 4.199–4.301 ms; maior GPU share 21.05%.
- Nenhum claim de FPS, qualidade ou generalização.

## Verificação

- Conversor `--check-full` reproduz o bundle completo; builder `--check` reproduz o atlas.
- Todos os `evidence_uri` existem; schema/coerência verdes.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma nova captura, mudança de contrato, runtime, engine, cenas ou CI.
- Dataset de uma sessão única em uma RTX 5050; sem generalização.
- M06 bounded admission cobre evidência/análise, não runtime.
- M09 parent continua no escopo bounded admitted; nenhum outro parent é admitido.

## Rollback

Remover o bundle full, o atlas, os builders/testes novos e o delta/WO/lock correspondentes.

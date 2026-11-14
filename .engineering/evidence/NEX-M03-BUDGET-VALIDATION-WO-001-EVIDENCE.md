# Evidence Bundle · NEX-M03-BUDGET-VALIDATION-WO-001

**Status:** `EVIDENCE_SYNTHESIS / SINGLE_SESSION / PARTIAL_DOMAIN_MATCH / NO_MODEL_CHANGE`
**Issue:** #43 · **Base:** `71375d6621bb179abe88fde398fb62a7fe16da80`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m03/light-cost-model.v1.json`: snapshot verificado dos coeficientes.
- `docs/benchmarks/m03/budget-validation.v1.json`, `BUDGET-VALIDATION.md` e builder determinístico.
- `tests/ci/test_m03_budget_validation.py`: 5 testes.

## Resultados

| Cena | Preset | Omni | Shadowed | Previsto ms | Medido p95 ms | Erro |
|---|---|---:|---:|---:|---:|---:|
| corridor_static | ab-low | 3 | 0 | 0.35450 | 0.088 | +302.8% |
| corridor_static | ab-high | 3 | 3 | 0.41525 | 0.423 | −1.8% |
| arena_combat | ab-low | 4 | 0 | 0.37900 | 0.109 | +247.7% |
| arena_combat | ab-high | 4 | 4 | 0.46000 | 0.462 | −0.4% |
| dense_city | ab-low | 5 | 0 | 0.40350 | 0.084 | +380.4% |
| dense_city | ab-high | 5 | 4 | 0.48450 | 0.362 | +33.8% |

- 2/6 células dentro de 2% (corridor e arena no `ab-high`).
- Veredito `PARTIAL_DOMAIN_MATCH`; o modelo não representa resolução, MSAA, glow, atlas ou geometria.
- Os acertos de high são candidatos a coincidência de domínio, não prova de generalização.

## Verificação

- Snapshot confere com `DEFAULT_MODEL` do GDScript.
- Builder reproduz JSON e Markdown; testes verdes.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança no modelo, contrato M03, engine, cenas, `project.godot`, hub ou CI.
- Nenhuma nova captura ou medição.
- Nenhum claim de FPS, qualidade, ganho universal ou generalização.
- M03 parent (#43) permanece `NOT_ADMITTED`.

## Rollback

Remover o snapshot, o relatório, o builder, o teste e o delta/WO/lock correspondentes.

# NEX M01-S06 · Backlog de experimentos

Derivado de `RADAR-RD-2026-11-13.md`. Nenhum experimento abaixo autoriza implementação de módulo não admitido; os que dependem de WO estão marcados.

| ID | Hipótese (curta) | Módulo | Status | Pré-requisito | Runs | Gate primário |
|---|---|---|---|---|---:|---|
| E-01 | Warmup explícito reduz p95 inicial de frame time | M06 (harness M01) | READY | harness S05 aprovado | 3+3 | p95 −20%; sem regressão estável |
| E-02 | MultiMesh 200 reduz CPU p95 e melhora 1% low | M06 (harness M01) | READY | harness S05 aprovado | 3+3 | CPU p95 −30%; 1% low +5% |
| E-03 | Limite de luzes por relevância reduz GPU p95 | M03 (cenário sintético) | READY | harness S05 + cenário lights | 3+3 | GPU p95 −15%; erro visual ≤1/255 |
| E-04 | Batching 2D reduz draw calls/estado | M07 | DESIGN_ONLY | contrato M07 + WO de implementação | 3+3 | −25% draw calls; pixel-identical |
| E-05 | Input lag instrumentado com incerteza declarada | FLOW #70 | DESIGN_ONLY | admissão #70 | 3+3 | incerteza ≤1 frame |

## Regras

- Uma variável por experimento; baseline e tratamento no mesmo hardware/driver/SHA.
- 30 s por run após warmup de 2 s; 3 repetições seriais; sem GPU concorrente.
- Nenhum resultado é promovido a benchmark sem validador independente e SHA-256 dos brutos.
- `INCONCLUSIVE` é resultado válido; não repetir até "dar verde".
- Qualquer experimento que exija alterar `project.godot`, shaders compartilhados ou core precisa de WO e lock próprios.

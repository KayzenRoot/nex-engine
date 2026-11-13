# NEX M01 · Research inputs (S06)

Fonte completa: `docs/research/nex-m01/RADAR-RD-2026-11-13.md` e `EXPERIMENT-BACKLOG.md`.

## Ranking de experimentos imediatos no harness

| Ordem | ID | Hipótese | Status | Gate primário |
|---:|---|---|---|---|
| 1 | E-01 | Warmup de pipeline reduz p95 inicial | READY | p95 −20% sem regressão estável |
| 2 | E-02 | MultiMesh 200 reduz CPU p95 e melhora 1% low | READY | CPU p95 −30%; 1% low +5% |
| 3 | E-03 | Limite de luzes por relevância reduz GPU p95 | READY | GPU p95 −15%; erro visual ≤1/255 |
| 4 | E-04 | Batching 2D reduz draw calls | DESIGN_ONLY | contrato M07 + WO |
| 5 | E-05 | Input lag instrumentado com incerteza | DESIGN_ONLY | admissão #70 |

## Candidatos de módulos (não admitidos)

NEX-RD-05 oclusão, RD-06 pacing governor, RD-07 câmera isométrica, RD-08 orçamento de textura, RD-09 warmup de VFX, RD-10 input lag — todos `DESIGN_ONLY`; nenhum ganho medido.

**Regra:** este documento não declara originalidade nem ganho; apenas organiza hipóteses e critérios GO/NO_GO.

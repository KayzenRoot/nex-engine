# Checkpoint Delta · NEX-M06-FULL-ATLAS-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `75bf4811b696e2070475039cd50a2d7ae7913ee8`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06-FULL-ATLAS integrado:** 144 observações `performance.v1` dos sete bundles M09 e atlas agregado por bundle/célula.
2. **Cobertura:** preset-ab 6, proxy-scaling 18, m01-ab 18, res-scaling 18, interaction 24, cross-scene 48, interaction-200 12.
3. **Resultado:** 144/144 pacing; GPU p95 global 0.068–0.887 ms; pacing p95 4.199–4.301 ms; maior GPU share 21.05%.
4. **Sem nova medição, runtime ou mudança de contrato.** M06 bounded admission inalterada.
5. **Sem generalização:** sessão única em uma RTX 5050.

## O que NÃO muda

- M01–M05/M07–M08/M10–M12 permanecem como estão; nenhum outro parent é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-FULL-ATLAS-WO-001-EVIDENCE.md`
- `docs/benchmarks/m06/observations/m09-observations-full.v1.json`
- `docs/benchmarks/m06/m09-performance-atlas.v1.json`
- `tests/ci/test_m06_full_observations.py` e `tests/ci/test_m06_m09_atlas.py` (10 testes)

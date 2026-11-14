# Checkpoint Delta · NEX-M06-FULL-REFRESH-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `c7d6f7271b1bf4ef5aa2a7f60fd09a08784b78aa`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06-FULL-REFRESH integrado:** dataset completo com **156 observações** de **9 bundles** M09.
2. **Atlas:** GPU p95 0.068–1.55 ms (mediana 0.226), pacing 4.199–4.311 ms, maior GPU share 36.29%.
3. **Advisories:** 156, headroom 2.716–4.009 ms, maior GPU share 36.29%.
4. **Top cell:** `res-scaling-1440` / `ab-high` / 2560×1440 / 100 proxies / 1.547 ms.
5. **Saída curada de 12 observações/advisórios inalterada.**
6. **Sem nova medição ou mudança de bundle M09, contrato, modelo ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-FULL-REFRESH-WO-001-EVIDENCE.md`
- `docs/benchmarks/m06/observations/m09-observations-full.v1.json`
- `docs/benchmarks/m06/m09-performance-atlas.v1.json`
- `docs/benchmarks/m06/advisories-full.v1.json`

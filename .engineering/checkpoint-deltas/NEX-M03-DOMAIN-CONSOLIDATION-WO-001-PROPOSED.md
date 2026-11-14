# Checkpoint Delta · NEX-M03-DOMAIN-CONSOLIDATION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `0683631df4e047bfff2bf8a0c45dd6b0df9853dd`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03-DOMAIN-CONSOLIDATION integrado:** relatório `--domain` com grid de resolução + 200/1280 + 2560×1440.
2. **Resultado:** `ab-high`/1280×720 dentro de 2% em 100 e 200 proxies; 2560×1440 sem acertos; `within_2pct_total = 2`.
3. **Veredito:** `CALIBRATION_RESOLUTION_MATCH_ONLY` reforçado — robusto a proxies, não a resolução.
4. **Sem nova medição, mudança de modelo, GDScript, bundle M09, contrato ou ruleset.**
5. **Saída curada de 6 células inalterada.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-DOMAIN-CONSOLIDATION-WO-001-EVIDENCE.md`
- `docs/benchmarks/m03/budget-domain-boundary.v1.json`
- `docs/benchmarks/m03/BUDGET-DOMAIN-BOUNDARY.md`
- `tests/ci/test_m03_domain_boundary.py` (7 testes)

# Checkpoint Delta · NEX-PROVENANCE-INDEX-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `ee4e853d1506178d13e4f0c6632c39b1cd9895a1`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **NEX-PROVENANCE-INDEX integrado:** 57 entradas do checkpoint, PRs 112–241, 57 merge SHAs únicos.
2. **Auditoria:** todos os rótulos são `ADMIN_SOLO_NOT_INDEPENDENT`; nenhum `INDEPENDENT_APPROVED`.
3. **Enforcement:** builder cross-module com `--check` no job requerido.
4. **Sem alteração de checkpoint, admissão, medição, harness, contrato, modelo ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-PROVENANCE-INDEX-WO-001-EVIDENCE.md`
- `docs/benchmarks/provenance-index.v1.json`
- `docs/benchmarks/PROVENANCE-INDEX.md`
- `tests/ci/test_provenance_index.py` (6 testes)

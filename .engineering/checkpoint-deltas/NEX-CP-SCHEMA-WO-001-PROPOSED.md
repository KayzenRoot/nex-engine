# Checkpoint Delta · NEX-CP-SCHEMA-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `35b6b25ce317f8a6a8b53784dfaa70613de7c6b2`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **NEX-CP-SCHEMA integrado:** validador determinístico do `CHECKPOINT.json` no job requerido.
2. **Cobertura:** 61 blocos de proveniência; falha em SHA inválido, merge ausente, aprovação falsa, bloco de admissão ausente, merge duplicado e contagem incoerente.
3. **Enforcement:** validador cross-module no Fast Lane.
4. **Sem alteração de checkpoint, admissão, medição, harness, contrato, modelo ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M04/M05/M06/M09 seguem bounded admitted; M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-CP-SCHEMA-WO-001-EVIDENCE.md`
- `docs/benchmarks/tools/validate_checkpoint.py`
- `tests/ci/test_checkpoint_schema.py` (7 testes)

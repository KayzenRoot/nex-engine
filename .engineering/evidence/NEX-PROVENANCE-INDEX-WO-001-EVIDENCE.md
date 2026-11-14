# Evidence Bundle · NEX-PROVENANCE-INDEX-WO-001

**Status:** `AUDIT_ENABLER_EVIDENCE / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M09 #14 · **Base:** `ee4e853d1506178d13e4f0c6632c39b1cd9895a1`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** LOW

## Entregue

- `docs/benchmarks/tools/build_provenance_index.py` com `--check`.
- `docs/benchmarks/provenance-index.v1.json` e `PROVENANCE-INDEX.md`: **57 entradas**, PRs **112–241**, 57 merge SHAs únicos.
- `tests/ci/test_provenance_index.py` (6 testes) e enforcement cross-module no Fast Lane.
- WO/lock/evidência/delta.

## Resultado

- Todos os blocos do checkpoint com `pr` + `protectedMergeSha` estão indexados.
- Todos os merge SHAs são 40-hex e únicos; todos os PRs são inteiros positivos.
- Rótulos de auditoria: apenas `ADMIN_SOLO_NOT_INDEPENDENT`; nenhum `INDEPENDENT_APPROVED`.
- O índice declara explicitamente que o checkpoint é a autoridade e que a auditoria é solo.

## Verificação

- `--check` do builder PASS; teste de proveniência e enforcement verdes.
- Suítes: CI **527**, contratos **203**, telemetria **31** — OK.
- Nenhum checkpoint, bloco de admissão, medição, harness, cena, contrato, modelo ou ruleset alterado.

## O que não foi feito / não é alegado

- Nenhuma revisão independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
- Nenhuma nova medição ou mudança de estado de parent.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.

## Rollback

Remover builder, índice, teste, enforcement, WO/lock/evidência/delta e a entrada de checkpoint correspondente.

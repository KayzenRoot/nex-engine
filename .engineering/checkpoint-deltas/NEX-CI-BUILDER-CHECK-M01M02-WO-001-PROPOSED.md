# Checkpoint Delta · NEX-CI-BUILDER-CHECK-M01M02-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `4cec20142d4c464d10cc18fd28aa2c1121738d92`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **CI-BUILDER-CHECK estendido a M01/M02:** o job requerido `NEX Fast Lane / Batch Policy Tests` passa a executar 19 comandos `--check` (18 arquivos).
2. **Cobertura:** 2 M01/M02 + 1 M03 + 5 comandos M06 (4 arquivos) + 11 M09.
3. **Guard:** o teste falha se `build_manifest.py` ou `qa_ledger.py` deixarem de ser cobertos, se houver modo escrita ou se o job deixar de ser required context.
4. **Sem mudança de builder, manifesto, ledger, artefato, dado, contrato, medição ou ruleset.**
5. **Sem nova medição ou admissão de parent.**

## O que NÃO muda

- M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M01/M02/M03/M06/M09 seguem bounded admitted.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-CI-BUILDER-CHECK-M01M02-WO-001-EVIDENCE.md`
- `.github/workflows/nex-ci-fastlane.yml`
- `tests/ci/test_builder_check_enforcement.py` (5 testes)

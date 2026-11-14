# Checkpoint Delta · NEX-CI-BUILDER-CHECK-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `065a037d996e36fe62c35bb9fcc818f3dd91fa20`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **CI-BUILDER-CHECK integrado:** o job requerido `NEX Fast Lane / Batch Policy Tests` passa a executar 17 comandos `--check` dos builders M03/M06/M09.
2. **Cobertura:** 1 M03, 5 M06 (4 arquivos, com `--check` e `--check-full`) e 11 M09.
3. **Guard:** `tests/ci/test_builder_check_enforcement.py` falha se um builder novo não for listado, se houver modo de escrita ou se o job deixar de ser required context.
4. **Sem mudança de builder, artefato, dado, contrato, medição ou ruleset.**
5. **Sem nova medição ou admissão de parent.**

## O que NÃO muda

- M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M01/M02/M03/M06/M09 seguem bounded admitted.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-CI-BUILDER-CHECK-WO-001-EVIDENCE.md`
- `.github/workflows/nex-ci-fastlane.yml`
- `tests/ci/test_builder_check_enforcement.py` (5 testes)

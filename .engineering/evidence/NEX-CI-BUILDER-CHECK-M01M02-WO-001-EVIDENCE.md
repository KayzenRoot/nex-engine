# Evidence Bundle · NEX-CI-BUILDER-CHECK-M01M02-WO-001

**Status:** `CI_ENFORCEMENT_EVIDENCE / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M01 #6 · M02 #7 · M03 #8 · M06 #11 · M09 #14 · **Base:** `4cec20142d4c464d10cc18fd28aa2c1121738d92`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** LOW

## Entregue

- Dois comandos adicionais no step `Verify deterministic builders reproduce committed artifacts` do job requerido `NEX Fast Lane / Batch Policy Tests`: `docs/benchmarks/m01/tools/build_manifest.py --check` e `docs/benchmarks/m02/tools/qa_ledger.py --check`.
- Total: 19 comandos `--check` (18 arquivos) cobrindo M01/M02/M03/M06/M09.
- `tests/ci/test_builder_check_enforcement.py` atualizado para m01/m02 e contagens 18/19.
- WO/lock/evidência/delta correspondentes.

## Verificação

- `build_manifest.py --check` → `MANIFEST_OK artifacts=71`; `qa_ledger.py --check` → `QA_LEDGER_OK`, ambos em worktree LF limpo sobre `4cec2014`.
- 19/19 comandos passam; teste novo verde; suítes CI/contratos/telemetria verdes antes do squash.
- Nenhum ruleset, required context, builder, manifesto, ledger, artefato, contrato, dado ou medição alterado.

## O que não foi feito / não é alegado

- Nenhuma nova medição, renderização real, runtime, renderer, shader ou mudança de engine.
- Nenhum novo parent admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Remover os dois comandos do workflow, ajustar o teste de volta a 16/17, e remover WO/lock/evidência/delta e a entrada de checkpoint correspondente.

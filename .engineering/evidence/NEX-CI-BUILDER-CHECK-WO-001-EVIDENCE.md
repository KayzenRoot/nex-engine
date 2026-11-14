# Evidence Bundle · NEX-CI-BUILDER-CHECK-WO-001

**Status:** `CI_ENFORCEMENT_EVIDENCE / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M03 #8 · M06 #11 · M09 #14 · **Base:** `065a037d996e36fe62c35bb9fcc818f3dd91fa20`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Step `Verify deterministic builders reproduce committed artifacts` no job requerido `NEX Fast Lane / Batch Policy Tests` (`.github/workflows/nex-ci-fastlane.yml`).
- 17 comandos `--check`: 1 M03, 5 M06 (4 arquivos, incluindo `--check-full`) e 11 M09.
- `tests/ci/test_builder_check_enforcement.py`: 5 testes de cobertura, modo somente leitura, vínculo ao required context e contagem.
- WO/lock/evidência/delta correspondentes.

## Verificação

- Os 17 comandos passaram em worktree LF limpo sobre a base `065a037d`.
- Teste novo verde; suítes CI/contratos/telemetria verdes antes do squash.
- O step roda dentro do job já exigido pelo ruleset; nenhum ruleset ou required context foi alterado.
- `--check` não escreve: divergência entre builder e artefato commitado falha o check.

## O que não foi feito / não é alegado

- Nenhum builder, artefato, observação, atlas, contrato, dado ou medição foi alterado.
- Nenhuma nova medição, renderização real, runtime, renderer, shader ou mudança de engine.
- Nenhum novo parent admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Remover o step do workflow, o teste, WO/lock/evidência/delta e a entrada de checkpoint correspondente.

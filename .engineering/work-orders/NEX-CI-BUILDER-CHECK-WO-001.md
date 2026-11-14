# NEX-CI-BUILDER-CHECK-WO-001 | Enforcement de CI para builders determinísticos

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-14 para executar a ordem sugerida; quarto caminho é o enforcement de CI dos builders M03/M06/M09.
**Base:** `main` `065a037d996e36fe62c35bb9fcc818f3dd91fa20`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (gate de CI).
**Lock:** `.engineering/context-locks/NEX-CI-BUILDER-CHECK-WO-001-EXECUTION.json`.

## Objetivo

Fazer o check obrigatório `NEX Fast Lane / Batch Policy Tests` executar todos os builders determinísticos de M03/M06/M09 em modo `--check`, de forma que artefato commitado divergente do builder falhe a PR e a main. Não altera builders, artefatos, dados, contratos, medições ou ruleset.

## Escopo

- `.github/workflows/nex-ci-fastlane.yml`: novo step no job `policy-tests` existente, com os 17 comandos `--check`.
- `tests/ci/test_builder_check_enforcement.py`: cobertura de todos os builders `build_*.py`/`convert_*.py` dos três módulos, modo somente leitura e vínculo ao check obrigatório.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar qualquer builder, artefato, observação, atlas, contrato ou medição.
- Alterar o ruleset, o conjunto de required contexts ou o `ops/github/nex-main-ruleset.json`.
- Builders de M01/M02/M04/M05/M07/M08/M10–M12.
- Criar novos builders, novas medições ou admitir novos parents.
- Relaxar timeout, permissões, segurança, locks ou auditoria solo.

## DoD

- O job requerido executa 17 comandos `--check` (16 arquivos; `convert_m09_observations.py` cobre `--check` e `--check-full`).
- O teste falha se um builder novo não for listado, se algum comando não for `--check` ou se o job deixar de ser required context.
- Os 17 comandos passam em worktree LF limpo; suítes CI/contratos/telemetria verdes.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, builder falhando por artefato ou dado, necessidade de alterar medição/contrato/ruleset ou check vermelho → parar e registrar.

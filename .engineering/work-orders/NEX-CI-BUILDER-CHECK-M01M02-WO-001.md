# NEX-CI-BUILDER-CHECK-M01M02-WO-001 | Enforcement M01/M02 no check de builders

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005) após o enforcement M03/M06/M09 (PR #223); M01/M02 são bounded admitted desde NEX-ADR-0008.
**Base:** `main` `4cec20142d4c464d10cc18fd28aa2c1121738d92`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** LOW (extensão de step de CI já existente).
**Lock:** `.engineering/context-locks/NEX-CI-BUILDER-CHECK-M01M02-WO-001-EXECUTION.json`.

## Objetivo

Estender o step `Verify deterministic builders reproduce committed artifacts` do job requerido `NEX Fast Lane / Batch Policy Tests` para incluir os builders determinísticos já admitidos de M01 (`build_manifest.py`) e M02 (`qa_ledger.py`), fechando a lacuna de reprodutibilidade dos dois pipelines de referência.

## Escopo

- `.github/workflows/nex-ci-fastlane.yml`: dois comandos `--check` adicionais (19 no total).
- `tests/ci/test_builder_check_enforcement.py`: cobertura de m01/m02, contagens 18 arquivos / 19 comandos.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar builders, manifestos, ledger, artefatos, contratos, dados ou medições.
- Alterar ruleset, required contexts ou `ops/github/nex-main-ruleset.json`.
- Builders de M04–M05/M07–M08/M10–M12.
- Novas medições ou admissão de parents.

## DoD

- `build_manifest.py --check` e `qa_ledger.py --check` executam no job requerido.
- Teste cobre m01/m02 e falha se um builder novo não for listado ou usar modo escrita.
- 19/19 comandos passam em worktree LF limpo; suítes CI/contratos/telemetria verdes.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, builder falhando por artefato ou dado, necessidade de alterar medição/contrato/ruleset ou check vermelho → parar e registrar.

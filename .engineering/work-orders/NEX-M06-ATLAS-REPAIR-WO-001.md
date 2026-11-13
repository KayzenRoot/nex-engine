# NEX-M06-ATLAS-REPAIR-WO-001 | Reparação do atlas M06 (Sonar + bytecode)

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; reparação do incremento NEX-M06-BOTTLENECK-ATLAS-WO-001 imediatamente após a integração.
**Base:** `main` `aee4c15cf5bd912ea31fa36731cca55671776080`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M06-ATLAS-REPAIR-WO-001-EXECUTION.json` (24 fingerprints).

## Objetivo

Corrigir os 14 code smells introduzidos pelo builder do atlas e remover o arquivo `.pyc` rastreado acidentalmente, sem alterar o comportamento do builder, os artefatos `atlas.v1.json`/`ATLAS.md` ou os testes.

## Escopo

- `docs/benchmarks/m06/tools/build_atlas.py`: trocar appends consecutivos por `extend`, usar `\d`, extrair `_verify_entry` e `_reject_non_finite`.
- `docs/benchmarks/m06/tools/.gitignore`: ignorar `__pycache__/` e `*.pyc`.
- Remoção de `docs/benchmarks/m06/tools/__pycache__/build_atlas.cpython-313.pyc`.
- Evidência e este WO/lock.

## Fora de escopo

- Alterar atlas, MD, testes, contrato, capturas, engine, CI ou `project.godot`.
- M06 parent admission.

## DoD

- `--check` continua passando com os artefatos byte-idênticos.
- 12 testes do atlas verdes; suítes completas verdes em worktree LF limpo.
- Sonar sem os 14 achados novos; nenhum `.pyc` rastreado.
- PR com checks verdes e squash protegido.

## STOP

- Qualquer mudança de saída do atlas, check vermelho ou hash divergente → parar e registrar.

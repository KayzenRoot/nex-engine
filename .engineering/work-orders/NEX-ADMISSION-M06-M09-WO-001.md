# NEX-ADMISSION-M06-M09-WO-001 | Admissão bounded dos pipelines de evidência

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-14 para executar os três próximos caminhos, incluindo a admissão bounded M06/M09.
**Base:** `main` `8ed41bafaf19cff52da9250784f78c3d608ac504`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (governança).
**Lock:** `.engineering/context-locks/NEX-ADMISSION-M06-M09-WO-001-EXECUTION.json`.

## Objetivo

Registrar a admissão bounded de M06 (#11) e M09 (#14) como `BOUNDED_ADMITTED_EVIDENCE_PIPELINE`, cobrindo contratos, protótipos, harnesses, evidência, relatórios e testes já verificados. A admissão não autoriza runtime, hub, engine, renderer, shaders, cenas de produção ou claims de qualidade/FPS.

## Escopo

- ADR `NEX-ADR-0006` e ledger `NEX-D-016`.
- Atualização de `AGENTS.md`, `SCOPE.md` e `CHECKPOINT.json/md` com o status bounded.
- `tests/ci/test_m06_m09_admission.py`: consistência documental e escopo.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Qualquer mudança de código de engine, renderer, shaders, cenas, hub, `project.godot` ou CI.
- Aplicação de presets no runtime, integração de performance ou generalização.
- Admissão de M01–M05/M07–M08/M10–M12.
- Relaxamento de checks, locks, segurança, ruleset ou auditoria solo.

## DoD

- ADR e ledger promovidos juntos, com escopo admitido e exclusões explícitas.
- Checkpoint com status `M06_M09_BOUNDED_ADMITTED_...` e SHA de admissão.
- `AGENTS.md` e `SCOPE.md` apontam para o novo status e mantêm os demais parents NOT_ADMITTED.
- Teste de consistência verde; suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Divergência de base/HEAD, status contraditório, tentativa de admissão além do escopo de evidência ou check vermelho → parar e registrar.

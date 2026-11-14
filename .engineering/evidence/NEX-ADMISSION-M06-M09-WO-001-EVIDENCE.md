# Evidence Bundle · NEX-ADMISSION-M06-M09-WO-001

**Status:** `GOVERNANCE_EVIDENCE / BOUNDED_ADMITTED_EVIDENCE_PIPELINE / ADMIN_SOLO_NOT_INDEPENDENT`
**Issues:** M06 #11 · M09 #14 · **Base:** `8ed41bafaf19cff52da9250784f78c3d608ac504`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `NEX-ADR-0006-M06-M09-BOUNDED-ADMISSION.md` e `NEX-D-016`.
- `AGENTS.md` com status corrente e seção histórica marcada.
- `SCOPE.md` com admissão bounded e seção histórica marcada.
- `CHECKPOINT.json/md` com status `M06_M09_BOUNDED_ADMITTED_M01_M05_M07_M08_M10_M12_NOT_ADMITTED`.
- `tests/ci/test_m06_m09_admission.py`: 6 testes de consistência.

## Escopo admitido

- M06: `performance.v1`, atlas S05, observações M09, advisórios, builders e testes.
- M09: `preset_pack.v1`, resolver, harness A/B, todos os bundles de medição, atlas, builders e testes.

## Escopo excluído

- Runtime, hub, engine, renderer, shaders, cenas de produção e `project.godot`.
- Aplicação de presets, generalização de performance/qualidade e claims de FPS.
- M01–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum relaxamento de CI, segurança, testes, locks ou ruleset.

## Verificação

- ADR, ledger e checkpoint coerentes; teste de consistência verde.
- `parentM06`/`parentM09` atualizados para `BOUNDED_ADMITTED_EVIDENCE_PIPELINE` nos blocos históricos.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança de código de engine, renderer, shaders, cenas, hub, `project.godot` ou CI.
- Nenhuma nova medição.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
- A admissão não torna M06/M09 produtos completos nem admite os demais parents.

## Rollback

Reverter ADR, ledger, AGENTS, SCOPE, checkpoint, teste e delta/WO/lock correspondentes.

# Evidence Bundle · NEX-ADMISSION-M01-M02-WO-001

**Status:** `GOVERNANCE_EVIDENCE / BOUNDED_ADMITTED_REFERENCE_PIPELINE / ADMIN_SOLO_NOT_INDEPENDENT`
**Issues:** M01 #6 · M02 #7 · **Base:** `e729774583eb8ce3b75271aea66589bb9e04a587`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `NEX-ADR-0008-M01-M02-BOUNDED-ADMISSION.md` e `NEX-D-018`.
- `AGENTS.md` com status M01/M02/M03/M06/M09 e seção histórica preservada.
- `SCOPE.md` com admissão M01/M02/M03/M06/M09.
- `CHECKPOINT.json/md` com status `M01_M02_M03_M06_M09_BOUNDED_ADMITTED_...`.
- `tests/ci/test_m01_m02_bounded_admission.py`: 7 testes.

## Escopo admitido

- M01: contratos, cenas base de referência, benchmark docs, baseline/QA e testes M01.
- M02: contratos, protótipos render3d (câmera, depth composition, profiles, sightline, temporal), QA docs e testes.

## Escopo excluído

- Runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção, renderização real.
- `nex_modules/render2d/**`/M07, generalização e claims de FPS.
- M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum relaxamento de CI, segurança, testes, locks ou ruleset.

## Verificação

- ADR/ledger/checkpoint coerentes; `parentM01`/`parentM02` atualizados.
- Teste de consistência verde; suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança de código de engine, renderer, shaders, cenas, hub, `project.godot` ou CI.
- Nenhuma nova medição ou renderização real.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
- M01/M02 não são produtos completos; a admissão é de referência/análise.

## Rollback

Reverter ADR, ledger, AGENTS, SCOPE, checkpoint, teste e delta/WO/lock correspondentes.

# Evidence Bundle · NEX-ADMISSION-M03-WO-001

**Status:** `GOVERNANCE_EVIDENCE / BOUNDED_ADMITTED_ANALYSIS_PIPELINE / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** M03 #8 · **Base:** `51110ff02eb2c542832b6290a98fdc5f979b58a9`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `NEX-ADR-0007-M03-BOUNDED-ADMISSION.md` e `NEX-D-017`.
- `AGENTS.md` com status M03/M06/M09 e seção histórica preservada.
- `SCOPE.md` com admissão M03/M06/M09.
- `CHECKPOINT.json/md` com status `M03_M06_M09_BOUNDED_ADMITTED_...`.
- `tests/ci/test_m03_bounded_admission.py`: 7 testes.

## Escopo admitido

- Contrato `lighting.v1` e ownership.
- Light rig planner, shadow stability analyzer e light budget arbiter.
- Validação do modelo contra M09, snapshot, builders e testes.

## Escopo excluído

- Runtime, renderer, shaders, cenas, hub, `project.godot`, gameplay.
- Implementação real de luz/sombra/GI, generalização e claims de FPS.
- M01–M02, M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum relaxamento de CI, segurança, testes, locks ou ruleset.

## Verificação

- ADR/ledger/checkpoint coerentes; `parentM03` atualizado em todos os blocos M03.
- Teste de consistência verde; suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança de código de engine, renderer, shaders, cenas, hub, `project.godot` ou CI.
- Nenhuma nova medição.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
- M03 não é produto completo; a admissão é apenas de análise.

## Rollback

Reverter ADR, ledger, AGENTS, SCOPE, checkpoint, teste e delta/WO/lock correspondentes.

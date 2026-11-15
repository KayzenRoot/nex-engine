# Evidence Bundle · NEX-ADMISSION-M04-M05-WO-001

**Status:** `GOVERNANCE_EVIDENCE / BOUNDED_ADMITTED_MATERIALS_VFX_PIPELINES / ADMIN_SOLO_NOT_INDEPENDENT`
**Issues:** M04 #9 · M05 #10 · **Base:** `5f801c09ca4148fb9712f84cfd638bd80f3a4372`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `NEX-ADR-0009-M04-M05-BOUNDED-ADMISSION.md` e `NEX-D-019`.
- `AGENTS.md` com status M01/M02/M03/M04/M05/M06/M09 e seção histórica preservada.
- `SCOPE.md` com admissão M01/M02/M03/M04/M05/M06/M09.
- `CHECKPOINT.json/md` com status `M01_M02_M03_M04_M05_M06_M09_BOUNDED_ADMITTED_...`.
- `tests/ci/test_m04_m05_bounded_admission.py`: 7 testes; testes de admissão existentes ajustados para o novo status.

## Escopo admitido

- M04: contrato `material.v1`, ownership, docs, protótipo `texturebudget`, smoke headless, testes e evidência.
- M05: contrato `spellfx.v1`, ownership, docs, protótipo `fxbudget`, smoke headless, testes e evidência.

## Escopo excluído

- Criação de material/shader/textura/atlas/partícula/emissor/luz/decal.
- Decodificação de textura, atlas packing, criação de partículas e integração de renderização.
- Runtime, hub, engine, renderer, shaders, `project.godot`, gameplay e cenas de produção.
- Performance, FPS, qualidade visual, game feel e licensing claims.
- M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum relaxamento de CI, segurança, testes, locks ou ruleset.

## Verificação

- ADR/ledger/checkpoint coerentes; `parentM04`/`parentM05` atualizados.
- Teste de consistência verde; suítes completas em worktree LF limpo: CI **534**, contratos **203**, telemetria **31**.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança de código de engine, renderer, shaders, cenas, hub, `project.godot` ou CI.
- Nenhuma criação de material/textura/partícula, renderização real ou medição.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
- M04/M05 não são produtos completos; a admissão é de contratos/protótipos determinísticos.

## Rollback

Reverter ADR, ledger, AGENTS, SCOPE, checkpoint, teste e delta/WO/lock correspondentes.

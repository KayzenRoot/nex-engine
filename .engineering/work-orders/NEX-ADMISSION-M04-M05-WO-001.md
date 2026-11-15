# NEX-ADMISSION-M04-M05-WO-001 | Admissão bounded dos pipelines M04/M05

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-14 ("faça isso tudo de uma vez, autorizo tudo"); M04/M05 são o próximo par bounded admitido.
**Base:** `main` `5f801c09ca4148fb9712f84cfd638bd80f3a4372`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (governança).
**Lock:** `.engineering/context-locks/NEX-ADMISSION-M04-M05-WO-001-EXECUTION.json`.

## Objetivo

Registrar M04 (#9) e M05 (#10) como `BOUNDED_ADMITTED_MATERIALS_PIPELINE` e `BOUNDED_ADMITTED_VFX_PIPELINE`, cobrindo contratos `material.v1`/`spellfx.v1`, documentação, protótipos determinísticos de orçamento de texturas/FX, smoke headless, testes e evidência já verificados. Não autoriza criação de material/shader/textura/partícula, integração de renderização, runtime ou claims de performance/qualidade.

## Escopo

- ADR `NEX-ADR-0009` e ledger `NEX-D-019`.
- Atualização de `AGENTS.md`, `SCOPE.md` e `CHECKPOINT.json/md`.
- `tests/ci/test_m04_m05_bounded_admission.py` e ajustes nos testes de admissão existentes.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Criação de material, shader, textura, atlas, partícula, emissor, luz ou decal.
- Decodificação de textura, atlas packing, criação de partículas, integração de renderização.
- Runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção.
- Admissão de M07–M08/M10–M12.
- Relaxamento de checks, locks, segurança, ruleset ou auditoria solo.

## DoD

- ADR/ledger/checkpoint coerentes, com escopo admitido e exclusões.
- `parentM04`/`parentM05` atualizados nos blocos correspondentes.
- Teste de consistência verde; suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Base/HEAD divergente, status contraditório, admissão além do escopo de contratos/protótipos ou check vermelho → parar e registrar.

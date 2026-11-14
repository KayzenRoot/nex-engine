# NEX-ADMISSION-M03-WO-001 | Admissão bounded da análise M03

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-14 para executar a ordem sugerida; M03 é o segundo parent admitido bounded.
**Base:** `main` `51110ff02eb2c542832b6290a98fdc5f979b58a9`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (governança).
**Lock:** `.engineering/context-locks/NEX-ADMISSION-M03-WO-001-EXECUTION.json`.

## Objetivo

Registrar M03 (#8) como `BOUNDED_ADMITTED_ANALYSIS_PIPELINE`, cobrindo contrato `lighting.v1`, light rig, shadow stability, light budget e validação do modelo contra M09. Não autoriza runtime, renderer, shaders, cenas, hub, `project.godot` ou claims de performance/qualidade.

## Escopo

- ADR `NEX-ADR-0007` e ledger `NEX-D-017`.
- Atualização de `AGENTS.md`, `SCOPE.md` e `CHECKPOINT.json/md`.
- `tests/ci/test_m03_bounded_admission.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Código de engine/renderer/shaders/cenas/hub/`project.godot`/CI.
- Implementação real de luz/sombra/GI, generalização ou FPS.
- Admissão de M01–M02/M04–M05/M07–M08/M10–M12.
- Relaxamento de checks, locks, segurança, ruleset ou auditoria solo.

## DoD

- ADR/ledger/checkpoint coerentes, com escopo admitido e exclusões.
- `parentM03` atualizado nos blocos M03 do checkpoint.
- Teste de consistência verde; suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Base/HEAD divergente, status contraditório, admissão além do escopo de análise ou check vermelho → parar e registrar.

# NEX-ADMISSION-M01-M02-WO-001 | Admissão bounded das referências M01/M02

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-14 para executar a ordem sugerida; M01/M02 são o terceiro parent admitido bounded.
**Base:** `main` `e729774583eb8ce3b75271aea66589bb9e04a587`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (governança).
**Lock:** `.engineering/context-locks/NEX-ADMISSION-M01-M02-WO-001-EXECUTION.json`.

## Objetivo

Registrar M01 (#6) e M02 (#7) como `BOUNDED_ADMITTED_REFERENCE_PIPELINE`, cobrindo contratos, cenas base de referência, docs/QA, protótipos de câmera/profundidade/perfis/sightline/temporal e testes. Não autoriza runtime, hub, renderer, shaders, `project.godot`, engine, gameplay, cenas de produção ou claims de performance/qualidade.

## Escopo

- ADR `NEX-ADR-0008` e ledger `NEX-D-018`.
- Atualização de `AGENTS.md`, `SCOPE.md` e `CHECKPOINT.json/md`.
- `tests/ci/test_m01_m02_bounded_admission.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Código de engine/renderer/shaders/hub/`project.godot`/CI.
- Renderização real, gameplay, cenas de produção, `nex_modules/render2d/**`/M07.
- Admissão de M04–M05/M07–M08/M10–M12.
- Relaxamento de checks, locks, segurança, ruleset ou auditoria solo.

## DoD

- ADR/ledger/checkpoint coerentes, com escopo admitido e exclusões.
- `parentM01`/`parentM02` atualizados nos blocos correspondentes.
- Teste de consistência verde; suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Base/HEAD divergente, status contraditório, admissão além do escopo de referência/análise ou check vermelho → parar e registrar.

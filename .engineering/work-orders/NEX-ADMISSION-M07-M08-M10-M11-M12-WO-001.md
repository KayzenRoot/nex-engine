# NEX-ADMISSION-M07-M08-M10-M11-M12-WO-001 | Admissão bounded dos pipelines restantes

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-15 ("faça as 3 por favor"), terceiro caminho; M07/M08/M10/M11/M12 são os últimos parents `NOT_ADMITTED`.
**Base:** `main` `8bb4bef1b216e71eafe0dc83efe897bb926530ce`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (governança).
**Lock:** `.engineering/context-locks/NEX-ADMISSION-M07-M08-M10-M11-M12-WO-001-EXECUTION.json`.

## Objetivo

Registrar M07 (#12), M08 (#13), M10 (#15), M11 (#16) e M12 (#17) como `BOUNDED_ADMITTED_RENDER2D_PIPELINE`, `BOUNDED_ADMITTED_COMPOSITION_PIPELINE`, `BOUNDED_ADMITTED_ANIMATION_PIPELINE`, `BOUNDED_ADMITTED_ASSET_PIPELINE` e `BOUNDED_ADMITTED_IDENTITY_PIPELINE`, cobrindo contratos, documentação, protótipos determinísticos, smoke headless, testes e evidência já verificados. Com isso, todos os parents M01–M12 ficam bounded admitted em referência/análise/evidência.

## Escopo

- ADR `NEX-ADR-0010` e ledger `NEX-D-020`.
- Atualização de `AGENTS.md`, `SCOPE.md` e `CHECKPOINT.json/md`.
- `tests/ci/test_m07_m08_m10_m11_m12_bounded_admission.py` e ajustes nos testes de admissão existentes e no validador de schema.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção.
- Renderização real, geração de assets, importação/cozimento, aprovação de marca, liberação de licenças.
- Claims de FPS, qualidade, game feel, performance ou ganho.
- Relaxamento de checks, locks, segurança, ruleset ou auditoria solo.

## DoD

- ADR/ledger/checkpoint coerentes; todos os parent fields atualizados.
- Status `ALL_PARENTS_BOUNDED_ADMITTED_M01_..._M12`; nenhum parent `NOT_ADMITTED`.
- Teste de consistência verde; suítes completas verdes em worktree LF limpo.
- Validador de schema e índice de proveniência coerentes.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Base/HEAD divergente, status contraditório, admissão além de contratos/protótipos ou check vermelho → parar e registrar.

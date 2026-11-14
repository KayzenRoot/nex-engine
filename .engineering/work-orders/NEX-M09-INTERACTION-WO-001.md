# NEX-M09-INTERACTION-WO-001 | Interação proxies × resolução

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `3af467648b0b8b7831fb99003a9a16e583553fe7`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-INTERACTION-WO-001-EXECUTION.json`.

## Objetivo

Medir a interação entre contagem de proxies e resolução no custo do `ab-low` → `ab-high` na cena M01 `arena_combat`: 50/100 proxies × 960×540/1920×1080 × 2 presets × 3 repetições = 24 capturas reais com viewport nativo. O bucket inferior é 50 porque a cena base `arena_combat` já tem 34 meshes; 25 exigiria remover geometria, o que está fora de escopo.

## Escopo

- `nex_bench/scenes/preset_ab/**`: uso dos hooks existentes (`NEX_PRESET_AB_PROXY_COUNT`, `WIDTH/HEIGHT`, `NATIVE_RESOLUTION`); sem mudança de engine.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction/**`: 24 capturas, 24 validações, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório `interaction.v1.json` / `INTERACTION-REPORT.md` e builder.
- `tests/ci/test_interaction.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- 200 proxies, 2560×1440 ou outros hardwares.
- Claims de FPS de jogo, qualidade ou ganho universal.
- M09 parent admission.

## DoD

- 24 capturas COMPLETE/validadas com proxies (50/100), resolução, scene/layout e viewport corretos.
- Deltas high vs low por célula e leitura de interação (proxies × resolução).
- Relatório reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Viewport/proxy divergir, captura inválida ou validador rejeitar → parar e registrar.

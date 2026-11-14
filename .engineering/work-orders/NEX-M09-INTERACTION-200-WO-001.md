# NEX-M09-INTERACTION-200-WO-001 | Interação com 200 proxies

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `c1b73743c0c95d9fb8867079cb91fb74cfc03d49`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-INTERACTION-200-WO-001-EXECUTION.json`.

## Objetivo

Medir 200 proxies × 960×540/1920×1080 × 2 presets × 3 repetições na cena `arena_combat` (12 capturas) para verificar se o padrão pixel-bound observado em 50/100 proxies se mantém no limite superior de proxies.

## Escopo

- `nex_bench/scenes/preset_ab/**`: uso dos hooks existentes; sem mudança de engine.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction-200/**`: 12 capturas, 12 validações, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório `interaction-200.v1.json` / `INTERACTION-200-REPORT.md` e builder.
- `tests/ci/test_interaction_200.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- Re-medir 50/100 proxies; a comparação usa o relatório `interaction.v1.json` já integrado.
- 2560×1440 ou outros hardwares.
- Claims de FPS de jogo, qualidade ou ganho universal.
- M09 parent admission.

## DoD

- 12 capturas COMPLETE/validadas com proxies 200, resolução, scene/layout e viewport corretos.
- Deltas high vs low por resolução e comparação documentada com 50/100.
- Relatório reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Viewport/proxy divergir, captura inválida ou validador rejeitar → parar e registrar.

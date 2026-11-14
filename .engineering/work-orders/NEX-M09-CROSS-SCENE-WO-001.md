# NEX-M09-CROSS-SCENE-WO-001 | Interação em três cenas M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-CROSS-SCENE-WO-001-EXECUTION.json`.

## Objetivo

Testar se o padrão de interação proxies × resolução observado em `arena_combat` se repete em `corridor_static` e `dense_city`: 2 cenas × 50/100 proxies × 960×540/1920×1080 × 2 presets × 3 repetições = 48 capturas reais com viewport nativo.

## Escopo

- `nex_bench/scenes/preset_ab/**`: uso dos hooks existentes; sem mudança de engine.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-cross-scene/**`: 48 capturas, 48 validações, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório `cross-scene.v1.json` / `CROSS-SCENE-REPORT.md` e builder.
- `tests/ci/test_cross_scene.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- `arena_combat` (já coberta), 200 proxies, 2560×1440 ou outros hardwares.
- Claims de FPS de jogo, qualidade ou ganho universal.
- M09 parent admission.

## DoD

- 48 capturas COMPLETE/validadas com cena, proxies, resolução, layout e viewport corretos.
- Deltas high vs low por cena/célula e comparação do padrão com `arena_combat`.
- Relatório reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Cena não carregar, viewport/proxy divergir, captura inválida ou validador rejeitar → parar e registrar.

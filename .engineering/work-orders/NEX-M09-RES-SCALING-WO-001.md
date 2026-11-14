# NEX-M09-RES-SCALING-WO-001 | Escala de resolução do custo de preset

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `f796de1445ff3147b87d8e7a3afe08e83a9284a5`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-RES-SCALING-WO-001-EXECUTION.json`.

## Objetivo

Medir como o custo GPU do `ab-low` → `ab-high` escala com a resolução no workload M01 `arena_combat` (100 meshes). Resoluções 16:9: 960×540, 1280×720 e 1920×1080 (máxima 16:9 suportada pelo display de 2560×1080). 3 repetições por preset por resolução, 18 capturas reais.

## Escopo

- `nex_bench/scenes/preset_ab/**`: validação/testes do uso de `NEX_PRESET_AB_WIDTH/HEIGHT`; sem mudança de engine.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling/**`: 18 capturas, 18 validações, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório `res-scaling.v1.json` / `RES-SCALING-REPORT.md` e builder.
- `tests/ci/test_res_scaling.py` e ajuste opcional em `_preset_ab_support.py` para conferir viewport.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- 2560×1440 ou resoluções acima do display; generalização para outros hardwares.
- Claims de FPS de jogo, qualidade ou ganho universal.
- M09 parent admission.

## DoD

- 18 capturas COMPLETE/validadas com viewport declarado e scene/layout/proxy corretos.
- Deltas high vs low por resolução e escala 960×540→1920×1080 por preset.
- Relatório reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Viewport divergir do solicitado, captura inválida, A/A instável acima do esperado ou validador rejeitar → parar e registrar.

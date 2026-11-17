# NEX-M09-FINAL-REFERENCE-WO-001 | Fechamento das ferramentas de editor M09

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0020` / `NEX-D-031`; instrução do Owner de 2026-11-17 para finalizar o M09 com ferramentas determinísticas, sem paridade com PoE2.
**Base:** `main` `371ca4ab4a5f70debc96e84bba55aba3870fc9cf`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (ferramentas headless e fixtures).
**Lock:** `.engineering/context-locks/NEX-M09-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M09 como ferramentas de editor de referência: PresetResolver, PerfLint, ImportGuard e BenchmarkRecipe, com fixtures determinísticas, smoke headless, relatório/gate e fechamento de #14.

## Escopo

- `nex_modules/tools/editor_lab/perf_lint.gd`, `import_guard.gd`, `recipe_builder.gd`, `smoke.gd`, `project.godot`, `main.tscn` e `fixtures/`.
- Evidence `nex_modules/tools/editor_lab/evidence/m09-editor-smoke-2026-11-17.json`.
- `docs/benchmarks/m09/tools/build_m09_editor_tools.py`, `EDITOR-TOOLS.md` e `editor-tools.v1.json`.
- `docs/benchmarks/m09/M09-FINAL-GATE.md`.
- `tests/ci/test_m09_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #14.

## Fora de escopo

- Importação real, escrita/overwrite de assets, import/cook pipeline.
- Rendering, shader, cena de produção, editor core, `project.godot` principal.
- M10–M12, gameplay, rede, cloud, assets de terceiros.
- FPS, frame-time, VRAM, qualidade, paridade com PoE2.

## DoD

- PresetResolver **50 checks**; editor smoke **42 checks**; total **92 checks**.
- PerfLint: **13 findings** (4 errors, 9 warns), 12 códigos distintos.
- ImportGuard: **1 accepted / 3 rejected / 2 noop / 1 conflict**, sem escrita.
- BenchmarkRecipe: `m09-corridor_static-ab-high-4101`, driver vulkan, 3 runs.
- 4 fixtures determinísticas; 0 assets de terceiros.
- Builder `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issue #14 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, fixture ausente, check vermelho, escrita de asset, claim de paridade com PoE2 ou generalização → parar e registrar.

# NEX-M04-M05-ASSET-KIT-WO-001 | Kit PBR M04 e dataset de orçamento M05

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-15 ("vamos continuar faça as 3 por favor") para trabalho de feature M04/M05; `NEX-ADR-0011` / `NEX-D-021` estendem o escopo bounded sem mudar o status dos parents.
**Base:** `main` `99437b22e94a6494eaef801872bb8fd0c79c0f1a`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (geração determinística de assets não-rendering).
**Lock:** `.engineering/context-locks/NEX-M04-M05-ASSET-KIT-WO-001-EXECUTION.json`.

## Objetivo

Entregar duas extensões reais e não-rendering: (1) um kit PBR procedural M04 com 12 texturas PNG determinísticas, quatro materiais `StandardMaterial3D` e uma observação `material.v1`, carregável por `ResourceLoader` headless; (2) um dataset M05 de três arquétipos de encontro analisados pelo `FXBudgetPlanner`, exercitando `FIT`, `TIGHT` e `OVER_BUDGET` com plano de redução.

## Escopo

- `nex_modules/materials/kit/**`: `project.godot`, `main.tscn`, `validate_kit.gd`, 12 PNGs, 4 `.tres`, `kit.v1.json`, `README.md`, `.gitignore` e evidência de carregamento headless.
- `docs/benchmarks/m04/tools/build_material_kit.py` e `docs/benchmarks/m04/MATERIAL-KIT.md`.
- `nex_modules/vfx/fxbudget/dataset.gd` e `nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json`.
- `docs/benchmarks/m05/tools/build_fx_budget_dataset.py`, `docs/benchmarks/m05/fx-budget-dataset.v1.json` e `FX-BUDGET-DATASET.md`.
- `tests/ci/test_material_kit.py`, `tests/ci/test_fx_budget_dataset.py` e `tests/ci/test_m04_m05_asset_kit_admission.py`.
- `.github/workflows/nex-ci-fastlane.yml`: enforcement dos dois builders; `test_builder_check_enforcement.py`.
- `NEX-ADR-0011`, `NEX-D-021`, `AGENTS.md`, `SCOPE.md`, `CHECKPOINT.json`, WO/lock/evidência/delta.

## Fora de escopo

- Shader customizado, `ShaderMaterial`, compilação de shader, renderer, integração/aplicação em cena, rendering ou GPU execution.
- Runtime, hub, engine, `project.godot` principal, gameplay, cenas de produção.
- Partículas/emissores/luzes/decais reais; decodificação/compressão/atlas packing; pipeline de import/cook de produção.
- Claims de FPS, frame-time, VRAM, overdraw, qualidade visual, game feel ou generalização.
- Novos parents ou mudança de status dos parents.

## DoD

- 12 PNGs 128×128 decodificáveis, com SHA-256 estável; 4 `.tres` carregados headless com 28 checks.
- `kit.v1.json` conforme `material.v1`, com `performance` e `provenance` explicitamente `UNAVAILABLE`.
- Dataset M05: `skirmish` FIT (484 partículas), `elite` TIGHT (1047/1100), `boss` OVER_BUDGET (2753/2000) com plano de 3 passos e projeção 1834.
- Builders `--check` reproduzem todos os bytes; CI enforcement 27 arquivos / 30 checks.
- Suíte CI completa verde; evidência, ADR/ledger/WO/lock/delta e checkpoint.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, PNG não determinístico, `.tres` que não carrega, dataset inválido, divergência de builder, check vermelho ou tentativa de rendering/claim de qualidade → parar e registrar.

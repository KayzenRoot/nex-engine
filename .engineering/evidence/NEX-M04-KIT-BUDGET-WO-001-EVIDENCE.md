# Evidence Bundle · NEX-M04-KIT-BUDGET-WO-001

**Status:** `BUDGET_PLANNING_EVIDENCE / NON_RENDERING / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M04 #9 · **Base:** `873f4a7d05d3b70912a5112089e3ebfbf068703c`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/materials/texturebudget/kit_budget.gd`: SceneTree headless que lê o kit por caminho absoluto e chama o `TextureBudgetPlanner`.
- `nex_modules/materials/texturebudget/evidence/kit-budget-2026-11-15.json`.
- `docs/benchmarks/m04/tools/build_kit_budget.py`, `kit-budget.v1.json` e `KIT-BUDGET.md`.
- `tests/ci/test_kit_budget.py` (6 testes); enforcement no Fast Lane (28 arquivos / 31 checks).
- WO/lock/evidência/delta e checkpoint.

## Resultado

- Veredito **FIT** para 4 materiais e 12 texturas únicas.
- 0 refs duplicadas; 1.048.572 bytes decodificados/deduplicados.
- Atlas: 12 tiles de 256 disponíveis; pressão **0.047**.
- Nenhum finding do planner; `kit_sha256` confere com o `kit.v1.json` commitado.
- Nenhuma textura decodificada, comprimida, empacotada, importada ou renderizada.

## Verificação

- `build_kit_budget.py --check`: `M04_KIT_BUDGET_CHECK_PASS: 1 runs`.
- Suíte CI completa e 31/31 comandos de builder/validator verdes antes da PR.
- Nenhum contrato, planner, kit, cena, preset, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhum rendering, GPU, FPS, frame-time, VRAM, overdraw ou qualidade visual.
- Nenhuma compressão, atlas packing ou pipeline de import/cook.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter o script/evidência, builder/relatórios, teste, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.

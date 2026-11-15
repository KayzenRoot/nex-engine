# NEX-M04-KIT-BUDGET-WO-001 | Orçamento do kit M04 pelo planejador integrado

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0011` / `NEX-D-021` (kit M04 não-rendering); instrução contínua do Owner de 2026-11-15.
**Base:** `main` `873f4a7d05d3b70912a5112089e3ebfbf068703c`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (análise determinística de orçamento, sem rendering).
**Lock:** `.engineering/context-locks/NEX-M04-KIT-BUDGET-WO-001-EXECUTION.json`.

## Objetivo

Alimentar o `TextureBudgetPlanner` integrado com a observação `material.v1` do kit M04 e produzir um relatório determinístico de orçamento de texturas, provando que o kit é `FIT` sem decodificar, comprimir, empacotar ou renderizar texturas.

## Escopo

- `nex_modules/materials/texturebudget/kit_budget.gd`: SceneTree headless que lê o kit por caminho absoluto e chama o planner.
- `nex_modules/materials/texturebudget/evidence/kit-budget-2026-11-15.json`.
- `docs/benchmarks/m04/tools/build_kit_budget.py`, `docs/benchmarks/m04/kit-budget.v1.json` e `KIT-BUDGET.md`.
- `tests/ci/test_kit_budget.py`; enforcement no workflow e contagem 28 arquivos / 31 checks.
- WO/lock/evidência/delta e checkpoint.

## Fora de escopo

- Decodificação, compressão, atlas packing, import/cook ou rendering de textura.
- Alterar o kit, o planner, o contrato `material.v1`, cenas, presets, renderer ou shaders.
- Claims de FPS, frame-time, VRAM, qualidade ou ganho.
- Novos parents ou mudança de status.

## DoD

- Planner retorna `FIT` para 4 materiais, 12 texturas únicas, 0 duplicatas, 1.048.572 bytes e pressão de atlas 0.047.
- Nenhum finding; `kit_sha256` e `source_sha` conferidos pelo builder.
- `build_kit_budget.py --check` reproduz JSON/Markdown; CI 28/31.
- Suíte CI completa verde; PR protegida e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, kit/planner alterado, veredito diferente de FIT sem explicação, builder divergente ou check vermelho → parar e registrar.

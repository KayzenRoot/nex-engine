# NEX-M08-SCENE-COMPOSITION-WO-001 | Composição 2.5D sobre análise M02

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** M08 `BOUNDED_ADMITTED_COMPOSITION_PIPELINE` (`NEX-ADR-0010` / `NEX-D-020`); instrução contínua do Owner de 2026-11-15.
**Base:** `main` `d218525cbd7cd84b5c69f5e52577a6244f8733b6`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (planejamento determinístico, sem camada/viewport/shader/rendering).
**Lock:** `.engineering/context-locks/NEX-M08-SCENE-COMPOSITION-WO-001-EXECUTION.json`.

## Objetivo

Alimentar o `CompositionPlanner` integrado com a análise M02 das três cenas M01 e produzir planos 2.5D determinísticos de quatro camadas com entidades críticas player/threat, reportando conflitos de z-fight do plano 3D base sem criar camada, viewport, shader, cena ou renderer.

## Escopo

- `nex_modules/render2_5d/composition/scene_composition.gd`: lê o manifesto e os três JSONs M02, valida hashes e chama o planner.
- `nex_modules/render2_5d/composition/evidence/scene-composition-2026-11-15.json`.
- `docs/benchmarks/m08/tools/build_scene_composition.py`, `scene-composition.v1.json` e `SCENE-COMPOSITION.md`.
- `tests/ci/test_scene_composition.py`; enforcement no workflow e contagem 31 arquivos / 34 checks.
- WO/lock/evidência/delta e checkpoint.

## Fora de escopo

- Criar camada, viewport, shader, cena, renderer ou qualquer rendering.
- Alterar o planner, o contrato `composition.v1`, cenas, presets, renderer ou shaders.
- Claims de FPS, frame-time, qualidade visual, game feel ou ganho.
- Novos parents ou mudança de status.

## DoD

- `corridor_static` `SAFE_CONFIG_HEURISTIC` sem conflitos.
- `arena_combat` e `dense_city` `CONFLICTS_REPORTED` com exatamente um `base_z_fight_risk` medium cada.
- Quatro camadas (`background`, `gameplay`, `foreground`, `hud`) e entidades críticas `player`/`threat` em todas as cenas.
- 0 conflitos high, 0 alpha-over-critical e 0 overlay/gameplay.
- Builder `--check` reproduz JSON/Markdown; CI 31/34; suíte completa verde.
- PR protegida e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, planner/contrato alterado, hash M02 divergente, conflito high inesperado, builder divergente ou check vermelho → parar e registrar.

# Checkpoint Delta · NEX-M08-SCENE-COMPOSITION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `d218525cbd7cd84b5c69f5e52577a6244f8733b6`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M08 composição sobre M02:** três planos 2.5D de quatro camadas com entidades críticas player/threat.
2. **Resultado:** `corridor_static` `SAFE_CONFIG_HEURISTIC`; `arena_combat` e `dense_city` `CONFLICTS_REPORTED` com um `base_z_fight_risk` medium cada.
3. **Builder:** `build_scene_composition.py --check` reproduz JSON/Markdown; enforcement no Fast Lane (31 arquivos / 34 checks).
4. **Sem mudança de planner, contrato, cena, preset, renderer, shader, ruleset ou permissão de CI.**
5. **Sem camada/viewport/shader/rendering ou claim de FPS/qualidade/game feel.**

## O que NÃO muda

- Todos os parents M01–M12 seguem bounded admitted; nenhum parent muda de status.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime, hub, engine, `project.godot` principal ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M08-SCENE-COMPOSITION-WO-001-EVIDENCE.md`
- `nex_modules/render2_5d/composition/evidence/scene-composition-2026-11-15.json`
- `docs/benchmarks/m08/scene-composition.v1.json`
- `docs/benchmarks/m08/SCENE-COMPOSITION.md`
- `tests/ci/test_scene_composition.py` (7 testes)

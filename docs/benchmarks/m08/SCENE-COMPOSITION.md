# NEX M08 · Scene composition from M02 analysis

**Status:** `COMPOSITION_PLANNING_DERIVED / NON_RENDERING / NO_VISUAL_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_modules/render2_5d/composition/evidence/scene-composition-2026-11-15.json` · **Source SHA:** `d218525cbd7cd84b5c69f5e52577a6244f8733b6`
**Manifesto M02:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-analysis/runs.v1.json` · **SHA-256:** `1aab9825beeab8b69ac45ea46c251e33609713c5006e3e4c465715d0931df068`
**Evidence SHA-256:** `6dbaad91d5b2121d4540f0fba553015781a0430d4526ec039027a2d223d5237b`

| Cena | Opaque | Alpha | Overlay | Z-fight | Veredito |
|---|---:|---:|---:|---:|---|
| corridor_static | 16 | 0 | 0 | 0 | SAFE_CONFIG_HEURISTIC |
| arena_combat | 16 | 0 | 0 | 4 | CONFLICTS_REPORTED |
| dense_city | 16 | 0 | 0 | 4 | CONFLICTS_REPORTED |

## Observações

- corridor_static is SAFE_CONFIG_HEURISTIC with no conflicts
- arena_combat and dense_city each report one medium base_z_fight_risk from the M02 depth plan
- all scenes keep zero high, alpha-over-critical and overlay/gameplay conflicts
- each plan has four layers and the player/threat critical entities

## Limitações

- planning only; no layer, viewport, shader, scene or renderer is created
- the base 3D plan is the M02 scene-analysis bundle, not a rendered depth buffer
- layer roles and parallax values are reference defaults, not art direction
- no FPS, frame-time, visual-quality or game-feel claim

Gerado por `docs/benchmarks/m08/tools/build_scene_composition.py`; não é benchmark visual.

# NEX M10 · Archetype combat feedback

**Status:** `FEEDBACK_PLANNING_DERIVED / NON_RENDERING / NO_GAME_FEEL_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_modules/animation/combat_feedback/evidence/archetype-feedback-2026-11-15.json` · **Source SHA:** `91e6c15794662b3502244c2d03879b8dbb9980dd`
**Dataset:** `nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json` · **SHA-256:** `fd51d65b744c8d540283360b7de0ebe9cab861916063065e9c7749dbe3bcb57e`
**Evidence SHA-256:** `b4a181b0d8a22d0bf36dfea1c11ca3daf7afdc7d585f65504e220a1252e1e262`

| Arquétipo | Spells | Canais | Pico | Hit-stop | Shake máx. | Veredito |
|---|---:|---:|---:|---:|---:|---|
| skirmish | 2 | 10 | 5 | 40 ms | 0.232 | SAFE_CONFIG_HEURISTIC |
| elite | 3 | 15 | 5 | 60 ms | 0.264 | SAFE_CONFIG_HEURISTIC |
| boss | 5 | 25 | 5 | 100 ms | 0.313 | SAFE_CONFIG_HEURISTIC |

## Observações

- all 10 spell plans return SAFE_CONFIG_HEURISTIC with zero conflicts
- each spell uses five channels and peaks at the 5-channel concurrency budget
- archetype totals are 10, 15 and 25 channels for skirmish, elite and boss
- the largest shake intensity is 0.313 for meteor-storm, below the 0.8 budget

## Limitações

- planning only; no animation, camera, shader, scene or renderer is created
- damage is derived from impact particle amounts as reference data, not gameplay balance
- each spell is planned independently; archetype totals are aggregates, not a simultaneous rotation
- no FPS, frame-time, game-feel or visual-quality claim

Gerado por `docs/benchmarks/m10/tools/build_archetype_feedback.py`; não é benchmark de game feel.

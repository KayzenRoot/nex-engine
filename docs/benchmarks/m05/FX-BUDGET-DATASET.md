# NEX M05 · FX budget dataset

**Status:** `BUDGET_PLANNING_DERIVED / NON_RENDERING / NO_PERFORMANCE_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json` · **Source SHA:** `99437b22e94a6494eaef801872bb8fd0c79c0f1a`
**Evidence SHA-256:** `fd51d65b744c8d540283360b7de0ebe9cab861916063065e9c7749dbe3bcb57e`

| Arquétipo | Spells | Emitters | Particles | GPU emitters | Decals | Veredito |
|---|---:|---:|---:|---:|---:|---|
| skirmish | 2 | 7 | 484 | 3 | 2 | FIT |
| elite | 3 | 11 | 1047 | 5 | 3 | TIGHT |
| boss | 5 | 18 | 2753 | 8 | 5 | OVER_BUDGET |

## Observações

- skirmish fits its budget with 484 particles and 7 emitters
- elite is TIGHT on particles at 1047/1100 (95.2%)
- boss exceeds the 2000-particle budget at 2753 (137.7%) and receives a 3-step reduction plan
- no particle, emitter, light, decal or renderer is created

## Limitações

- planning only; no particle, emitter, light, decal or renderer is created
- budgets are reference values, not measured hardware limits
- no FPS, frame-time, overdraw or visual-quality claim

Gerado por `docs/benchmarks/m05/tools/build_fx_budget_dataset.py`; não é benchmark de hardware.

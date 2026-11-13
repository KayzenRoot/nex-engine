# NEX M03-LIGHTBUDGET · Lighting-budget arbiter (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_RENDERING / NO_NEW_MEASUREMENT / NO_GENERALIZATION_CLAIM`
**Work Order:** NEX-M03-LIGHTBUDGET-WO-001 (Issue #8) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`LightBudgetArbiter` projects GPU cost for a lighting configuration using coefficients calibrated from the verified S05 Lighting Matrix captures (RTX 5050, single session, GPU p95 at 25 proxies), then recommends an ordered degradation ladder when a budget is exceeded.

- `estimate(scene)` returns the breakdown, projected GPU ms, headroom and verdict (`FIT`, `TIGHT`, `OVER_BUDGET`, `INVALID_INPUT`).
- `arbitrate(scene)` adds degradation steps and the first step that fits the budget.

## Cost model (`nex_light_cost_model.v1`)

| Coefficient | Value (ms) | S05 anchor |
|---|---:|---|
| `base_gpu_ms` | 0.181 | baseline-25 |
| `per_omni_light_ms` | 0.0245 | lights-25 minus baseline |
| `directional_shadow_ms` | 0.100 | shadows-25 fit |
| `per_omni_shadow_ms` | 0.02025 | shadows-25 fit |
| `per_particle_emitter_ms` | 0.01375 | vfx-25 minus baseline |
| `shadow_vfx_interaction_ms` | 0.679 | combined-25 residual |

The interaction term applies only when `directional_shadow` and `particle_emitters > 0`. Coefficients are overridable through `configure({model: {...}})` and can be reset with `reset_model()`.

## Degradation ladder

Ordered by quality cost, then scope:

1. `halve_particle_emitters` (low)
2. `disable_directional_shadow` (high)
3. `disable_omni_shadows` (medium)
4. `halve_omni_lights` (high, clamps shadowed lights)
5. `disable_omni_lights` (high)

Steps that do not change the scene are skipped. `recommended_step` is the first step whose projection is `FIT`.

## API

| Method | Purpose |
|---|---|
| `configure({budget_ms, model})` | Budget (0.5–1000 ms) and coefficient overrides. |
| `estimate(scene)` | Deterministic projection and verdict. |
| `arbitrate(scene)` | Projection plus degradation ladder. |
| `get_last_report()` | Last report. |
| `reset_model()` / `clear()` | Restore default coefficients / full reset. |

Scene input: `{omni_lights, shadowed_omni_lights, directional_shadow, particle_emitters}`.

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/lighting/budget `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M03_LIGHTBUDGET_SMOKE_PASS: 57 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No rendering**: the arbiter never creates lights, shadows or particles.
- Coefficients come from **one synthetic S05 session** on an RTX 5050 at 25 proxies; they are not frame time, FPS, or a benchmark.
- The interaction term comes from a **single combined capture**; it is a planning heuristic.
- Projections do **not** generalize to other scenes, drivers, hardware or resolutions.
- Degradation steps are planning options, not quality-validated settings.
- No new GPU capture or engine integration is performed; M03 parent remains `NOT_ADMITTED`.

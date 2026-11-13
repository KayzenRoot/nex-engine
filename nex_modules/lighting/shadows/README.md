# NEX M03-SHADOWSTAB · Shadow-stability analyzer (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_RENDERING / NO_SHADOW_IMPLEMENTATION / NO_VISUAL_CLAIM`
**Work Order:** NEX-M03-SHADOWSTAB-WO-001 (Issue #8) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`ShadowStabilityAnalyzer` reads a `lighting.plan.v1` plan (from the light-rig planner) or a `lighting.v1` observation and returns a deterministic risk report:

- Validates schema, shadow budget, light identity/type and numeric fields.
- Counts shadowed and directional-shadowed lights and estimates shadow tiles from cascades plus one map per omni/spot caster.
- Computes an atlas tile budget (`atlas_size / 256`) and pressure ratio.
- Computes practical cascade splits for the configured camera near/far and split lambda.
- Flags heuristic risks: zero/over-budget shadow casters, demoted casters, cascade overflow/missing cascades, low bias (acne), high bias (peter-panning), soft shadows on small atlases, narrow spotlights and atlas pressure.
- Emits a verdict: `STABLE_CONFIG_HEURISTIC`, `STABLE_CONFIG_HEURISTIC_WITH_NOTES`, `RISK_REPRODUCED` or `INCONCLUSIVE`.

## Contract vocabulary (lighting.v1 / lighting.plan.v1)

| Input | Analyzer use |
|---|---|
| `lights[].light_type` | `directional`, `omni`, `spot`; unknown types are inconclusive |
| `lights[].shadow_enabled` | caster counting and budget checks |
| `lights[].shadow_bias` / `shadow_softness` | heuristic acne/peter-panning and atlas-band risks |
| `lights[].cascades` | directional tile estimate and cascade budget check |
| `lights[].spot_angle_degrees` | narrow-projection risk |
| `shadow_budget` | `max_shadowed_lights`, `directional_cascades`, `atlas_size` |
| `shadow_assigned` (plan only) | demoted-caster detection |

The analyzer does not modify the contract.

## API

| Method | Purpose |
|---|---|
| `configure({camera_near_m, camera_far_m, split_lambda})` | Camera and cascade-split inputs. |
| `analyze_plan(plan)` | Analyze a `lighting.plan.v1` plan. |
| `analyze_observation(observation)` | Analyze a `lighting.v1` observation. |
| `get_last_report()` | Last deterministic report. |
| `clear()` | Reset camera inputs and last report. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/lighting/shadows `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M03_SHADOWSTAB_SMOKE_PASS: 51 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No rendering**: no shadow map, filter, light or renderer is created; findings are heuristic, not visual proof.
- Acne, peter-panning, shimmer and cascade seams are **not measured**; thresholds are planning heuristics.
- Cascade splits use a practical split scheme, not the engine's cascade fitter.
- Atlas pressure is arithmetic (`shadow_tiles / (atlas_size / 256)`), not allocator behavior.
- Performance/quality/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.
- Real shadow integration requires a future M03 scene WO; M03 parent remains `NOT_ADMITTED`.

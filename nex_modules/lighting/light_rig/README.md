# NEX M03-LIGHTRIG · Light-rig planner (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_RENDERING / NO_SHADOW_IMPLEMENTATION / NO_PERFORMANCE_CLAIM`
**Work Order:** NEX-M03-LIGHTRIG-WO-001 (Issue #8) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`LightRigPlanner` is a deterministic planning layer aligned with `contracts/m03/lighting.v1`:

- Configures budgets: max lights, max shadowed lights, directional cascades and shadow atlas size.
- Configures the environment: ambient source/color/energy, tonemap, glow, fog and GI.
- Registers `directional`, `omni` and `spot` lights with color, energy, shadow bias/softness, cull mask and type-specific range/angle/cascades.
- Rejects invalid input: duplicate/empty ids, out-of-range color/energy/bias/softness/cull mask, type-field contradictions, dark shadow casters and budget caps.
- Sorts lights by id and assigns shadow slots by energy descending (ties by id) within `max_shadowed_lights`.
- Emits warnings: `no_lights`, `light_budget_exceeded`, `shadow_budget_exceeded`, `directional_cascade_exceeded`.
- Estimates `estimated_shadow_maps` from directional cascades plus one map per shadowed omni/spot light.
- Exports a `lighting.v1` observation with performance explicitly `UNAVAILABLE` and validated provenance.

## Contract vocabulary (lighting.v1)

| Contract field | Planner value |
|---|---|
| `light_type` | `directional`, `omni`, `spot` (enum order preserved) |
| `ambient_source` | `color`, `sky`, `disabled` |
| `tonemap` | `linear`, `reinhard`, `filmic`, `aces` |
| `gi.mode` | `disabled`, `sdfgi`, `voxelgi`, `lightmapgi` |
| limits | energy ≤ 16, cull mask ≤ 1048575, range ≤ 200 m, spot angle ≤ 90°, cascades ≤ 4, atlas 256–8192 |
| `shadow_budget` | mirrors `max_shadowed_lights`, `directional_cascades`, `atlas_size` |

The planner does not redefine or modify the contract.

## API

| Method | Purpose |
|---|---|
| `configure({max_lights, max_shadowed_lights, max_cascades, atlas_size})` | Budgets and limits. |
| `configure_environment({ambient_source, ambient_color, ambient_energy, tonemap, glow, fog_density, fog_light_energy, gi_mode, gi_energy})` | Partial environment update. |
| `register_light(id, type, color, energy, shadow_enabled, bias, softness, cull_mask, range_m, spot_angle_degrees, cascades)` | Register a light. |
| `plan()` / `get_last_plan()` | Deterministic plan with sorted lights, shadow slots, totals, warnings and limitations. |
| `export_observation(observation_id, captured_at_utc, provenance)` | Build a `lighting.v1` observation; performance is `UNAVAILABLE`. |
| `clear()` | Reset lights, last plan and environment to defaults. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/lighting/light_rig `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M03_LIGHTRIG_SMOKE_PASS: 70 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No rendering**: no light, shadow map, GI probe, shader, material or scene is created. `estimated_shadow_maps` is arithmetic, not a GPU measurement.
- Performance/quality/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.
- Shadow assignment is a deterministic planner policy, not a renderer; no atlas packing, cascade fitting or contact shadows.
- Real lighting integration requires a future M03 scene WO; M03 parent remains `NOT_ADMITTED`.
- The planner mirrors the contract vocabulary; it does not promote new contract terms.

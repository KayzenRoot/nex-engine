# NEX M07-S01 · Canvas/batching planner (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_RENDERING / NO_SHADER_CHANGE / NO_PERFORMANCE_CLAIM`
**Work Order:** NEX-M07-S01-WO-001 (Issue #12) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`CanvasPlanner` is a deterministic planning layer aligned with `contracts/m07/render2d.v1`:

- Registers **layers** (z-index, blend mode, material, transform, visibility), **materials** (shader + lighting mode), **2D lights** and **particles**.
- Sorts visible layers by `z_index`, ties by id.
- **Batches** consecutive layers that share material and blend mode; each batch is one estimated draw call.
- Estimates `batch_groups`, `draw_calls` and `state_changes`.
- Emitting particles add a draw call; non-emitting emitters do not.
- Reports warnings: `draw_call_budget_exceeded`, `light_budget_exceeded`, `lighting_without_lights`.
- Rejects invalid input: duplicate ids, unknown material, invalid blend/z/scale, non-finite transforms, invalid light/particle values, layer cap.

## Contract vocabulary (render2d.v1)

| Contract field | Planner value |
|---|---|
| `blend_mode` | `mix`, `add`, `sub`, `mul`, `premul_alpha` (enum order preserved) |
| `lighting_mode` | `unshaded`, `canvas_light` |
| `batching` | `max_draw_calls` budget; plan yields `batch_groups`, `draw_calls`, `state_changes` |
| layers/materials/lights/particles | same identities and invariants (unique ids, material references, emitting amount ≥ 1) |

The planner does not redefine or modify the contract.

## API

| Method | Purpose |
|---|---|
| `configure({max_layers, max_draw_calls, max_lights})` | Budgets and limits. |
| `register_material(id, shader_id, lighting_mode)` | Register a material identity. |
| `register_layer(id, z_index, blend_mode, material_id, position, scale, rotation_deg, visible)` | Register a layer. |
| `register_light(id, type, energy)` | Register a 2D light. |
| `register_particle(emitter_id, amount, emitting)` | Register a particle emitter. |
| `plan()` / `get_plan()` | Deterministic plan with batches, totals and warnings. |
| `clear()` | Reset all registries and the last plan. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render2d/canvas `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M07_S01_SMOKE_PASS: 46 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No rendering**: no CanvasItem, shader, material, light or particle is created. Draw calls are a deterministic estimate, not a GPU measurement.
- Performance/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.
- Batching is a simple consecutive-material/blend grouping, not a full renderer; no texture atlas, state cache, y-sort or transparency rasterization.
- Real 2D integration requires a future scene WO; M04/M05 materials/VFX and M08 2.5D are untouched.
- The planner mirrors the contract vocabulary; it does not promote new contract terms.

# NEX M08-COMPOSITION · 2.5D composition planner (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_RENDERING / NO_VIEWPORT / NO_VISUAL_CLAIM`
**Work Order:** NEX-M08-COMPOSITION-WO-001 (Issue #13) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`CompositionPlanner` consumes the `composition.v1` vocabulary and returns a deterministic 2.5D composition plan:

- Registers ordered layers (`background`, `gameplay`, `foreground`, `hud`) with parallax, blend mode, alpha, critical flags and optional depth override.
- Registers critical entities (`player`, `threat`, `objective`) with `must_remain_visible`.
- Applies depth policy (`inherit_3d`, `override_per_layer`, `hybrid`), alpha guard and HUD/overlay safety.
- Groups draw order by role (background → gameplay → foreground → HUD) and reports reordering.
- Reports conflicts: HUD depth override, HUD covering gameplay, alpha over visible critical entities, missing critical guard, depth override under `inherit_3d`, missing override under `override_per_layer`, parallax outside the role band, and base-plan z-fight/alpha/overlay risks.
- Emits `SAFE_CONFIG_HEURISTIC`, `CONFLICTS_REPORTED` or `INVALID_INPUT`.
- Exports a `composition.v1` observation with performance `UNAVAILABLE` and validated provenance.

## Contract vocabulary (composition.v1)

| Contract field | Planner value |
|---|---|
| `layer_stack[].role` | `background`, `gameplay`, `foreground`, `hud` |
| `layer_stack[].blend_mode` | `normal`, `add`, `multiply`, `screen` |
| `depth_policy` | `inherit_3d`, `override_per_layer`, `hybrid` |
| `overlay_safety.conflict_policy` | `report`, `block` |
| `critical_entities[].role` | `player`, `threat`, `objective` |
| `alpha_policy` | `critical_guard`, `max_alpha_over_gameplay` |
| `base_3d_plan` | schema/digest/counts/risks mirrored |

The planner mirrors the contract; it does not modify it.

## API

| Method | Purpose |
|---|---|
| `configure({max_layers, max_alpha_over_gameplay})` | Limits and alpha guard threshold. |
| `set_base_plan({plan_schema, plan_sha256, counts...})` | Reference to the M02 depth plan. |
| `set_policies({depth_policy, critical_guard, hud_layer_id, overlay_may_cover_gameplay, conflict_policy})` | Composition policies. |
| `register_layer(id, role, parallax, blend_mode, alpha, gameplay_critical, may_cover_gameplay, has_depth_override, depth_override_m)` | Register a 2.5D layer. |
| `register_critical_entity(id, role, must_remain_visible)` | Register a critical entity. |
| `plan()` / `get_last_plan()` | Deterministic plan with draw order, conflicts and summary. |
| `export_observation(observation_id, captured_at_utc, provenance)` | Build a `composition.v1` observation. |
| `clear()` | Reset all state. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render2_5d/composition `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M08_COMPOSITION_SMOKE_PASS: 69 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No rendering**: no layer, viewport, shader, scene or renderer is created; no pixels are composed.
- Alpha-over-critical is depth/alpha arithmetic, not pixel coverage or visual occlusion.
- Parallax bands are planning heuristics, not measured camera behavior.
- Draw order is grouped by role; the planner never reorders 3D primitives.
- Visual composition, edge cases and runtime cost: `INCONCLUSIVE_NOT_RUN`.
- Real 2.5D integration requires a future M08 scene WO; M08 parent remains `NOT_ADMITTED`.

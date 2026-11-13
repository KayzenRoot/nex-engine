# NEX M02-S03 · DepthWeave prototype (depth and composition planning)

**Status:** `PROTOTYPE / NO_RENDERING / NO_SHADER_CHANGE / NO_2.5D_IMPLEMENTATION / NO_PERFORMANCE_CLAIM`
**Work Order:** NEX-M02-S03-WO-001 (Issue #30) · **Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable (pinned by M00). Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`DepthCompositionSolver` is a deterministic planner for depth conflicts and composition passes:

- **Passes:** opaque/decal front-to-back; alpha back-to-front; overlays last. Ties are broken by id.
- **Z-fighting risk:** opaque primitives with overlapping depth intervals and centers within `depth_epsilon_m` are reported as `z_fight_risks`, with deterministic ordering.
- **Hysteresis:** adjacent primitives within `hysteresis_m` keep their previous relative order, preventing flicker from small camera motion; a large motion beyond the threshold changes the order.
- **Gameplay safety:** `alpha_over_critical` (alpha in front of a `gameplay_critical` primitive) and `overlay_gameplay_conflicts` (overlay marked `overlay_blocks_gameplay` with critical gameplay present) are reported, never hidden.
- **Projections:** perspective and orthographic are recorded; this prototype uses view-axis depth ordering for both (documented invariant).
- **M08 draft:** `M08-COMPOSITION-CONTRACT-DRAFT.md` sketches a future 2.5D composition contract. It is a draft, not an admitted contract or implementation.

## API

| Method | Purpose |
|---|---|
| `configure(dict) -> bool` | Projection, depth epsilon, hysteresis, primitive limit. |
| `set_camera(position, direction) -> bool` | Camera mock (normally from M02-S01). |
| `register_primitive(id, kind, position, radius, gameplay_critical, overlay_blocks_gameplay) -> bool` | Register a mock sphere primitive. |
| `clear_primitives()` | Reset scene and ordering history. |
| `plan() -> dict` | Compute passes, depths, risks, conflicts, stability and limitations. |
| `get_plan() -> dict` | Last plan copy. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render3d/depth_composition `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M02_S03_SMOKE_PASS: 37 checks`; log committed under `evidence/`.

## Limits (explicit)

- No rendering, rasterization, screenshots or visual human gate in this WO. Visual correctness of edges, aliasing, transparency and narrow passages is **`INCONCLUSIVE_NOT_RUN`**.
- Primitives are mock spheres with view-axis depth; real mesh bounds, per-pixel depth and transparent surfaces require a future scene-integration WO.
- `alpha_over_critical` is conservative (depth comparison, not pixel coverage); it is a warning, not a proof.
- Orthographic and perspective share ordering in this prototype; any projection-specific depth-buffer behavior must be validated with real rendering.
- No shader, material, M04 PBR, 2.5D, engine or CI changes.
- No fps/VRAM/frame-time claim. Any future measurement must use the M01 baseline and the same hardware/procedure.

## Fallbacks

- Native Godot depth buffer and `render_priority`/material sorting for real scenes; do not introduce a custom compositor until a measured conflict justifies it.
- Overlay safety via viewport layering and HUD separation rather than global z-depth hacks.
- If `alpha_over_critical` appears in a real scene, prefer moving the rim/indicator out of the critical silhouette rather than disabling transparency globally.

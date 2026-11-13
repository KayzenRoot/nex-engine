# NEX M02-S01 · Isometric camera rig (prototype)

**Status:** `PROTOTYPE / NOT_ENGINE_INTEGRATION / NOT_ADMITTED_AS_MODULE`
**Work Order:** NEX-M02-S01-WO-001 (Issue #28) · **Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable (pinned by M00). This module is a self-contained Godot project for deterministic headless tests; it is **not** wired into `nex_bench` or the future engine scene tree.

## What it does

`IsometricCameraRig` (Node3D) owns a `Camera3D` and provides a deterministic isometric camera with:

- **Two projections:** inclined perspective (`isometric_perspective`) and orthographic (`isometric_orthographic`), as a comparison.
- **Framing:** yaw/pitch, distance, orthographic size, vertical FOV, clip planes, viewport size.
- **Follow:** dead zone, exponential smoothing, world-XZ bounds, zoom clamped to `[zoom_min, zoom_max]`.
- **Synchronization:** `world_to_screen` / `screen_to_world` (ray-plane at a chosen Y) for selection/raycast consistency; `visible_margin` analytically checks actors against the safe frame for 16:9, 4:3 and 21:9.
- **Determinism:** `replay(events, fixed_delta, initial_focus, initial_zoom)` returns identical state arrays for identical inputs.
- **Optional stability aid:** `pixel_snap` quantizes camera position to 0.01 m. **Limitation:** this is not a projection-space subpixel snap; it does not eliminate shimmering on its own.

## Run the headless tests

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render3d/camera `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected marker: `NEX_M02_S01_SMOKE_PASS: 32 checks` (exit 0). The committed log is `evidence/headless-smoke-2026-11-13.log`.

## API

| Method | Purpose |
|---|---|
| `configure(dict) -> bool` | Validate and apply parameters; rejects invalid projection, clips, zoom, dead zone, bounds. |
| `set_focus(Vector3)` | Snap focus (clamped to bounds) and rebuild the camera transform. |
| `update_follow(Vector3, delta)` | Dead-zone + smoothed follow for one step. |
| `set_zoom(float)` / `zoom_by(float)` | Clamp and apply zoom. |
| `world_to_screen(Vector3) -> Vector2` | Camera projection for selection/UI anchoring. |
| `screen_to_world(Vector2, plane_y) -> Vector3` | Ray-plane unprojection; sets `last_error` if parallel. |
| `visible_world_extents(aspect)` | Analytic half-width/half-height at the focus plane. |
| `visible_margin(actors, margin)` | Whether actors are inside the safe frame. |
| `get_state() -> dict` | State compatible with `render_core.v1` camera fields. |
| `replay(events, ...)` | Deterministic state sequence for fixtures. |

## Contract mapping (`contracts/m02/render_core.v1`)

- `projection` ∈ `isometric_perspective` / `isometric_orthographic`.
- `position_m`, `target_m`, `view_rotation_degrees`, `near_clip_m`, `far_clip_m`, `viewport {width_px,height_px,unit:"px"}`, `stability {snap_to_pixel, anchor_offset_px}`.
- Perspective adds `vertical_fov_degrees`; orthographic adds `ortho_size_m`. The contract's availability rules are untouched because this rig does not produce performance metrics.

## M01 camera mapping and fallbacks

- M01/S04/S05 used a fixed camera at `(14, 14, 14)` looking at the origin, FOV 40°, 1280×720, VSync 1. This rig's defaults (`yaw 45°`, `pitch -35.264°`, `distance 18`, `FOV 40°`) approximate that view; the M01 scenes remain **read-only** and untouched.
- **Fallback A:** if the perspective prototype is rejected, use the orthographic projection with the same framing API.
- **Fallback B:** if the rig module is unavailable, keep a plain `Camera3D` with the same transform semantics (position/rotation/FOV/size); no engine dependency is introduced by this prototype.
- **Fallback C:** selection/raycast can use Godot's native `Camera3D` project/unproject directly; the rig only adds consistent framing math on top.

## Limits (explicit)

- **Performance/FPS A/B: `INCONCLUSIVE_NOT_RUN`.** This increment does not change rendering and did not capture GPU/FPS. Any number would be fabricated.
- No input mapping, collision/occlusion, shake, cinematic transitions or gameplay integration.
- Headless smoke is a deterministic logic test, **not** a visual or GPU benchmark.
- `visible_margin` uses the focus plane; actors at different depths may project differently under perspective (§ approximation to be validated by S02/S03 when admitted).
- The module is a self-contained Godot project; moving it into the engine module tree requires a future WO and Steward file lock.

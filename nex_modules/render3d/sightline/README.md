# NEX M02-S02 · Sightline prototype (occlusion and character readability)

**Status:** `PROTOTYPE / NO_ENGINE_INTEGRATION / NO_SHADER_CHANGE / NO_PERFORMANCE_CLAIM`
**Work Order:** NEX-M02-S02-WO-001 (Issue #29) · **Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable (pinned by M00). Self-contained Godot project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## Policy

| Actor priority | Blocked by occluder | Behavior |
|---|---|---|
| Player | Yes | Reveal after `enter_delay_s`: hard occluders keep opacity + silhouette; soft occluders fade to `target_alpha`. |
| Threat within `critical_threat_distance_m` | Yes | Same reveal as player (identifiable); `danger_alert` set immediately. |
| Threat beyond critical distance | Yes | No opacity change; `danger_alert` set so it is **not silently invisible**; no silhouette. |
| Decoration | Yes | No reveal; world occlusion preserved. |
| Any actor | Transparent occluder | Never blocks gameplay visibility; no reveal needed. |

Gameplay visibility (`gameplay_visible`) is computed from the camera→actor segment and is **never modified** by the visual policy. `visual_readable` is separate: it reports whether the actor is currently identifiable through a fade/silhouette.

## Mechanism

- Occluders are `AABB` volumes (mock geometry). Segment–AABB intersection uses the slab method.
- Hysteresis: reveal only after `enter_delay_s` of continuous blocking; clear only after `exit_delay_s` of continuous free sightline. Short jitter cannot flicker a revealed occluder.
- Fade: `reveal_progress` advances at `fade_speed`; soft occluders interpolate alpha from 1.0 to `target_alpha`; hard occluders keep alpha 1.0 and raise a silhouette flag.
- Cap: at most `max_reveal_occluders` active, ordered by camera-to-AABB-center distance; the rest are marked `capped`.
- No global z-depth hack, no shader edit, no material contract change.

## API

| Method | Purpose |
|---|---|
| `configure(dict) -> bool` | Validate delays, fade, alphas, cap and critical distance. |
| `set_camera_position(Vector3)` | Camera pose input (normally from M02-S01). |
| `register_occluder(id, AABB, kind, transparent) -> bool` | Register/mock an occluder. |
| `move_occluder(id, AABB) -> bool` | Move/replace a mock occluder (moving wall test). |
| `set_actors(Array) -> bool` | At most one player; threats and decoration. |
| `update(delta)` | Recompute blocking, hysteresis, fade/silhouette, cap, alerts. |
| `get_state() -> dict` | Actors, occluders, summary (`active_reveals`, `danger_alerts`, `critical_unseen`). |
| `segment_intersects_aabb(start, end, box) -> bool` | Deterministic slab test (exposed for tests). |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render3d/sightline `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M02_S02_SMOKE_PASS: 49 checks` (exit 0); log committed under `evidence/`.

## Scene applicability and limits

- `corridor_static`, `arena_combat` and `dense_city` would supply real occluder AABBs; this prototype does **not** run those scenes. Visual/GPU results are `INCONCLUSIVE_NOT_RUN`; no fps, VRAM or frame-time claim is made.
- AABB-only prototype: real meshes, transparent materials, vegetation, VFX and moving doors require a future scene-integration WO.
- Occluder cap ordering uses camera-to-center distance; a tall near-camera wall may outrank a low wall closer to the player. Documented behavior; tests assert the invariant, not a specific id.
- Threat beyond critical distance is alerted but not visually revealed; gameplay visibility remains authoritative. No gameplay state is changed.
- Fallback routes: Godot native layers/raycasts, plain `modulate` transparency, or a standard outline shader. None is implemented here.
- No HIGH/CRITICAL behavior is hidden: blocked threats raise `danger_alert`; `critical_unseen` is surfaced in `summary`.

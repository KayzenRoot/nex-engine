# NEX M09-RESOLVER · Preset resolver (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_RUNTIME_APPLICATION / NO_PERFORMANCE_CLAIM`
**Work Order:** NEX-M09-RESOLVER-WO-001 (Issue #14) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`PresetResolver` loads a `preset_pack.v1`, validates its tier ladder and settings, checks hardware/Godot/contract compatibility, and resolves a tier or named preset with deterministic deep-merged overrides.

- Validates preset ids, standard-tier uniqueness, settings blocks, ranges/enums and reduced-motion limits.
- Enforces tier monotonicity for `resolution_scale`, `shadow_quality`, `shadow_atlas_size` and `target_fps`.
- Checks pack hardware tier against the environment, required contract versions against the pack and environment, and the Godot version range.
- Applies overrides block-by-block, records `block.key` paths, and revalidates the merged settings.
- Emits `RESOLVED`, `INVALID` or `INCOMPATIBLE`.

## Contract vocabulary (preset_pack.v1)

| Contract field | Resolver use |
|---|---|
| `presets[].tier` | `low`, `medium`, `high`, `ultra`, `custom` |
| `settings.rendering` | renderer/driver/resolution/MSAA/shadow quality |
| `settings.lighting` | tonemap/glow/atlas/shadowed lights |
| `settings.performance` | target fps/draw calls/LOD bias |
| `settings.composition` | depth policy/parallax scale |
| `settings.feedback` | hit-stop/shake/reduced motion |
| `settings.accessibility` | contrast/focus ring |
| `compatibility` | contract versions/Godot range/hardware tier |

## API

| Method | Purpose |
|---|---|
| `configure({hardware_tier, godot_version, available_contracts, required_contracts})` | Environment. |
| `load_pack(pack)` | Validate and store a preset pack. |
| `resolve_tier(tier, overrides)` | Resolve a standard tier. |
| `resolve_preset(preset_id, overrides)` | Resolve by id. |
| `list_presets()` | Presets ordered by tier. |
| `get_last_resolution()` / `clear()` | Last result / reset. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/tools/preset_resolver `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M09_RESOLVER_SMOKE_PASS: 50 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No runtime application**: no `ProjectSettings`, engine setting, scene or renderer is modified.
- Compatibility uses declared versions, not probed hardware.
- Settings merge deterministically; visual quality and performance are not validated.
- Tier monotonicity is structural, not measured.
- No FPS, frame-time or quality claim.
- Real preset application requires a future M09 WO; M09 parent remains `NOT_ADMITTED`.

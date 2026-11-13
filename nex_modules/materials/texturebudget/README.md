# NEX M04-TEXTUREBUDGET · Texture-budget planner (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_DECODING / NO_ATLAS_PACKING / NO_VRAM_CLAIM`
**Work Order:** NEX-M04-TEXTUREBUDGET-WO-001 (Issue #9) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`TextureBudgetPlanner` reads material texture descriptors in the `material.v1` vocabulary and returns a deterministic budget report:

- Validates material ids against the contract pattern and texture descriptors (slot, SHA-256, dimensions, mips, sRGB).
- Deduplicates textures by SHA-256 and reports duplicate references and saved bytes.
- Estimates decoded bytes: `width * height * 4`, multiplied by `4/3` when mipmaps are enabled.
- Estimates atlas tiles at 256 px and compares them with the atlas grid.
- Flags: over byte/count budget, duplicates, atlas pressure, oversized textures, non-power-of-two dimensions, sRGB on normal/ORM data, missing mips, digest/dimension mismatches and detail-slot pressure.
- Produces a greedy downscale plan (halve the largest textures down to 64 px) and the projected bytes after the plan.
- Emits `FIT`, `TIGHT`, `OVER_BUDGET` or `INVALID_INPUT`.

## Contract vocabulary (material.v1)

| Contract field | Planner use |
|---|---|
| `material_id` | Lowercase contract pattern validation |
| `textures[].slot` | `albedo`, `normal`, `orm`, `emission`, `detail` |
| `textures[].sha256` | Deduplication identity; lowercase 64-hex |
| `textures[].width_px` / `height_px` | Decoded size and atlas tiles |
| `textures[].mipmaps` | 4/3 size factor and missing-mips finding |
| `textures[].srgb` | Normal/ORM data-color finding |
| `texture_budget` | `max_texture_count`, `max_texture_bytes`, `atlas_size`; `orm_packed` is not used |

The planner mirrors the contract vocabulary; it does not modify the contract.

## API

| Method | Purpose |
|---|---|
| `configure({max_decoded_bytes, max_texture_count, atlas_size})` | Budgets and atlas size. |
| `analyze(materials)` | Deterministic report with findings and downscale plan. |
| `get_last_report()` | Last report. |
| `clear()` | Restore defaults. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/materials/texturebudget `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M04_TEXTUREBUDGET_SMOKE_PASS: 55 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No decoding**: no `Image`, `Texture2D`, `ResourceLoader` or GPU upload is used; bytes are arithmetic estimates.
- Decoded size is not VRAM usage; driver compression, alignment and residency are not modeled.
- Atlas pressure is tile arithmetic, not an allocator or packer simulation.
- Downscale steps are planning suggestions; no resampling is performed and visual quality is not validated.
- Performance/quality: `INCONCLUSIVE_NOT_RUN`.
- Real texture integration requires a future M04 WO; M04 parent remains `NOT_ADMITTED`.

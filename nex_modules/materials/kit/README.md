# NEX M04 · Procedural material kit

**Status:** `REFERENCE_KIT / NON_RENDERING / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Admission:** `NEX-ADR-0011` bounded non-rendering material-kit scope.

## Contents

- `textures/`: 12 deterministic PNGs (albedo, normal, ORM) at 128×128 for four reference materials.
- `materials/`: four `StandardMaterial3D` `.tres` resources referencing the textures.
- `kit.v1.json`: one `material.v1` observation with SHA-256 per texture and declared budget.
- `validate_kit.gd`: headless `ResourceLoader` validation; loads the four materials and checks the texture slots.
- `evidence/headless-load-2026-11-15.log`: captured validation output.

## Verify

```powershell
python docs/benchmarks/m04/tools/build_material_kit.py --check
godot --headless --path nex_modules/materials/kit --import
godot --headless --path nex_modules/materials/kit --script res://validate_kit.gd
```

Expected: `M04_MATERIAL_KIT_CHECK_PASS` and `KIT_LOAD_OK`.

## Boundaries

No shader compilation, renderer integration, scene application, runtime, build pipeline, compression or production art. No FPS, frame-time, VRAM, visual-quality or gain claim. The kit is reference data, not a visual benchmark.

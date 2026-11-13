# NEX M02-S05 · RenderPassport prototype (capability matrix and profiles)

**Status:** `PROTOTYPE / INVENTORY_ONLY / NO_RENDERING / NO_PROJECT_GODOT_WRITES / NO_REMOTE_HARDWARE`
**Work Order:** NEX-M02-S05-WO-001 (Issue #32) · **Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

- **Capability matrix** (`capability_matrix.v1.json`): camera/visibility/composition capabilities with documented state per renderer (`forward_plus`, `gl_compatibility`), an official source URL, and an explicit `DOCUMENTED_UNVERIFIED_UNLESS_PROBED` verification policy.
- **RenderPassport**: validates an inventory (Godot 4.7 / Windows / renderer / driver / GPU / VRAM), applies the Windows fallback chain Vulkan → D3D12 → GL Compatibility, and reports capability states. A runtime `probe` overrides documented states with `MEASURED_ENABLED`/`MEASURED_DISABLED`; without a probe, status is `INCONCLUSIVE_NOT_PROBED`.
- **Profiles** (`profiles.v1.json`): `quality`, `balanced`, `performance` only. No "ultra" tier, no FPS claim. Values are reversible settings.
- **Profile selection/switch**: applies effective renderer/driver, disables visibility features the renderer does not support (`degraded_features`), and verifies round-trip switching.
- **Explicit flags:** `project_godot_writes=false`, `personal_hardware_collected=false`, `gpu_name_implies_capability=false`.

## Fallbacks

| Input | Effective | Degraded |
|---|---|---|
| forward_plus + vulkan | forward_plus + vulkan | no |
| forward_plus + vulkan, Vulkan unavailable | forward_plus + d3d12 | no |
| Vulkan and D3D12 unavailable | gl_compatibility + opengl3 | yes |
| unknown renderer/driver, non-Windows, wrong version, no GPU/VRAM | `INCONCLUSIVE` / `NO_GO` | — |

## API

| Method | Purpose |
|---|---|
| `load_data()` / `configure(overrides)` | Load/validate matrix and profiles. |
| `build_passport(inventory, probe)` | Inventory, fallbacks, capability states, flags. |
| `select_profile(name, inventory, probe)` | Effective settings and degraded features. |
| `switch_profile(from, to, inventory, probe)` | Diff and verified round trip. |
| `list_profiles()` | Available profiles. |
| `get_report()` | Last report copy. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render3d/profiles `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M02_S05_SMOKE_PASS: 87 checks`; log committed under `evidence/`.

## Limits (explicit)

- Capability states are **documentation-derived and unverified** unless a probe supplies them. The matrix does not prove runtime support on a specific driver.
- No rendering, benchmark, screenshot, GPU/VRAM/frame-time measurement. Profiles are settings; achieving a profile is not proven.
- No project.godot write, no remote hardware collection, no telemetry upload.
- Culling/LOD/streaming tuning belongs to M06; lighting/GI to M03; PBR to M04; VFX to M05. This prototype only inventories native capabilities.
- `gl_compatibility` disables mesh LOD, visibility ranges and occlusion culling in effective settings; this is documented behavior, to be re-verified with a runtime probe in a future scene-integration WO.

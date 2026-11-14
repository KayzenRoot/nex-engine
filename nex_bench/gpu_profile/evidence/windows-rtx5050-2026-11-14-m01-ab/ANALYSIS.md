# NEX M09 · M01 scene A/B/A — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the `ab-low` → `ab-high` preset difference remain observable when the
workload is the three admitted M01 base scenes instead of the synthetic
200-proxy grid? The answer below is limited to this session, this GPU, this
driver and these three scene compositions.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE` selecting `corridor_static`, `arena_combat` or
  `dense_city` from `res://scenes/base/`.
- Each scene is instanced with its own camera, directional light and omni
  lights. Deterministic fillers bring the total `MeshInstance3D` count to 100
  in every scene; the harness fails the stage if the runtime count differs.
- `ab-low`: 0.5 resolution scale, MSAA off, low shadows, 1024 atlas, glow off.
- `ab-high`: 1.0 resolution scale, MSAA 4x, ultra shadows, 4096 atlas, glow on.
- VSync disabled, `max_fps = 240`, 1280×720, 2 s warmup and 30 s observation
  per capture through `nex_gpu_render_profile.v2`.
- Sequence per scene: low, high, low, high, low, high. Three samples per cell.
- Every capture passed `validate_preset_ab.py`, which checks
  scene/layout/proxy/effect/max_fps/vsync and delegates aggregates to the
  canonical GPU profile validator.

## Results (median of three runs)

| Scene | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---|---|---:|---:|---:|---:|---:|---:|
| Corridor | ab-low | 0.083 | 0.088 | 0.215 | 0.347 | 4.208 | 229.24 |
| Corridor | ab-high | 0.416 | 0.423 | 0.571 | 0.452 | 4.218 | 226.99 |
| Arena | ab-low | 0.103 | 0.109 | 0.246 | 0.345 | 4.218 | 228.03 |
| Arena | ab-high | 0.455 | 0.462 | 0.614 | 0.435 | 4.231 | 225.66 |
| City | ab-low | 0.079 | 0.084 | 0.213 | 0.325 | 4.284 | 222.32 |
| City | ab-high | 0.358 | 0.362 | 0.505 | 0.432 | 4.270 | 223.25 |

### ab-high vs ab-low (median deltas)

| Scene | GPU p95 | GPU p50 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---|---:|---:|---:|---:|---:|---:|
| Corridor | +380.7% | +401.2% | +165.6% | +30.3% | +0.2% | −1.0% |
| Arena | +323.9% | +341.7% | +149.6% | +26.1% | +0.3% | −1.0% |
| City | +331.0% | +353.2% | +137.1% | +32.9% | −0.3% | +0.4% |

### A/A stability (three ab-low runs)

| Scene | GPU p95 spread | CPU p95 spread | Pacing p95 spread | 1% low spread |
|---|---:|---:|---:|---:|
| Corridor | 3.4% | 12.1% | 0.0% | 1.7% |
| Arena | 7.3% | 14.2% | 0.3% | 2.7% |
| City | 1.2% | 1.2% | 1.1% | 2.2% |

## Observations

- The high preset costs more GPU time in every scene. The median GPU p95
  increases from 0.084–0.109 ms to 0.362–0.462 ms; the absolute differences are
  small because the 100-mesh workload is light for this GPU.
- The direction is consistent across all three scenes, but the magnitude is
  scene-dependent: corridor +380.7%, arena +323.9%, city +331.0% at GPU p95.
- Pacing remains capped near 240 FPS (p95 interval ≈ 4.2 ms) in both presets;
  the 1% low changes are within −1.0% to +0.4% and are not a gain claim.
- Renderer allocation is session history, not device VRAM: the median
  `RENDERER_ALLOCATION_BYTES` is about 23.4 MB for ab-low and 176–182 MB for
  ab-high. This is consistent with the higher-resolution/MSAA/atlas settings
  but is not a VRAM measurement.
- Corridor ab-high has a visible first-run high outlier: GPU p95 0.542 ms in
  run 1 vs 0.421/0.423 ms in runs 2/3 (28.6% spread). The median (0.423 ms) is
  used above. Arena and city ab-high spreads are 0.0% and 0.3%.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- Three runs per cell; the corridor ab-high first-run outlier is documented,
  not removed.
- Fillers are deterministic but may overlap base-scene props. The workload is
  a stress composition, not a visual-quality scene.
- GPU render timing can describe earlier work and is not input-to-photon.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1`; it is not the full preset
  resolver and does not prove visual quality.
- No FPS gain, quality improvement or universal recommendation is claimed.

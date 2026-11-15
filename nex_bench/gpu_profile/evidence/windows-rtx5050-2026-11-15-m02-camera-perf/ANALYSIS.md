# NEX M02-S01 · Camera performance A/B/A — RTX 5050

**Status:** `PERFORMANCE_COMPARISON_MEASURED / SINGLE_SESSION / NO_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does replacing the frozen M01 scene camera with the M02 `IsometricCameraRig`
change GPU, CPU or pacing cost on the three M01 scenes?

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_CAMERA_MODE=baseline|rig`, `ab-low`, 100 proxies, 1280×720.
- The rig is configured per scene to match the baseline camera distance and FOV;
  the visual bundle shows the framing is effectively identical.
- Three runs per mode per scene; 2 s warmup and 30 s observation; VSync off and
  `max_fps = 240`.
- Every capture passed `validate_preset_ab.py`; medians of three runs are used.

## Results (median of three runs)

| Scene | Mode | GPU p95 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---|---|---:|---:|---:|---:|
| corridor_static | baseline | 0.094 | 0.366 | 4.210 | 213.79 |
| corridor_static | rig | 0.094 | 0.366 | 4.224 | 216.15 |
| arena_combat | baseline | 0.106 | 0.361 | 4.209 | 214.65 |
| arena_combat | rig | 0.107 | 0.409 | 4.221 | 219.23 |
| dense_city | baseline | 0.080 | 0.309 | 4.240 | 227.61 |
| dense_city | rig | 0.081 | 0.349 | 4.223 | 220.64 |

### Rig vs baseline (median deltas)

| Scene | GPU p95 | CPU p95 |
|---|---:|---:|
| corridor_static | 0.0% | 0.0% |
| arena_combat | +0.94% | +13.3% |
| dense_city | +1.25% | +12.94% |

## Observations

- GPU p95 is effectively unchanged (0.0% to +1.25%), consistent with the rig
  adding only a camera node and no rendering work.
- CPU p95 is unchanged in corridor and +12.9%/+13.3% in arena/city; the absolute
  values remain small (0.31–0.41 ms) and the delta may include session noise.
- Pacing remains near 4.21–4.24 ms and 1% low ranges 213–227 fps.
- This is a measured cost comparison for one preset and three static scenes,
  not an FPS or quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One preset (`ab-low`), static scenes and one camera pose per scene.
- CPU p95 deltas are small in absolute terms and not proven to be causal.
- `max_fps = 240` and disabled VSync cap frame pacing.
- No FPS gain, quality or universal recommendation is claimed.

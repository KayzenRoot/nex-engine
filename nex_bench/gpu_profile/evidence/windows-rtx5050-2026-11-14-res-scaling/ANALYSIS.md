# NEX M09 · Preset resolution scaling — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

How does the `ab-low` → `ab-high` GPU cost scale with render resolution on the
M01 `arena_combat` workload (100 meshes)? This report covers 960×540,
1280×720 and 1920×1080 in one session on one GPU.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE=arena_combat`, `NEX_PRESET_AB_WIDTH/HEIGHT` and
  `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- The native-resolution flag disables the project's `canvas_items` stretch
  mode so the measured viewport equals the requested window size. Without it,
  the first attempt recorded a logical 1280×720 viewport for every window
  size; those captures were discarded before evidence assembly.
- Each run uses 100 meshes, 2 s warmup and 30 s observation through
  `nex_gpu_render_profile.v2`; VSync is disabled and `max_fps = 240`.
- Sequence per resolution: low, high, low, high, low, high (three runs per
  preset). Every capture passed `validate_preset_ab.py`.

## Results (median of three runs)

| Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---|---|---:|---:|---:|---:|---:|---:|
| 960×540 | ab-low | 0.093 | 0.096 | 0.222 | 0.322 | 4.202 | 227.25 |
| 960×540 | ab-high | 0.308 | 0.317 | 0.454 | 0.443 | 4.203 | 228.82 |
| 1280×720 | ab-low | 0.103 | 0.106 | 0.108 | 0.328 | 4.250 | 227.70 |
| 1280×720 | ab-high | 0.454 | 0.460 | 0.604 | 0.438 | 4.255 | 226.90 |
| 1920×1080 | ab-low | 0.142 | 0.156 | 0.159 | 0.329 | 4.242 | 226.27 |
| 1920×1080 | ab-high | 0.820 | 0.826 | 1.032 | 0.454 | 4.273 | 226.35 |

### ab-high vs ab-low (GPU p95 median)

| Resolution | Delta |
|---|---:|
| 960×540 | +230.2% |
| 1280×720 | +334.0% |
| 1920×1080 | +429.5% |

### Scaling 960×540 → 1920×1080

| Preset | GPU p95 scaling |
|---|---:|
| ab-low | +62.5% |
| ab-high | +160.6% |

### A/A stability (GPU p95 spread, 3 ab-low runs)

| Resolution | Spread |
|---|---:|
| 960×540 | 0.0% |
| 1280×720 | 0.9% |
| 1920×1080 | 0.6% |

## Observations

- The high preset costs more GPU time at every resolution, and its relative
  cost grows with resolution: +230.2% at 960×540, +334.0% at 1280×720 and
  +429.5% at 1920×1080.
- The high preset scales faster in absolute terms: GPU p95 rises 160.6% from
  960×540 to 1920×1080, while ab-low rises 62.5%.
- Absolute GPU times remain below 1.1 ms p99 in every cell; 100 meshes are a
  light workload for this GPU, and pacing stays near the 240 fps cap.
- 1% low deltas range from −0.4% to +0.7%; this is not a gain claim.
- The 960×540 ab-low p99 has one run at 0.222 ms vs 0.098/0.225 ms; the median
  is reported and the A/A p95 spread is 0.0%.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One scene (`arena_combat`) and one 100-mesh composition; fillers may overlap
  base-scene props.
- 1920×1080 is the largest 16:9 mode tested because the display is 2560×1080;
  2560×1440 is not covered.
- The native-resolution flag differs from the project's default stretch mode;
  results describe native viewport rendering, not the stretched default.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

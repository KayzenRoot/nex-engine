# NEX M09 · 2560×1440 resolution scaling — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the resolution-dominance pattern extend to 2560×1440, and does the M03
ab-high match observed at 1280×720 survive this resolution? This report fills
the last documented resolution gap of the M09 campaign.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE=arena_combat`, `NEX_PRESET_AB_PROXY_COUNT=100`,
  `NEX_PRESET_AB_WIDTH=2560`, `NEX_PRESET_AB_HEIGHT=1440` and
  `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- 100 proxies = 34 base meshes + 66 deterministic fillers.
- Three runs per preset (low, high, low, high, low, high), 2 s warmup and
  30 s observation; VSync is disabled and `max_fps = 240`.
- The desktop is 2560×1080; the 2560×1440 window is taller than the display,
  but Godot reports and captures a 2560×1440 viewport.
- Every capture passed `validate_preset_ab.py` with proxy count, scene, layout
  and viewport provenance.
- The 960/1280/1920 context comes from the already integrated `res-scaling`
  report measured earlier on the same day; it is not re-measured here.
- The M03 prediction is quoted only as context from
  `docs/benchmarks/m03/budget-validation.v1.json`.

## Results (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 100 | 2560×1440 | ab-low | 0.202 | 0.206 | 0.314 | 0.390 | 4.268 | 222.75 |
| 100 | 2560×1440 | ab-high | 1.315 | 1.547 | 1.698 | 0.493 | 4.269 | 223.12 |

### ab-high vs ab-low (GPU p95 median)

| Proxies | 2560×1440 |
|---:|---:|
| 100 | +651.0% |

### Resolution scaling 1920×1080 → 2560×1440 (GPU p95, different session)

| Preset | 1920×1080 | 2560×1440 | Delta |
|---|---:|---:|---:|
| ab-low | 0.156 | 0.206 | +32.1% |
| ab-high | 0.826 | 1.547 | +87.3% |

### Resolution scaling 960×540 → 2560×1440 (GPU p95, different session)

| Preset | 960×540 | 2560×1440 | Delta |
|---|---:|---:|---:|
| ab-low | 0.096 | 0.206 | +114.6% |
| ab-high | 0.317 | 1.547 | +388.0% |

### Context: M03 model prediction vs measured 2560/1440

| Preset | Predicted ms | Measured p95 ms | Error |
|---|---:|---:|---:|
| ab-low | 0.379 | 0.206 | +84.0% |
| ab-high | 0.460 | 1.547 | −70.3% |

## Observations

- The resolution-dominance pattern extends to 2560×1440: high/low grows from
  +323.9% at 1280×720 to +651.0% at 2560×1440, and GPU p95 rises +87.3%
  (ab-high) from 1920×1080 to 2560×1440.
- The M03 ab-high prediction (0.460 ms) is 70.3% below the measured 1.547 ms
  at 2560×1440; the 2% match is confined to 1280×720 and does not survive
  this resolution.
- The M03 ab-low prediction (0.379 ms) is 84.0% above the measured 0.206 ms,
  so the low preset remains overestimated, but by less than at 1280×720.
- The first ab-low run has an isolated 1% low outlier (38.9 fps), likely a
  first-run window/allocation hitch; medians are used and the 1% low is not
  used for a trend claim.
- Pacing remains near 4.27 ms; 1% low for ab-high is stable at 221.97–224.34
  fps.
- This is a measured cost for one scene and one proxy count, not a universal
  rule or a quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One scene, one proxy count (100) and one resolution (2560×1440); the
  960/1280/1920 context is from a different session and is labeled as such.
- The 2560×1440 window is taller than the 2560×1080 desktop; the viewport is
  captured off-screen and the window is clipped.
- Three runs per preset; the ab-low 1% low has an 82.9% spread due to one
  outlier.
- Native resolution disables the canvas_items stretch mode.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

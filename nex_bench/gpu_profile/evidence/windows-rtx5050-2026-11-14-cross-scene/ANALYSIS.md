# NEX M09 · Cross-scene interaction — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the proxy × resolution pattern measured on `arena_combat` repeat on
`corridor_static` and `dense_city`? This report covers 50/100 proxies at
960×540 and 1920×1080 for two additional M01 scenes in one session.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE`, `NEX_PRESET_AB_PROXY_COUNT` 50/100,
  `NEX_PRESET_AB_WIDTH/HEIGHT` and `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- Each scene uses its base meshes plus deterministic fillers to 50 or 100
  meshes; 25 proxies is not used because the interaction baseline uses 50.
- Each cell has 3 runs per preset (low, high, low, high, low, high), 2 s
  warmup and 30 s observation; VSync is disabled and `max_fps = 240`.
- Every capture passed `validate_preset_ab.py` with scene, proxy count,
  layout and viewport provenance.

## Results — corridor_static (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.070 | 0.071 | 0.075 | 0.311 | 4.275 | 223.56 |
| 50 | 960×540 | ab-high | 0.270 | 0.280 | 0.416 | 0.427 | 4.252 | 224.80 |
| 50 | 1920×1080 | ab-low | 0.125 | 0.136 | 0.139 | 0.328 | 4.284 | 225.83 |
| 50 | 1920×1080 | ab-high | 0.778 | 0.784 | 0.991 | 0.425 | 4.242 | 226.20 |
| 100 | 960×540 | ab-low | 0.070 | 0.071 | 0.073 | 0.337 | 4.276 | 223.86 |
| 100 | 960×540 | ab-high | 0.270 | 0.280 | 0.416 | 0.442 | 4.293 | 224.15 |
| 100 | 1920×1080 | ab-low | 0.128 | 0.140 | 0.143 | 0.338 | 4.288 | 224.33 |
| 100 | 1920×1080 | ab-high | 0.785 | 0.790 | 0.998 | 0.451 | 4.259 | 225.86 |

## Results — dense_city (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.067 | 0.068 | 0.069 | 0.306 | 4.261 | 223.73 |
| 50 | 960×540 | ab-high | 0.228 | 0.235 | 0.352 | 0.407 | 4.250 | 225.93 |
| 50 | 1920×1080 | ab-low | 0.109 | 0.122 | 0.125 | 0.320 | 4.243 | 225.54 |
| 50 | 1920×1080 | ab-high | 0.679 | 0.685 | 0.883 | 0.418 | 4.294 | 224.71 |
| 100 | 960×540 | ab-low | 0.068 | 0.069 | 0.071 | 0.326 | 4.247 | 225.84 |
| 100 | 960×540 | ab-high | 0.233 | 0.241 | 0.366 | 0.429 | 4.251 | 225.41 |
| 100 | 1920×1080 | ab-low | 0.110 | 0.124 | 0.126 | 0.330 | 4.281 | 223.48 |
| 100 | 1920×1080 | ab-high | 0.685 | 0.691 | 0.890 | 0.444 | 4.247 | 226.89 |

## Deltas ab-high vs ab-low (GPU p95 median)

| Scene | 50/960×540 | 50/1920×1080 | 100/960×540 | 100/1920×1080 |
|---|---:|---:|---:|---:|
| corridor_static | +294.4% | +476.5% | +294.4% | +464.3% |
| dense_city | +245.6% | +461.5% | +249.3% | +457.3% |

## Resolution scaling 960×540 → 1920×1080 (GPU p95)

| Scene | Proxies | ab-low | ab-high |
|---|---:|---:|---:|
| corridor_static | 50 | +91.5% | +180.0% |
| corridor_static | 100 | +97.2% | +182.1% |
| dense_city | 50 | +79.4% | +191.5% |
| dense_city | 100 | +79.7% | +186.7% |

## Proxy scaling 50 → 100 (GPU p95)

| Scene | Resolution | ab-low | ab-high |
|---|---|---:|---:|
| corridor_static | 960×540 | 0.0% | 0.0% |
| corridor_static | 1920×1080 | +2.9% | +0.8% |
| dense_city | 960×540 | +1.5% | +2.6% |
| dense_city | 1920×1080 | +1.6% | +0.9% |

## Observations

- The arena pattern repeats in both scenes: resolution dominates GPU cost and
  the high preset's relative cost grows with resolution.
- Corridor GPU p95 high vs low rises from +294.4% at 960×540 to +464.3–476.5%
  at 1920×1080; city rises from +245.6–249.3% to +457.3–461.5%.
- Proxy scaling 50→100 changes GPU p95 by 0.0–2.9% in these scenes, while
  resolution scaling 960→1920 changes it by +79.4–97.2% (ab-low) and
  +180.0–191.5% (ab-high).
- CPU p95 is higher in corridor than city at the same cell, consistent with
  the corridor's more numerous omni lights and scene layout.
- Pacing remains near 4.25 ms (240 fps cap); 1% low deltas are within −0.4% to
  +1.5% and are not a gain claim.
- This is consistent with a pixel-bound preset cost at 50–100 meshes across
  the three M01 scenes; it is not a universal rule or a quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- Two scenes only; `arena_combat` is covered by a separate report.
- Two proxy counts and two resolutions; 200 proxies and 2560×1440 are not
  covered.
- Native resolution disables the project's canvas_items stretch mode.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

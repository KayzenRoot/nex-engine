# NEX M09 · 200-proxy interaction — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the pixel-bound pattern measured at 50/100 proxies hold at the upper
proxy bound (200) on `arena_combat`? This report covers 200 proxies at
960×540 and 1920×1080 in one session and compares the result with the
separate 50/100 interaction report.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE=arena_combat`, `NEX_PRESET_AB_PROXY_COUNT=200`,
  `NEX_PRESET_AB_WIDTH/HEIGHT` and `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- 200 proxies = 34 base meshes + 166 deterministic fillers.
- Each resolution has 3 runs per preset (low, high, low, high, low, high),
  2 s warmup and 30 s observation; VSync is disabled and `max_fps = 240`.
- Every capture passed `validate_preset_ab.py` with proxy count, scene, layout
  and viewport provenance.
- The 50/100 comparison comes from the already integrated
  `interaction.v1.json` report measured earlier on the same day; it is not
  re-measured in this session.

## Results (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 200 | 960×540 | ab-low | 0.095 | 0.098 | 0.221 | 0.357 | 4.247 | 224.05 |
| 200 | 960×540 | ab-high | 0.315 | 0.322 | 0.468 | 0.503 | 4.264 | 224.91 |
| 200 | 1920×1080 | ab-low | 0.145 | 0.157 | 0.160 | 0.361 | 4.289 | 225.70 |
| 200 | 1920×1080 | ab-high | 0.838 | 0.845 | 1.052 | 0.518 | 4.294 | 225.11 |

### ab-high vs ab-low (GPU p95 median)

| Proxies | 960×540 | 1920×1080 |
|---:|---:|---:|
| 200 | +228.6% | +438.2% |

### Resolution scaling 960×540 → 1920×1080 (GPU p95)

| Proxies | ab-low | ab-high |
|---:|---:|---:|
| 200 | +60.2% | +162.4% |

### Context: 100 → 200 proxies (GPU p95, different session)

| Resolution | ab-low | ab-high |
|---|---:|---:|
| 960×540 | +2.1% | +2.5% |
| 1920×1080 | +9.0% | +2.3% |

## Observations

- The pixel-bound pattern holds at 200 proxies: resolution scaling raises GPU
  p95 by +60.2% (ab-low) and +162.4% (ab-high), while going from 100 to 200
  proxies changes it by only +2.1–9.0%.
- The high preset's relative cost is larger at 1920×1080 (+438.2%) than at
  960×540 (+228.6%), consistent with the 50/100 report.
- The 200/1920 high-vs-low delta (+438.2%) is slightly below the 100/1920
  value (+473.6%) from the other session; this is a cross-session comparison
  and not evidence of a monotonic trend.
- CPU p95 rises with proxy count: 0.357/0.503 ms at 960×540 and 0.361/0.518 ms
  at 1920×1080, higher than the 50/100 cells.
- Pacing remains near 4.25–4.29 ms; 1% low deltas are −0.3% to +0.4%.
- This is a measured cost for one scene and one proxy count, not a universal
  rule or a quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One scene and one proxy count (200); 50/100 context is from a different
  session and is labeled as such.
- Two resolutions only; 2560×1440 is not covered.
- Native resolution disables the project's canvas_items stretch mode.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

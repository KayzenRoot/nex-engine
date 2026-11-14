# NEX M09 · Proxy × resolution interaction — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

At 50 and 100 meshes, does the `ab-low` → `ab-high` cost depend on resolution
and object count together, or is one dimension dominant? This report covers
the M01 `arena_combat` scene at 960×540 and 1920×1080 in one session.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE=arena_combat`, `NEX_PRESET_AB_PROXY_COUNT` 50/100,
  `NEX_PRESET_AB_WIDTH/HEIGHT` and `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- The 50-proxy bucket uses 16 deterministic fillers over the 34 base meshes;
  25 proxies is not possible without removing base geometry, which is out of
  scope.
- Each cell has 3 runs per preset (low, high, low, high, low, high), 2 s
  warmup and 30 s observation; VSync is disabled and `max_fps = 240`.
- Every capture passed `validate_preset_ab.py` with proxy count, scene, layout
  and viewport provenance.

## Results (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.092 | 0.096 | 0.097 | 0.233 | 4.240 | 230.10 |
| 50 | 960×540 | ab-high | 0.302 | 0.307 | 0.309 | 0.304 | 4.242 | 229.92 |
| 50 | 1920×1080 | ab-low | 0.139 | 0.144 | 0.147 | 0.236 | 4.241 | 231.41 |
| 50 | 1920×1080 | ab-high | 0.812 | 0.820 | 1.043 | 0.306 | 4.240 | 230.18 |
| 100 | 960×540 | ab-low | 0.092 | 0.096 | 0.097 | 0.247 | 4.240 | 230.21 |
| 100 | 960×540 | ab-high | 0.309 | 0.314 | 0.316 | 0.320 | 4.240 | 228.85 |
| 100 | 1920×1080 | ab-low | 0.139 | 0.144 | 0.149 | 0.246 | 4.243 | 230.94 |
| 100 | 1920×1080 | ab-high | 0.820 | 0.826 | 1.013 | 0.330 | 4.243 | 229.02 |

### ab-high vs ab-low (GPU p95 median)

| Proxies | 960×540 | 1920×1080 |
|---:|---:|---:|
| 50 | +219.8% | +469.4% |
| 100 | +227.1% | +473.6% |

### Resolution scaling 960×540 → 1920×1080 (GPU p95)

| Proxies | ab-low | ab-high |
|---:|---:|---:|
| 50 | +50.0% | +167.1% |
| 100 | +50.0% | +163.1% |

### Proxy scaling 50 → 100 (GPU p95)

| Resolution | ab-low | ab-high |
|---|---:|---:|
| 960×540 | 0.0% | +2.3% |
| 1920×1080 | 0.0% | +0.7% |

## Observations

- Resolution dominates GPU cost in this range: doubling proxies from 50 to 100
  changes GPU p95 by 0.0–2.3%, while moving from 960×540 to 1920×1080 raises it
  50.0% (ab-low) and 163.1–167.1% (ab-high).
- The high preset's relative cost grows with resolution at both proxy counts:
  +219.8%/+227.1% at 960×540 versus +469.4%/+473.6% at 1920×1080.
- CPU p95 is the dimension that reacts to proxy count: it rises 4.2–7.8% from
  50 to 100 proxies, while GPU p95 stays essentially flat.
- Pacing remains near 4.24 ms (240 fps cap); 1% low deltas are −0.8% to −0.1%.
- This is consistent with a pixel-bound preset cost at 50–100 meshes on this
  GPU; it is not a universal rule or a quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One scene and two proxy counts; 25 proxies is impossible without removing
  base geometry, and 200 proxies was not measured here.
- Two resolutions only; 2560×1440 is not covered.
- Native resolution disables the project's canvas_items stretch mode.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

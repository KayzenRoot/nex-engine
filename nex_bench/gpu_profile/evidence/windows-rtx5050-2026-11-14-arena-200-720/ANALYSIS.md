# NEX M09 · 200-proxy arena at 1280×720 — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the 1280×720 high-preset behavior observed at 100 proxies persist at 200
proxies? This report fills the calibration-resolution gap in the 200-proxy
evidence and provides a same-resolution context for the M03 light-cost model.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE=arena_combat`, `NEX_PRESET_AB_PROXY_COUNT=200`,
  `NEX_PRESET_AB_WIDTH=1280`, `NEX_PRESET_AB_HEIGHT=720` and
  `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- 200 proxies = 34 base meshes + 166 deterministic fillers.
- Three runs per preset (low, high, low, high, low, high), 2 s warmup and
  30 s observation; VSync is disabled and `max_fps = 240`.
- Every capture passed `validate_preset_ab.py` with proxy count, scene, layout
  and viewport provenance.
- The 100-proxy context at 1280×720 comes from the already integrated
  `m01-ab.v1.json` report measured earlier on the same day; it is not
  re-measured in this session.
- The M03 model prediction is quoted only as context from
  `docs/benchmarks/m03/light-cost-model.v1.json` (arena: 4 omni lights,
  directional shadow, 0 shadowed omni at ab-low and 4 at ab-high).

## Results (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 200 | 1280×720 | ab-low | 0.107 | 0.111 | 0.116 | 0.445 | 4.232 | 207.25 |
| 200 | 1280×720 | ab-high | 0.463 | 0.468 | 0.656 | 0.647 | 4.234 | 219.25 |

### ab-high vs ab-low (GPU p95 median)

| Proxies | 1280×720 |
|---:|---:|
| 200 | +321.6% |

### Context: 100 → 200 proxies at 1280×720 (GPU p95, different session)

| Preset | 100 proxies | 200 proxies | Delta |
|---|---:|---:|---:|
| ab-low | 0.109 | 0.111 | +1.8% |
| ab-high | 0.462 | 0.468 | +1.3% |

### Context: M03 model prediction vs measured 200/1280

| Preset | Predicted ms | Measured p95 ms | Error |
|---|---:|---:|---:|
| ab-low | 0.379 | 0.111 | +241.4% |
| ab-high | 0.460 | 0.468 | −1.7% |

## Observations

- GPU p95 at 200/1280 is nearly identical to the 100-proxy cell: +1.8%
  (ab-low) and +1.3% (ab-high). Proxy count is not the dominant GPU term at
  this resolution.
- The ab-high prediction (0.460 ms) remains within 2% of the measured value
  (0.468 ms) at 200 proxies, so the calibration-resolution match is robust to
  this proxy change.
- The ab-low prediction is still far above the measured value (+241.4%),
  consistent with unmodeled preset rendering such as resolution scale, MSAA
  and glow.
- CPU p95 rises more than GPU p95 when going from 100 to 200 proxies
  (0.345→0.445 ms ab-low, 0.435→0.647 ms ab-high), while GPU p95 stays near
  0.11/0.47 ms.
- Pacing remains near 4.23 ms; 1% low moves from 228.03/225.66 fps at 100
  proxies to 207.25/219.25 fps at 200 proxies, with 7.6–9.3% spread, so this
  metric is not stable enough for a trend claim.
- This is a measured cost for one scene and one proxy count, not a universal
  rule or a quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One scene, one proxy count (200) and one resolution (1280×720); the
  100-proxy context is from a different session and is labeled as such.
- Three runs per preset; 1% low spread is 7.6–9.3%.
- Native resolution disables the project's canvas_items stretch mode.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

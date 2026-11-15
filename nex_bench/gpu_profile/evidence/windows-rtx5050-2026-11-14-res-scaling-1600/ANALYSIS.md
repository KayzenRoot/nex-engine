# NEX M09 · 1600×900 resolution scaling — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the resolution curve remain monotonic between 1280×720 and 1920×1080,
and how far is the M03 ab-high prediction from the measured cost at 1600×900?
This fills the intermediate resolution point.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_SCENE=arena_combat`, `NEX_PRESET_AB_PROXY_COUNT=100`,
  `NEX_PRESET_AB_WIDTH=1600`, `NEX_PRESET_AB_HEIGHT=900` and
  `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- 100 proxies = 34 base meshes + 66 deterministic fillers.
- Three runs per preset (low, high, low, high, low, high), 2 s warmup and
  30 s observation; VSync is disabled and `max_fps = 240`.
- Every capture passed `validate_preset_ab.py` with proxy count, scene, layout
  and viewport provenance.
- The 1280×720 and 1920×1080 context comes from the already integrated
  `res-scaling` report; the M03 prediction is quoted only as context.

## Results (median of three runs)

| Proxies | Resolution | Preset | GPU p50 ms | GPU p95 ms | GPU p99 ms | CPU p95 ms | Pacing p95 ms | 1% low FPS |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 100 | 1600×900 | ab-low | 0.120 | 0.133 | 0.135 | 0.462 | 4.252 | 213.08 |
| 100 | 1600×900 | ab-high | 0.625 | 0.632 | 0.917 | 0.749 | 4.274 | 214.03 |

### ab-high vs ab-low (GPU p95 median)

| Proxies | 1600×900 |
|---:|---:|
| 100 | +375.2% |

### Resolution scaling (GPU p95, different session)

| Preset | 1280×720 | 1600×900 | 1920×1080 | 1280→1600 | 1600→1920 |
|---|---:|---:|---:|---:|---:|
| ab-low | 0.106 | 0.133 | 0.156 | +25.5% | +17.3% |
| ab-high | 0.460 | 0.632 | 0.826 | +37.4% | +30.7% |

### Context: M03 model prediction vs measured 1600/900

| Preset | Predicted ms | Measured p95 ms | Error |
|---|---:|---:|---:|
| ab-low | 0.379 | 0.133 | +185.0% |
| ab-high | 0.460 | 0.632 | −27.2% |

## Observations

- The resolution curve remains monotonic: GPU p95 rises from 1280×720 to
  1600×900 and from 1600×900 to 1920×1080 in both presets.
- The high preset grows faster with resolution: +37.4% then +30.7%, versus
  +25.5% then +17.3% for the low preset.
- The M03 ab-high prediction is 27.2% below the measured 1600×900 value,
  between the 2% match at 1280×720 and the 44.3% error at 1920×1080.
- The M03 ab-low prediction remains far above measured (+185.0%), consistent
  with unmodeled resolution scale, MSAA and glow.
- This is a measured cost for one scene and one proxy count, not a universal
  rule or a quality claim.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- One scene, one proxy count (100) and one resolution (1600×900); the
  1280/1920 context is from a different session and is labeled as such.
- Three runs per preset; GPU p95 spread is 0.5–0.8%.
- Native resolution disables the canvas_items stretch mode.
- `max_fps = 240` and disabled VSync cap frame pacing.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS gain, quality or universal recommendation is claimed.

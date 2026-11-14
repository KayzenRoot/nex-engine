# NEX M09 · 2560×1440 resolution scaling — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1440` · **Source SHA:** `39633b347784e66526c60be6c655d007d86f16cd`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus

## Células (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 100 | 2560×1440 | ab-low | 0.202 | 0.206 | 0.314 | 0.390 | 4.268 | 222.75 |
| 100 | 2560×1440 | ab-high | 1.315 | 1.547 | 1.698 | 0.493 | 4.269 | 223.12 |

## ab-high vs ab-low (GPU p95)

- Delta: +651.0%.

## Contexto de resolução (GPU p95, sessão separada)

| Preset | 960×540 | 1280×720 | 1920×1080 | 2560×1440 | 1920→2560 | 960→2560 |
|---|---:|---:|---:|---:|---:|---:|
| ab-low | 0.096 | 0.106 | 0.156 | 0.206 | +32.1% | +114.6% |
| ab-high | 0.317 | 0.460 | 0.826 | 1.547 | +87.3% | +388.0% |

## Contexto do modelo M03

| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |
|---|---:|---:|---:|---|
| ab-low | 0.379 | 0.206 | +84.0% | não |
| ab-high | 0.460 | 1.547 | -70.3% | não |

## Observações

- high/low grows from +323.9% at 1280x720 to +651.0% at 2560x1440
- GPU p95 rises +32.1% (ab-low) and +87.3% (ab-high) from 1920x1080 to 2560x1440
- the ab-high M03 prediction (0.460 ms) is -70.3% from the measured 2560x1440 value; the 2% match does not survive this resolution
- the ab-low M03 prediction (0.379 ms) is +84.0% above the measured value, so the low preset remains overestimated
- the first ab-low run has an isolated 1% low outlier (38.9 fps); medians are used and the 1% low is not used for a trend claim

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- one scene, one proxy count (100) and one resolution (2560x1440)
- the 960/1280/1920 context is from a different session and is labeled as such
- the 2560x1440 window is taller than the 2560x1080 desktop; the viewport is captured off-screen
- three runs per preset; the ab-low 1% low has an 82.9% spread due to one outlier
- native resolution disables the canvas_items stretch mode
- max_fps 240 and disabled VSync cap frame pacing
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_res_scaling_1440.py`; não é benchmark nem claim de ganho.

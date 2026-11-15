# NEX M09 · 1600×900 resolution scaling — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1600` · **Source SHA:** `b9fd2ed1cbde0625200b104fbd2c34796258dad3`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus

## Células (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 100 | 1600×900 | ab-low | 0.120 | 0.133 | 0.135 | 0.462 | 4.252 | 213.08 |
| 100 | 1600×900 | ab-high | 0.625 | 0.632 | 0.917 | 0.749 | 4.274 | 214.03 |

## ab-high vs ab-low (GPU p95)

- Delta: +375.2%.

## Contexto de resolução (GPU p95, sessão separada)

| Preset | 1280×720 | 1600×900 | 1920×1080 | 1280→1600 | 1600→1920 |
|---|---:|---:|---:|---:|---:|
| ab-low | 0.106 | 0.133 | 0.156 | +25.5% | +17.3% |
| ab-high | 0.460 | 0.632 | 0.826 | +37.4% | +30.7% |

## Contexto do modelo M03

| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |
|---|---:|---:|---:|---|
| ab-low | 0.379 | 0.133 | +185.0% | não |
| ab-high | 0.460 | 0.632 | -27.2% | não |

## Observações

- GPU p95 rises from 1280x720 to 1600x900 by +25.5% (ab-low) and +37.4% (ab-high)
- GPU p95 rises from 1600x900 to 1920x1080 by +17.3% (ab-low) and +30.7% (ab-high)
- the ab-high M03 prediction (0.460 ms) is -27.2% from the measured 1600x900 value, between the 1280x720 match and the 1920x1080 error
- the ab-low M03 prediction (0.379 ms) is +185.0% above the measured value, consistent with unmodeled resolution scale, MSAA and glow
- this is a measured cost for one scene and one proxy count, not a universal rule or a quality claim

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- one scene, one proxy count (100) and one resolution (1600x900)
- the 1280/1920 context is from a different session and is labeled as such
- three runs per preset; GPU p95 spread is 0.5-0.8%
- native resolution disables the canvas_items stretch mode
- max_fps 240 and disabled VSync cap frame pacing
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_res_scaling_1600.py`; não é benchmark nem claim de ganho.

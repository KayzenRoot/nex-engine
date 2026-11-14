# NEX M09 · 200-proxy arena at 1280×720 — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-arena-200-720` · **Source SHA:** `99eaad041b84c373da33ec1bb8a5922c31f4dad4`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus

## Células (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 200 | 1280×720 | ab-low | 0.107 | 0.111 | 0.116 | 0.445 | 4.232 | 207.25 |
| 200 | 1280×720 | ab-high | 0.463 | 0.468 | 0.656 | 0.647 | 4.234 | 219.25 |

## ab-high vs ab-low (GPU p95)

- Delta: +321.6%.

## Contexto 100 → 200 proxies (GPU p95, sessão separada)

| Preset | 100 proxies | 200 proxies | Delta GPU p95 | Delta CPU p95 |
|---|---:|---:|---:|---:|
| ab-low | 0.109 | 0.111 | +1.8% | +29.0% |
| ab-high | 0.462 | 0.468 | +1.3% | +48.7% |

## Contexto do modelo M03

| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |
|---|---:|---:|---:|---|
| ab-low | 0.379 | 0.111 | +241.4% | não |
| ab-high | 0.460 | 0.468 | -1.7% | sim |

## Observações

- GPU p95 at 200/1280 is 0.111 ms (ab-low) and 0.468 ms (ab-high); 100->200 changes it by +1.8% and +1.3%
- the ab-high M03 prediction (0.460 ms) is -1.7% from the measured 200-proxy value and remains within 2%
- the ab-low M03 prediction (0.379 ms) is +241.4% above the measured value, consistent with unmodeled resolution scale, MSAA and glow
- CPU p95 rises from 0.345/0.435 ms at 100 proxies to 0.445/0.647 ms at 200 proxies
- pacing remains near 4.23 ms and 1% low spread is 7.6-9.3%, so it is not used for a trend claim

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- one scene, one proxy count (200) and one resolution (1280x720)
- the 100-proxy context is from a different session and is labeled as such
- three runs per preset; 1% low spread is 7.6-9.3%
- native resolution disables the canvas_items stretch mode
- max_fps 240 and disabled VSync cap frame pacing
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_interaction_200_720.py`; não é benchmark nem claim de ganho.

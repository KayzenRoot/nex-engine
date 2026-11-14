# NEX M09 · Proxy × resolution interaction — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction` · **Source SHA:** `2ef072c70189d5d013a62b7efc821f81078ef6d1`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Workload:** M01 Arena A/B/A · proxies [50, 100] · native resolution

## Células (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.092 | 0.096 | 0.097 | 0.233 | 4.240 | 230.10 |
| 50 | 960×540 | ab-high | 0.302 | 0.307 | 0.309 | 0.304 | 4.242 | 229.92 |
| 50 | 1920×1080 | ab-low | 0.139 | 0.144 | 0.147 | 0.236 | 4.241 | 231.41 |
| 50 | 1920×1080 | ab-high | 0.812 | 0.820 | 1.043 | 0.306 | 4.240 | 230.18 |
| 100 | 960×540 | ab-low | 0.092 | 0.096 | 0.097 | 0.247 | 4.240 | 230.21 |
| 100 | 960×540 | ab-high | 0.309 | 0.314 | 0.316 | 0.320 | 4.240 | 228.85 |
| 100 | 1920×1080 | ab-low | 0.139 | 0.144 | 0.149 | 0.246 | 4.243 | 230.94 |
| 100 | 1920×1080 | ab-high | 0.820 | 0.826 | 1.013 | 0.330 | 4.243 | 229.02 |

## Deltas ab-high vs ab-low (GPU p95)

- 50 proxies / 960×540: **+219.8%** (GPU p99 +218.6%, CPU p95 +30.5%, 1% low -0.1%).
- 50 proxies / 1920×1080: **+469.4%** (GPU p99 +609.5%, CPU p95 +29.7%, 1% low -0.5%).
- 100 proxies / 960×540: **+227.1%** (GPU p99 +225.8%, CPU p95 +29.6%, 1% low -0.6%).
- 100 proxies / 1920×1080: **+473.6%** (GPU p99 +579.9%, CPU p95 +34.1%, 1% low -0.8%).

## Escala de resolução 960×540 → 1920×1080 (GPU p95)

- 50 proxies: ab-low +50.0%, ab-high +167.1%.
- 100 proxies: ab-low +50.0%, ab-high +163.1%.

## Escala de proxies 50 → 100 (GPU p95)

- 960×540: ab-low +0.0%, ab-high +2.3%.
- 1920×1080: ab-low +0.0%, ab-high +0.7%.

## Observações

- Resolution dominates GPU cost in this range: GPU p95 high vs low is +219.8%/+227.1% at 960x540 and +469.4%/+473.6% at 1920x1080 (50/100 proxies).
- Proxy scaling 50 to 100 changes GPU p95 by +0.0%/+2.3% at 960x540 and +0.0%/+0.7% at 1920x1080.
- Resolution scaling 960x540 to 1920x1080 raises GPU p95 by +50.0% for ab-low and +167.1% for ab-high at 50 proxies.
- CPU p95 rises 4.2-7.8% from 50 to 100 proxies while GPU p95 is essentially flat, consistent with a pixel-bound GPU cost.
- Pacing remains near 4.24 ms and 1% low deltas are within -0.8% to -0.1%; no gain is claimed.

## Limitações

- single session on one RTX 5050; no cross-device or cross-session generalization
- one scene and two proxy counts; 25 proxies would require removing base geometry
- two resolutions only; 2560x1440 is not covered
- native resolution disables the project's canvas_items stretch mode
- max_fps 240 and vsync disabled; frame pacing is capped
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_interaction.py`; não é benchmark nem claim de ganho.

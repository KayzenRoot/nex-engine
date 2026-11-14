# NEX M09 · Preset resolution scaling — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling` · **Source SHA:** `6ebb98e8c7c9c6a9a0aa3faae5af7e8d4290b7f5`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Workload:** M01 Arena A/B/A · 100 meshes · native resolution

## Células (medianas de 3 runs)

| Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | GPU spread |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 960×540 | ab-low | 0.093 | 0.096 | 0.222 | 0.322 | 4.202 | 227.25 | 0.0% |
| 960×540 | ab-high | 0.308 | 0.317 | 0.454 | 0.443 | 4.203 | 228.82 | 0.3% |
| 1280×720 | ab-low | 0.103 | 0.106 | 0.108 | 0.328 | 4.250 | 227.70 | 0.9% |
| 1280×720 | ab-high | 0.454 | 0.460 | 0.604 | 0.438 | 4.255 | 226.90 | 0.4% |
| 1920×1080 | ab-low | 0.142 | 0.156 | 0.159 | 0.329 | 4.242 | 226.27 | 0.6% |
| 1920×1080 | ab-high | 0.820 | 0.826 | 1.032 | 0.454 | 4.273 | 226.35 | 0.1% |

## Deltas ab-high vs ab-low (GPU p95)

- 960x540: **+230.2%** (GPU p99 +104.5%, CPU p95 +37.6%, 1% low +0.7%).
- 1280x720: **+334.0%** (GPU p99 +459.3%, CPU p95 +33.5%, 1% low -0.4%).
- 1920x1080: **+429.5%** (GPU p99 +549.1%, CPU p95 +38.0%, 1% low +0.0%).

## Escala 960×540 → 1920×1080

- ab-low GPU p95: +62.5%.
- ab-high GPU p95: +160.6%.

## Observações

- ab-high GPU p95 cost grows with resolution: +230.2% at 960x540, +334.0% at 1280x720 and +429.5% at 1920x1080 versus ab-low.
- From 960x540 to 1920x1080, GPU p95 rises +62.5% for ab-low and +160.6% for ab-high.
- Absolute GPU p95 medians stay below 0.9 ms and pacing stays near the 240 fps cap in every cell.
- The 960x540 ab-low p99 has one run at 0.222 ms vs 0.098/0.225 ms; the median is reported and A/A p95 spread is 0.0%.
- These are measured costs for one M01 composition, not game FPS, quality or universal recommendations.

## Limitações

- single session on one RTX 5050; no cross-device or cross-session generalization
- one scene and one 100-mesh composition; fillers may overlap base-scene props
- 1920x1080 is the largest 16:9 mode tested; 2560x1440 is not covered
- native resolution disables the project's canvas_items stretch mode
- max_fps 240 and vsync disabled; frame pacing is capped
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_res_scaling.py`; não é benchmark nem claim de ganho.

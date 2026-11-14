# NEX M09 · Cross-scene interaction — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-cross-scene` · **Source SHA:** `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Workload:** 2 cenas · proxies [50, 100] · native resolution

## M01 Corridor A/B/A

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.070 | 0.071 | 0.075 | 0.311 | 4.275 | 223.56 |
| 50 | 960×540 | ab-high | 0.270 | 0.280 | 0.416 | 0.427 | 4.252 | 224.80 |
| 50 | 1920×1080 | ab-low | 0.125 | 0.136 | 0.139 | 0.328 | 4.284 | 225.83 |
| 50 | 1920×1080 | ab-high | 0.778 | 0.784 | 0.991 | 0.425 | 4.242 | 226.20 |
| 100 | 960×540 | ab-low | 0.070 | 0.071 | 0.073 | 0.337 | 4.276 | 223.86 |
| 100 | 960×540 | ab-high | 0.270 | 0.280 | 0.416 | 0.442 | 4.293 | 224.15 |
| 100 | 1920×1080 | ab-low | 0.128 | 0.140 | 0.143 | 0.338 | 4.288 | 224.33 |
| 100 | 1920×1080 | ab-high | 0.785 | 0.790 | 0.998 | 0.451 | 4.259 | 225.86 |

Deltas high vs low (GPU p95):

- 50 proxies / 960×540: **+294.4%**.
- 50 proxies / 1920×1080: **+476.5%**.
- 100 proxies / 960×540: **+294.4%**.
- 100 proxies / 1920×1080: **+464.3%**.

Escala 960×540 → 1920×1080 (GPU p95):

- 50 proxies: ab-low +91.5%, ab-high +180.0%.
- 100 proxies: ab-low +97.2%, ab-high +182.1%.

## M01 City A/B/A

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.067 | 0.068 | 0.069 | 0.306 | 4.261 | 223.73 |
| 50 | 960×540 | ab-high | 0.228 | 0.235 | 0.352 | 0.407 | 4.250 | 225.93 |
| 50 | 1920×1080 | ab-low | 0.109 | 0.122 | 0.125 | 0.320 | 4.243 | 225.54 |
| 50 | 1920×1080 | ab-high | 0.679 | 0.685 | 0.883 | 0.418 | 4.294 | 224.71 |
| 100 | 960×540 | ab-low | 0.068 | 0.069 | 0.071 | 0.326 | 4.247 | 225.84 |
| 100 | 960×540 | ab-high | 0.233 | 0.241 | 0.366 | 0.429 | 4.251 | 225.41 |
| 100 | 1920×1080 | ab-low | 0.110 | 0.124 | 0.126 | 0.330 | 4.281 | 223.48 |
| 100 | 1920×1080 | ab-high | 0.685 | 0.691 | 0.890 | 0.444 | 4.247 | 226.89 |

Deltas high vs low (GPU p95):

- 50 proxies / 960×540: **+245.6%**.
- 50 proxies / 1920×1080: **+461.5%**.
- 100 proxies / 960×540: **+249.3%**.
- 100 proxies / 1920×1080: **+457.3%**.

Escala 960×540 → 1920×1080 (GPU p95):

- 50 proxies: ab-low +79.4%, ab-high +191.5%.
- 100 proxies: ab-low +79.7%, ab-high +186.7%.

## Observações

- The arena pattern repeats in both scenes: resolution dominates GPU cost and the high preset's relative cost grows with resolution.
- Corridor GPU p95 high vs low: +294.4% at 50/960x540 and +476.5% at 50/1920x1080.
- City GPU p95 high vs low: +245.6% at 50/960x540 and +461.5% at 50/1920x1080.
- Proxy scaling 50 to 100 changes GPU p95 by 0.0-2.9%; resolution scaling 960 to 1920 changes it by 79.4-97.2% (ab-low) and 180.0-191.5% (ab-high).
- Pacing remains near 4.25 ms and 1% low deltas are within -0.4% to +1.5%; no gain is claimed.

## Limitações

- single session on one RTX 5050; no cross-device or cross-session generalization
- two scenes only; arena_combat is covered by a separate report
- two proxy counts and two resolutions; 200 proxies and 2560x1440 are not covered
- native resolution disables the project's canvas_items stretch mode
- max_fps 240 and vsync disabled; frame pacing is capped
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_cross_scene.py`; não é benchmark nem claim de ganho.

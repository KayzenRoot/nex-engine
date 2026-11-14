# NEX M09 · Preset scaling 25/100/200 — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling` · **Source SHA:** `4e4719ac504ddb0ea7961d5c9d557c745f216990`
**Hardware:** NVIDIA GeForce RTX 5050 · Vulkan 1.4.351 · 4.7.2-stable
**Viewport:** 1280×720 · vsync 0 · max_fps 240

## Células (medianas de 3 runs)

| Count | Preset | GPU p95 | CPU p95 | Pacing p95 | 1% low | GPU spread |
|---:|---|---:|---:|---:|---:|---:|
| 25 | ab-low | 0.128 | 0.298 | 4.249 | 224.69 | 0.8% |
| 25 | ab-high | 0.774 | 0.382 | 4.269 | 222.33 | 1.4% |
| 100 | ab-low | 0.139 | 0.310 | 4.264 | 223.63 | 1.4% |
| 100 | ab-high | 0.833 | 0.444 | 4.274 | 221.84 | 1.4% |
| 200 | ab-low | 0.152 | 0.374 | 4.274 | 218.93 | 2.0% |
| 200 | ab-high | 0.879 | 0.457 | 4.256 | 222.93 | 0.3% |

## Deltas high vs low

- 25 proxies: GPU p95 **+504.7%**, CPU p95 +28.2%, pacing +0.5%, 1% low -1.1%.
- 100 proxies: GPU p95 **+499.3%**, CPU p95 +43.2%, pacing +0.2%, 1% low -0.8%.
- 200 proxies: GPU p95 **+478.3%**, CPU p95 +22.2%, pacing -0.4%, 1% low +1.8%.

## Escala 25→200

- ab-low GPU p95: +18.7%.
- ab-high GPU p95: +13.6%.

## Observações

- GPU p95 high vs low: 25 proxies +504.7%, 100 proxies +499.3%, 200 proxies +478.3%.
- GPU p95 scaling 25→200: ab-low +18.7%, ab-high +13.6%.
- Pacing remains ~4.267 ms across all cells (240 fps cap).
- One 200/low run has an isolated 1% low outlier (157.39); medians are used.
- These are measured GPU costs on a synthetic workload, not game FPS, quality or universal recommendations.

## Limitações

- single session; 3 runs per preset per proxy count
- synthetic scene at 1280x720; no cross-scene generalization
- max_fps 240 and vsync disabled; frame pacing is capped
- one isolated 1% low outlier in the 200/low cell; medians reported
- renderer allocation bytes are session history, not device VRAM
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_scaling.py`; não é benchmark nem claim de ganho.

# NEX M09 · M01 scene A/B/A — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab` · **Source SHA:** `617db53d6752f30584b296f133e6990ca6602549`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1280×720 · vsync 0 · max_fps 240
**Workload:** 100 meshes per scene · effect_mode lights

## Medianas por cena (3 runs por preset)

| Cena | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | Alloc MiB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| corridor_static | ab-low | 0.083 | 0.088 | 0.215 | 0.347 | 4.208 | 229.24 | 22.3 |
| corridor_static | ab-high | 0.416 | 0.423 | 0.571 | 0.452 | 4.218 | 226.99 | 171.9 |
| arena_combat | ab-low | 0.103 | 0.109 | 0.246 | 0.345 | 4.218 | 228.03 | 22.4 |
| arena_combat | ab-high | 0.455 | 0.462 | 0.614 | 0.435 | 4.231 | 225.66 | 173.4 |
| dense_city | ab-low | 0.079 | 0.084 | 0.213 | 0.325 | 4.284 | 222.32 | 22.3 |
| dense_city | ab-high | 0.358 | 0.362 | 0.505 | 0.432 | 4.270 | 223.25 | 167.7 |

## Deltas ab-high vs ab-low (medianas)

| Cena | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---|---:|---:|---:|---:|---:|---:|
| corridor_static | +401.2% | +380.7% | +165.6% | +30.3% | +0.2% | -1.0% |
| arena_combat | +341.7% | +323.9% | +149.6% | +26.1% | +0.3% | -1.0% |
| dense_city | +353.2% | +331.0% | +137.1% | +32.9% | -0.3% | +0.4% |

## A/A stability (3 ab-low runs)

| Cena | GPU p95 spread | 1% low spread |
|---|---:|---:|
| corridor_static | 3.4% | 1.7% |
| arena_combat | 7.3% | 2.7% |
| dense_city | 1.2% | 2.2% |

## Observações

- ab-high GPU p95 is higher in every scene: corridor +380.7%, arena +323.9%, city +331.0%.
- Absolute GPU p95 medians stay below 0.5 ms because 100 meshes are a light workload for this GPU.
- Pacing stays near 4.2 ms (240 fps cap); 1% low deltas range from -1.0% to +0.4% and are not a gain claim.
- Corridor ab-high has a first-run p95 outlier (0.542 ms vs 0.421/0.423 ms); the median is reported.
- These are measured GPU costs for three specific M01 compositions, not game FPS, quality or universal recommendations.

## Limitações

- single session; 3 runs per preset per scene
- three specific M01 compositions at 100 meshes; fillers may overlap base-scene props
- max_fps 240 and vsync disabled; frame pacing is capped
- corridor ab-high first-run p95 outlier is documented and retained
- renderer allocation bytes are session history, not device VRAM
- GPU render timing can describe earlier work and is not input-to-photon
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_m01_ab.py`; não é benchmark nem claim de ganho.

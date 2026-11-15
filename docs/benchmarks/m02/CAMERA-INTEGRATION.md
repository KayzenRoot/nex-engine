# NEX M02-S01 · Camera integration — RTX 5050

**Status:** `CAMERA_RIG_REPRODUCES_BASELINE_FRAMING / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte visual:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-camera-visual`
**Fonte performance:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-camera-perf`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable

## Visual A/B/A

| Cena | A/A idêntico | Mean abs | Pixels alterados | PSNR | Max abs |
|---|---|---:|---:|---:|---:|
| corridor_static | sim | 0.0020 | 0.013% | 59.66 dB | 141 |
| arena_combat | sim | 0.0003 | 0.003% | 71.95 dB | 34 |
| dense_city | sim | 0.0000 | 0.000% | 106.53 dB | 1 |

## Performance A/B/A (medianas de 3 runs)

| Cena | GPU p95 baseline | GPU p95 rig | Δ GPU | CPU p95 baseline | CPU p95 rig | Δ CPU |
|---|---:|---:|---:|---:|---:|---:|
| corridor_static | 0.094 | 0.094 | +0.00% | 0.366 | 0.366 | +0.00% |
| arena_combat | 0.106 | 0.107 | +0.94% | 0.361 | 0.409 | +13.30% |
| dense_city | 0.080 | 0.081 | +1.25% | 0.309 | 0.349 | +12.94% |

## Observações

- all three repetitions of each camera mode are byte-identical
- the rig reproduces the baseline framing with negligible pixel difference: 0.000% (city), 0.003% (arena) and 0.013% (corridor) of changed pixels
- GPU p95 is effectively unchanged (0.0% to +1.25%); CPU p95 is unchanged in corridor and +12.9%/+13.3% in arena/city with small absolute values
- this is a scene and performance comparison for one preset, not a quality or FPS claim

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- one preset (ab-low), static frame and one camera pose per scene
- CPU p95 deltas are small in absolute terms and not proven to be causal
- no animation, camera motion, gameplay or production-scene validation
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m02/tools/build_camera_integration.py`; não é benchmark nem claim de qualidade.

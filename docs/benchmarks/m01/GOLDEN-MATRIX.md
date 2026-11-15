# NEX M01 · Golden matrix and S01 acceptance

**Status:** `GOLDEN_MATRIX_DERIVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-golden` · **Source SHA:** `900d2b2d031a87048702625a1e98bc50905bc663`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1920×1080 · threshold 2

| Cena | Seed | A/A idêntico | A/B mean abs | A/B pixels | A/B PSNR | Imagem de aceitação |
|---|---:|---|---:|---:|---:|---|
| corridor_static | 4101 | sim | 0.4168 | 3.367% | 38.485 dB | `corridor_static_ab-low_1.png` |
| arena_combat | 4102 | sim | 0.4215 | 3.354% | 36.851 dB | `arena_combat_ab-low_1.png` |
| dense_city | 4103 | sim | 0.1785 | 1.276% | 40.464 dB | `dense_city_ab-low_1.png` |

## Regiões (ab-low vs ab-high)

| Cena | Região | Mean abs | Pixels alterados | PSNR |
|---|---|---:|---:|---:|
| corridor_static | full | 0.4168 | 3.367% | 38.485 dB |
| corridor_static | center_gameplay | 0.9732 | 7.845% | 34.782 dB |
| corridor_static | top_band | 0.0260 | 0.275% | 53.130 dB |
| corridor_static | bottom_band | 0.0000 | 0.000% | ∞ |
| corridor_static | left_band | 0.0208 | 0.154% | 51.672 dB |
| corridor_static | right_band | 0.0000 | 0.000% | ∞ |
| arena_combat | full | 0.4215 | 3.354% | 36.851 dB |
| arena_combat | center_gameplay | 1.0036 | 7.986% | 33.083 dB |
| arena_combat | top_band | 0.0000 | 0.000% | ∞ |
| arena_combat | bottom_band | 0.0000 | 0.000% | ∞ |
| arena_combat | left_band | 0.0000 | 0.000% | ∞ |
| arena_combat | right_band | 0.0000 | 0.000% | ∞ |
| dense_city | full | 0.1785 | 1.276% | 40.464 dB |
| dense_city | center_gameplay | 0.4251 | 3.038% | 36.697 dB |
| dense_city | top_band | 0.0000 | 0.000% | ∞ |
| dense_city | bottom_band | 0.0000 | 0.000% | ∞ |
| dense_city | left_band | 0.0000 | 0.000% | ∞ |
| dense_city | right_band | 0.0000 | 0.000% | ∞ |

## Observações

- all 18 captures are 1920x1080 native Forward+/Vulkan on the RTX 5050
- all three repetitions per scene/preset are byte-identical
- the ab-low vs ab-high comparison is the only lighting/preset difference
- S01 acceptance images are the ab-low first repetitions per scene
- no third-party asset is referenced by the three base scenes

## Limitações

- single session, one GPU and driver; static frame
- PNG comparison is a regression signal, not an artistic quality metric
- fillers may overlap base-scene props
- no FPS, game-performance or cross-device generalization claim

Gerado por `docs/benchmarks/m01/tools/build_golden_matrix.py`; não é benchmark de hardware.

# NEX M09 · M01 visual truth at 1920×1080 — RTX 5050

**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-1920` · **Harness SHA:** `06eb6d92da50bdb8105bbc8f7b6bed98faebb329`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1920×1080 · threshold de pixel alterado: 2

## Comparações por cena

| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR | Δ mean abs vs 1280 |
|---|---|---:|---:|---:|---:|---:|---:|
| corridor_static | sim | 0.0000 | 0.4168 | 167 | 3.367% | 38.485 dB | -18.8% |
| arena_combat | sim | 0.0000 | 0.4215 | 189 | 3.354% | 36.851 dB | -13.9% |
| dense_city | sim | 0.0000 | 0.1785 | 146 | 1.276% | 40.464 dB | -23.0% |

## Observações

- A/A is exact: all three repetitions of each scene/preset pair share one SHA-256.
- ab-high changes the image in every scene at 1920x1080; changed pixels are 3.367% (corridor), 3.354% (arena) and 1.276% (city).
- The A/B mean absolute difference is slightly lower at 1920x1080 than at 1280x720 in all three scenes.
- The direction is consistent across resolutions: the high preset changes the image, and city has the smallest difference.
- This is a pixel-difference observation, not a quality ranking or a universal recommendation.

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- static frame only; animation, temporal effects and camera motion are not covered
- fillers may overlap base-scene props; this is a stress composition, not a beauty shot
- PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_m01_visual_1920.py`; não é benchmark nem claim de qualidade.

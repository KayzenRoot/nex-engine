# NEX M09 · M01 visual truth at 2560×1440 — RTX 5050

**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-2560` · **Harness SHA:** `4f739cd6808677cd7e3780a8bedb295da55e046d`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 2560×1440 · threshold de pixel alterado: 2

## Comparações por cena

| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR | Δ mean abs vs 1920 |
|---|---|---:|---:|---:|---:|---:|---:|
| corridor_static | sim | 0.0000 | 0.3694 | 168 | 2.996% | 39.085 dB | -11.4% |
| arena_combat | sim | 0.0000 | 0.3863 | 190 | 3.074% | 37.136 dB | -8.4% |
| dense_city | sim | 0.0000 | 0.1524 | 123 | 1.031% | 40.790 dB | -14.6% |

## Observações

- A/A is exact: all three repetitions of each scene/preset pair share one SHA-256.
- ab-high changes the image in every scene at 2560x1440; changed pixels are 2.996% (corridor), 3.074% (arena) and 1.031% (city).
- The A/B mean absolute difference is slightly lower at 2560x1440 than at 1920x1080 in all three scenes.
- The direction is consistent across resolutions: the high preset changes the image, and city has the smallest difference.
- This is a pixel-difference observation, not a quality ranking or a universal recommendation.

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- static frame only; animation, temporal effects and camera motion are not covered
- fillers may overlap base-scene props; this is a stress composition, not a beauty shot
- PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces
- the harness applies a subset of preset_pack.v1 settings
- the 2560x1440 window is taller than the 2560x1080 desktop; the viewport is captured off-screen
- one initial corridor/high capture was clipped to 2560x1009 and re-captured; the committed image is 2560x1440
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_m01_visual_2560.py`; não é benchmark nem claim de qualidade.

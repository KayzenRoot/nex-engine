# NEX M09 · M01 visual truth — RTX 5050

**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual` · **Harness SHA:** `952b5a63bc1696cadf7436a061a7d996c80fa220`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1280×720 · threshold de pixel alterado: 2

## Comparações por cena

| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR |
|---|---|---:|---:|---:|---:|---:|
| corridor_static | sim | 0.0000 | 0.5135 | 170 | 4.077% | 37.406 dB |
| arena_combat | sim | 0.0000 | 0.4898 | 187 | 3.884% | 36.386 dB |
| dense_city | sim | 0.0000 | 0.2317 | 133 | 1.745% | 39.763 dB |

## Observações

- A/A is exact: all three repetitions of each scene/preset pair share one SHA-256, so every A/A pixel difference is zero.
- ab-high changes the image in every scene: corridor 4.077% changed pixels, arena 3.884%, city 1.745% at threshold 2.
- The matched A/B pairs are identical within each scene because the repetitions are byte-identical; medians are reported.
- City has the smallest changed-pixel fraction; corridor has the largest at this fixed camera and 100-mesh composition.
- The difference confirms a rendering-state change, not a visual-quality ranking or a universal recommendation.

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- static frame only; animation, temporal effects and camera motion are not covered
- fillers may overlap base-scene props; this is a stress composition, not a beauty shot
- PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_m01_visual.py`; não é benchmark nem claim de qualidade.

# NEX M09 · Camera-motion sequence — RTX 5050

**Status:** `CAMERA_MOTION_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-camera-motion` · **Harness SHA:** `a6ce04bf74e7dee5712738a213704aab8068132b`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1280×720 · **Motion:** orbit 3.0°/frame

## Comparações por célula

| Cena | Preset | Frames | Mean abs médio | Changed pixels máx | PSNR mín |
|---|---|---:|---:|---:|---:|
| corridor_static | ab-low | 5 | 5.0913 | 19.766% | 21.734 dB |
| corridor_static | ab-high | 5 | 5.1619 | 19.168% | 21.428 dB |
| arena_combat | ab-low | 5 | 2.1781 | 8.534% | 25.912 dB |
| arena_combat | ab-high | 5 | 2.2321 | 8.088% | 25.728 dB |
| dense_city | ab-low | 5 | 1.7989 | 7.051% | 27.127 dB |
| dense_city | ab-high | 5 | 1.8396 | 6.477% | 26.768 dB |

## Observações

- all 30 frames were captured with a deterministic 3-degree orbit step between frames; every consecutive pair differs
- the mean absolute difference grows with frame index: 2.864 -> 7.184 in the first cell
- changed pixels range from 3.132% to 19.766% across all pairs
- this is a harness capability observation for camera motion, not a quality, stability or performance claim
- static temporal stability remains covered by the separate temporal-stability bundle

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- discrete 3-degree camera steps between captured frames; not continuous animation
- static scene content; animation, VFX, physics and gameplay motion are not covered
- the comparison is exact RGB byte comparison; it does not model human perception or color spaces
- no FPS, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_camera_motion.py`; não é benchmark nem claim de qualidade.

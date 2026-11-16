# NEX M08 · 2.5D hybrid runtime

**Status:** `M08_RENDER25D_REFERENCE_DERIVED / NATIVE_2.5D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `2c7dd515e307086cdd7180577b0c78ad7fb5cf1c` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · CompositionPlanner

- **COMPOSITION_PLANNER_VERIFIED**: 69 checks headless.

## S02 · Câmera, sprites e sorting

| Modo | GPU p95 | CPU p95 | GPU vs base | Pixels | PSNR |
|---|---:|---:|---:|---:|---:|
| baseline | 0.390 ms | 0.247 ms | +0.00% | 0.000% | — |
| sprites | 0.400 ms | 0.375 ms | +2.56% | 6.463% | 19.68 dB |
| sorted | 0.401 ms | 0.349 ms | +2.82% | 6.463% | 19.68 dB |
| shadows | 0.498 ms | 0.525 ms | +27.69% | 15.477% | 18.00 dB |
| overlay | 0.411 ms | 0.381 ms | +5.38% | 22.789% | 18.18 dB |
| hybrid | 0.508 ms | 0.550 ms | +30.26% | 31.714% | 16.97 dB |
| perspective | 0.332 ms | 0.364 ms | -14.87% | 34.442% | 16.18 dB |
| quality_low | 0.397 ms | 0.302 ms | +1.79% | 3.347% | 22.58 dB |
| quality_high | 0.497 ms | 0.675 ms | +27.44% | 37.775% | 15.52 dB |

## S03 · Shadows

- Shadows vs baseline: **15.477%** de pixels; GPU **0.498 ms** (+27.69%).

## S04 · Overlay 2D

- Overlay vs baseline: **22.789%** de pixels; GPU **0.411 ms** (+5.38%).

## S05 · Hybrid

- Hybrid vs baseline: **31.714%** de pixels; GPU **0.508 ms** (+30.26%).

## S06 · Câmera ortho vs perspective

- Orthographic **0.390 ms** → perspective **0.332 ms** (-14.87%); 34.442% de pixels.

## S07 · Quality profiles

| Perfil | GPU p95 | GPU vs base | Pixels |
|---|---:|---:|---:|
| quality_low | 0.397 ms | +1.79% | 3.347% |
| quality_high | 0.497 ms | +27.44% | 37.775% |

## S08 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| CompositionPlanner / composition.v1 | **GO** | 69 headless checks; planning only |
| Orthographic hybrid camera | **GO_WITH_LIMITATIONS** | baseline GPU p95 0.390 ms in the 2.5D lab |
| Sprite3D billboards | **GO_WITH_LIMITATIONS** | 40 sprites add +2.56% GPU and change 6.463% of the frame |
| Custom depth sorting | **NO_GO** | sorted vs sprites change 0.000% of pixels; native sorting is sufficient |
| 3D shadow casting | **GO_WITH_LIMITATIONS** | shadows add +27.69% GPU and change 15.477% of the frame |
| CanvasLayer overlay | **GO_WITH_LIMITATIONS** | overlay adds +5.38% GPU and changes 22.789% of the frame |
| Hybrid 2.5D composition | **GO_WITH_LIMITATIONS** | hybrid adds +30.26% GPU and changes 31.714% of the frame |
| Perspective camera mode | **GO_WITH_LIMITATIONS** | perspective GPU 0.332 ms (-14.87% vs ortho) with different framing |
| 2.5D quality profiles | **GO_WITH_LIMITATIONS** | low/high GPU 0.397/0.497 ms in one hybrid lab |

- 9 runs, 9 imagens, 69 checks de planner, 0 assets de terceiros.

## Observações

- 9 native 2.5D runs and 9 captures cover orthographic/perspective cameras, sprites, sorting, shadows, overlay, hybrid and quality profiles
- baseline GPU p95 is 0.390 ms; sprites 0.400 ms; sorted 0.401 ms; shadows 0.498 ms; overlay 0.411 ms; hybrid 0.508 ms
- perspective camera is 0.332 ms with 34.442% different pixels versus orthographic
- sorted vs sprites changes 0.000% of pixels; native transparent sorting is sufficient
- shadows add +27.69% GPU and change 15.477% of the frame
- overlay adds +5.38% GPU and changes 22.789% of the frame
- hybrid adds +30.26% GPU and changes 31.714% of the frame
- CompositionPlanner still passes 69 headless checks

## Limitações

- single session, one GPU and driver; 1920x1080 static 2.5D lab
- no production 2.5D renderer, viewport stacking or art-directed layer stack
- depth sorting is native Sprite3D transparency sorting, not a custom sorter
- no input-to-photon, VRAM pressure or cross-device claim
- no production art, no PoE2 parity and no generalized FPS claim

Gerado por `docs/benchmarks/m08/tools/build_m08_runtime.py`; não é paridade com PoE2.

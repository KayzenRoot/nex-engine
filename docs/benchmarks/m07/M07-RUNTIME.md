# NEX M07 · Render2D runtime

**Status:** `M07_RENDER2D_REFERENCE_DERIVED / NATIVE_2D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `aa6256a82f6cd34e347b05ac43375ac4042d2ede` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · CanvasPlanner

- **CANVAS_PLANNER_VERIFIED**: 46 checks headless.

## S02 · 2D lighting

| Modo | GPU p95 | CPU p95 | GPU vs base | Pixels | PSNR |
|---|---:|---:|---:|---:|---:|
| baseline | 0.060 ms | 0.128 ms | +0.00% | 0.000% | — |
| lighting | 0.075 ms | 0.139 ms | +25.00% | 16.218% | 21.55 dB |
| shadows | 0.100 ms | 0.176 ms | +66.67% | 16.223% | 17.79 dB |
| normal | 0.082 ms | 0.138 ms | +36.67% | 16.223% | 16.68 dB |
| particles | 0.071 ms | 0.145 ms | +18.33% | 0.979% | 28.26 dB |
| parallax | 0.070 ms | 0.142 ms | +16.67% | 23.006% | 30.66 dB |
| quality_low | 0.065 ms | 0.187 ms | +8.33% | 16.223% | 16.67 dB |
| quality_medium | 0.081 ms | 0.184 ms | +35.00% | 39.224% | 17.46 dB |
| quality_high | 0.153 ms | 0.219 ms | +155.00% | 39.691% | 15.80 dB |

## S03 · Shadows

- Shadows vs lighting: **9.028%** de pixels, PSNR 20.18 dB.
- GPU p95: lighting **0.075 ms** → shadows **0.100 ms**.

## S04 · Normal maps

- Normal vs lighting: **14.542%** de pixels, PSNR 18.36 dB.
- GPU p95: lighting **0.075 ms** → normal **0.082 ms**.

## S05 · Particles

- 384 particles: GPU **0.071 ms** (+18.33% vs baseline); pixels **0.979%**.

## S06 · Parallax

- 3 layers: GPU **0.070 ms** (+16.67% vs baseline); pixels **23.006%**.

## S07 · Quality profiles

| Perfil | GPU p95 | GPU vs base | Pixels |
|---|---:|---:|---:|
| quality_low | 0.065 ms | +8.33% | 16.223% |
| quality_medium | 0.081 ms | +35.00% | 39.224% |
| quality_high | 0.153 ms | +155.00% | 39.691% |

## S08 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| CanvasPlanner / render2d.v1 | **GO** | 46 headless checks; planning only, no rendering |
| 2D lighting / CanvasModulate | **GO_WITH_LIMITATIONS** | 4 PointLight2D change 16.218% of the frame at +25.0% GPU p95 |
| 2D shadows / LightOccluder2D | **GO_WITH_LIMITATIONS** | shadows add +33.3% GPU over lighting and 9.028% pixel change |
| Normal maps / CanvasTexture | **GO_WITH_LIMITATIONS** | normal maps add +9.3% GPU over lighting and 14.542% pixel change |
| GPUParticles2D | **GO_WITH_LIMITATIONS** | 384 particles add +18.3% GPU over baseline and 0.979% pixel change |
| ParallaxBackground | **GO** | 3 layers change 23.006% of the frame at +16.7% GPU p95 |
| 2D quality profiles | **GO_WITH_LIMITATIONS** | low/medium/high GPU 0.065/0.081/0.153 ms in one 100-sprite lab |

- 9 runs, 9 imagens, 46 checks de planner, 0 assets de terceiros.

## Observações

- 9 native 2D runs and 9 captures cover lighting, shadows, normal maps, particles, parallax and quality profiles
- baseline GPU p95 is 0.060 ms; quality_high is 0.153 ms in the 100-sprite lab
- lighting changes 16.218% of the frame at +25.0% GPU p95 versus baseline
- shadows add +33.3% GPU over lighting and 9.028% pixel change
- normal maps add +9.3% GPU over lighting and 14.542% pixel change
- 384 particles add +18.3% GPU over baseline and 0.979% pixel change
- parallax changes 23.006% of the frame at +16.7% GPU p95
- CanvasPlanner still passes 46 headless checks

## Limitações

- single session, one GPU and driver; 1920x1080 static 2D lab
- no production 2D renderer, atlas packing, y-sort or transparency rasterization
- no input-to-photon, VRAM pressure or cross-device claim
- lighting/shadows/normal maps are native Godot features, not a custom renderer
- no production art, no PoE2 parity and no generalized FPS claim

Gerado por `docs/benchmarks/m07/tools/build_m07_runtime.py`; não é paridade com PoE2.

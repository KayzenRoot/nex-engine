# NEX M10 · Animation and combat feedback

**Status:** `M10_ANIMATION_REFERENCE_DERIVED / NATIVE_ANIMATION_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `818759d5e6daaa3d3f9be922331b0d39d5cd4f5c` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · FeedbackPlanner

- **FEEDBACK_PLANNER_VERIFIED**: 66 checks headless.

## S02 · Animation blending

| Modo | GPU p95 | CPU p95 | GPU vs base | Pixels | PSNR |
|---|---:|---:|---:|---:|---:|
| baseline | 0.256 ms | 0.273 ms | +0.00% | 0.000% | — |
| blend | 0.264 ms | 0.177 ms | +3.13% | 0.493% | 30.25 dB |
| attack | 0.256 ms | 0.292 ms | +0.00% | 0.931% | 27.46 dB |
| hit | 0.256 ms | 0.275 ms | +0.00% | 0.414% | 31.05 dB |
| hitstop | 0.255 ms | 0.287 ms | -0.39% | 0.931% | 27.46 dB |
| camera | 0.273 ms | 0.275 ms | +6.64% | 2.661% | 25.74 dB |
| vfx | 0.262 ms | 0.278 ms | +2.34% | 3.681% | 23.18 dB |
| quality_low | 0.264 ms | 0.213 ms | +3.13% | 0.008% | 48.16 dB |
| quality_high | 0.274 ms | 0.205 ms | +7.03% | 7.934% | 21.39 dB |

## S03 · Hit reaction

- Hit vs baseline: **0.414%** de pixels; GPU **0.256 ms**.

## S04 · Visual hit-stop

- Hit-stop vs attack: **0.000%** de pixels; GPU **0.255 ms** vs attack **0.256 ms**.
- O hit-stop é apenas visual; nenhuma autoridade de dano, física ou rede é alterada.

## S05 · Smooth camera

- Camera vs baseline: **2.661%** de pixels; GPU **0.273 ms** (+6.64%).

## S06 · M05 VFX synchronization

- VFX vs baseline: **3.681%** de pixels; GPU **0.262 ms** (+2.34%).

## S07 · Quality profiles

| Perfil | GPU p95 | GPU vs base | Pixels |
|---|---:|---:|---:|
| quality_low | 0.264 ms | +3.13% | 0.008% |
| quality_high | 0.274 ms | +7.03% | 7.934% |

## S08 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| FeedbackPlanner / feedback.v1 | **GO** | 66 headless checks; planning only |
| AnimationTree blending | **GO_WITH_LIMITATIONS** | blend 0.5 changes 0.493% of the frame at +3.13% GPU |
| Hit reaction | **GO_WITH_LIMITATIONS** | hit changes 0.414% of the frame; GPU neutral in the lab |
| Visual hit-stop | **GO_WITH_LIMITATIONS** | hit-stop changes 0.000% of the attack pose; timing/pacing only |
| Smooth camera | **GO_WITH_LIMITATIONS** | camera mode adds +6.64% GPU and changes 2.661% of the frame |
| M05 VFX synchronization | **GO_WITH_LIMITATIONS** | impact changes 3.681% of the frame; SpellFX event accepted |
| Animation quality profiles | **GO_WITH_LIMITATIONS** | low/high GPU 0.264/0.274 ms in one animation lab |

- 9 runs, 9 imagens, 66 checks de planner, 0 assets de terceiros.

## Observações

- 9 native animation runs and 9 captures cover idle, blend, attack, hit, hit-stop, camera, VFX and quality profiles
- baseline GPU p95 is 0.256 ms; blend 0.264 ms; attack 0.256 ms; hit 0.256 ms; camera 0.273 ms; vfx 0.262 ms
- blend 0.5 changes 0.493% of the frame; attack changes 0.931%; hit changes 0.414%
- visual hit-stop changes 0.000% of the attack pose; it is a timing/pacing experiment
- camera mode adds +6.64% GPU and changes 2.661% of the frame
- M05 impact changes 3.681% of the frame and the SpellFX event is accepted
- quality low/high GPU p95 is 0.264/0.274 ms
- FeedbackPlanner still passes 66 headless checks

## Limitações

- single session, one GPU and driver; 1920x1080 static animation lab
- the rig is a two-bone proxy, not a production character or skin
- hit-stop is visual only; no damage, physics or netcode authority
- no input-to-photon, VRAM pressure or cross-device claim
- no production art, no PoE2 parity and no generalized FPS claim

Gerado por `docs/benchmarks/m10/tools/build_m10_runtime.py`; não é paridade com PoE2.

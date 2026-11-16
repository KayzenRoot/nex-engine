# NEX M05 · VFX runtime

**Status:** `M05_VFX_REFERENCE_DERIVED / NATIVE_CAPTURES / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `dd840f86023057a4dc8af92148cdf36911175613` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · SpellFX

- Contrato `spellfx.v1`: **12 checks**, falhas `[]`.
- Budgets: `max_active=128`, `max_per_vfx=64`; tiers low, medium, high.
- Captura: 6 eventos, 6 luzes aceitas.
- Autoridade: data-only; damage and hit detection remain gameplay-owned.

## S02 · Biblioteca elemental

| Elemento | Partículas | Meshes | Diferença mediana | Máximo |
|---|---:|---:|---:|---:|
| fire | 64 | 0 | 4.269% | 6.856% |
| frost | 48 | 0 | 4.754% | 7.081% |
| lightning | 40 | 1 | 5.254% | 36.666% |
| smoke | 32 | 0 | 1.000% | 3.873% |
| impact | 40 | 0 | 4.717% | 6.661% |
| projectile | 24 | 2 | 7.065% | 20.678% |

| Cena | Elemento | Pixels alterados | Mean abs | PSNR | PNG |
|---|---|---:|---:|---:|---:|
| corridor_static | fire | 6.856% | 1.6945 | 24.86 dB | 472743 B |
| corridor_static | frost | 7.081% | 2.4527 | 23.46 dB | 505198 B |
| corridor_static | lightning | 36.666% | 4.6082 | 23.10 dB | 518990 B |
| corridor_static | smoke | 3.873% | 0.6734 | 33.45 dB | 455078 B |
| corridor_static | impact | 6.661% | 1.7092 | 26.11 dB | 483152 B |
| corridor_static | projectile | 20.678% | 2.5464 | 26.54 dB | 478972 B |
| arena_combat | fire | 4.269% | 1.3111 | 25.52 dB | 725564 B |
| arena_combat | frost | 4.754% | 1.6057 | 25.10 dB | 747538 B |
| arena_combat | lightning | 5.254% | 1.3901 | 26.22 dB | 731016 B |
| arena_combat | smoke | 1.000% | 0.2933 | 36.09 dB | 703337 B |
| arena_combat | impact | 4.717% | 0.8745 | 28.68 dB | 729448 B |
| arena_combat | projectile | 7.065% | 0.6685 | 30.40 dB | 712031 B |
| dense_city | fire | 3.986% | 1.1100 | 26.80 dB | 386854 B |
| dense_city | frost | 4.092% | 1.3152 | 26.21 dB | 408004 B |
| dense_city | lightning | 2.044% | 0.6637 | 29.53 dB | 374605 B |
| dense_city | smoke | 0.475% | 0.1682 | 41.07 dB | 356624 B |
| dense_city | impact | 4.079% | 0.7481 | 29.46 dB | 382235 B |
| dense_city | projectile | 6.246% | 0.4292 | 33.81 dB | 362546 B |

## S03 · Projectile/HitEcho

- Projétil: 24 partículas e 2 meshes de trilha; impacto: 40 partículas.
- Hit autoritativo, física e colisão: **não implementados**; a camada é somente visual.

## S04 · Combat clarity

- 25 eventos com 8 luzes alteram **28.055%** do frame da arena.
- Telegraphs, redução de flashes e ThreatBudget Scheduler: **não implementados**.

## S05 · FX budget e ciclo de vida

| Eventos | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | GPU vs base | 1% low vs base |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3.210 ms | — | 0.564 ms | 4.270 ms | 219.73 | — | — |
| 1 | 3.620 ms | 3.737 ms | 1.301 ms | 4.255 ms | 220.73 | +12.77% | +0.46% |
| 25 | 3.839 ms | 3.957 ms | 1.422 ms | 4.251 ms | 221.40 | +19.60% | +0.76% |
| 100 | 3.992 ms | 4.136 ms | 3.208 ms | 6.266 ms | 104.48 | +24.36% | -52.45% |

- Alocação do renderer: 781281008 B sem VFX; 1 evento 781325952 B (+44944 B); 25 eventos 783057920 B (+1776912 B); 100 eventos 789703824 B (+8422816 B).
- Pool: até 128 ativos e 64 por VFX; 12 checks de ciclo de vida.

## S06 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| GPUParticles3D elemental library | **GO** | 6 original effects rendered in 3 scenes at 1920x1080 |
| SpellFX request contract | **GO** | 12 smoke checks: idempotency, authority, budgets, cancel and expiry |
| LightBridge VFX lights | **GO** | 6 accepted lights for 6 events and 8 accepted for 25/100 events |
| PulsePool lifecycle | **GO_WITH_LIMITATIONS** | request budgets and expiry verified; no warm pool or shader prewarm |
| Projectile/HitEcho | **GO_WITH_LIMITATIONS** | visual trail and impact only; no authoritative hit or collision |
| Combat clarity / ThreatBudget | **NO_GO** | no telegraphs, flash reduction or threat scheduler implemented |
| Cinematic quality / PoE2 parity | **NO_GO** | no production art, no parity claim and no quality metric |

## S07 · QA

- 19 capturas visuais, 3 baselines, 9 runs de stress e 3 runs sem VFX.
- 3 cenas; 0 assets de terceiros.

## Observações

- 6 original elemental effects are rendered in corridor, arena and city scenes
- 25 simultaneous effects with 8 accepted lights change 28.055% of the arena frame
- 100 events keep GPU p95 at 3.992 ms and 1% low at 104.48 FPS on the reference GPU
- GPU p95 rises +12.77% / +19.60% / +24.36% for 1 / 25 / 100 events versus no VFX
- 1% low changes +0.46% / +0.76% / -52.45% for 1 / 25 / 100 events versus no VFX
- SpellFX smoke passes 12 checks and keeps gameplay authority outside the visual layer

## Limitações

- single session, one GPU and driver; static frames for the visual matrix
- no authoritative hit detection, projectile physics or GPU particle collision
- no telegraphs, flash reduction, threat scheduler or accessibility options
- no warm pool, shader prewarm, overdraw metric or VRAM budget
- no production art, no cinematic-quality metric and no PoE2 parity claim

Gerado por `docs/benchmarks/m05/tools/build_m05_runtime.py`; não é paridade com PoE2.

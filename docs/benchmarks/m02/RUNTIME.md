# NEX M02 · Runtime reference report

**Status:** `M02_RUNTIME_REFERENCE_DERIVED / NATIVE_GPU / NO_GENERAL_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `fa1adae7ab67e38c2556d126627006c338e2e8f4` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · câmera

- Round-trip 3D↔tela: **0.000003 m**.
- Fast follow máximo: **24.325 px** por passo.

| Aspecto | Resolução | SHA-256 |
|---|---|---|
| 16x9 | 1920×1080 | `71fd92e20d83371c…` |
| 16x10 | 1920×1200 | `23c7baca8bb90941…` |
| 21x9 | 2560×1080 | `918567d0e44c8a5e…` |
| 4x3 | 1440×1080 | `f9fda0dc5e2598da…` |

## S02 · sightline

| Cena | Reveals hidden→revealed | Pixels alterados | GPU p95 | Δ vs M01 |
|---|---|---:|---:|---:|
| corridor_static | 0→1 | 1.141% | 0.151 ms | +8.6% |
| arena_combat | 0→1 | 0.456% | 0.160 ms | +6.0% |
| dense_city | 0→1 | 0.123% | 0.132 ms | +8.2% |

## S03 · depth overlay

| Cena | Pixels alterados | Z-fight | Alpha crítico | Overlay/gameplay | GPU p95 | Δ vs M01 |
|---|---:|---:|---:|---:|---:|---:|
| corridor_static | 0.370% | 0 | 0 | 0 | 0.141 ms | +1.4% |
| arena_combat | 0.556% | 0 | 0 | 0 | 0.151 ms | +0.0% |
| dense_city | 0.741% | 0 | 0 | 0 | 0.126 ms | +3.3% |

## S04 · temporal TAA

- Off: `DEFECT_REPRODUCED` / `NO_GO`; ghosting 0.000, flicker 0.667, shimmer 0.050.
- On: `DEFECT_REPRODUCED` / `NO_GO`; ghosting 0.000, flicker 0.667, shimmer 0.053.
- First-frame A/B: 2.621% pixels, mean abs 0.2121.
- **Veredito:** `NO_GO_CUSTOM_COMPOSITOR` — TAA nativo disponível; nenhum compositor customizado justificado.

## S05 · perfis

| Perfil | Render scale | MSAA | GPU p95 | CPU p95 | 1% low | Alloc MiB |
|---|---:|---|---:|---:|---:|---:|
| quality | 1.00 | 2 | 0.758 ms | 0.486 ms | 226.50 | 209.6 |
| balanced | 0.85 | 1 | 0.571 ms | 0.441 ms | 225.16 | 124.6 |
| performance | 0.70 | 0 | 0.182 ms | 0.374 ms | 226.38 | 45.2 |

## S06 · decisões R&D

| Tecnologia | Nativo | Decisão | Evidência |
|---|---|---|---|
| NEX IsoDirector | Camera3D perspective/orthographic | **GO** | round trip 3e-6 m, 4 aspect captures, A/B framing reproduced |
| Sightline | occlusion query / material fade | **GO** | reveal rendered in 3 scenes, no critical unseen, GPU delta small |
| DepthWeave | transparent sorting / depth prepass | **GO** | overlay pass with 0 z-fight/alpha/overlay conflicts, GPU delta small |
| TemporalGuard | native TAA | **NO_GO_CUSTOM_COMPOSITOR** | native TAA available; off/on analyzer metrics identical, no benefit proven |
| RenderPassport | documented capability matrix | **GO** | runtime probe on Forward+/Vulkan, three profiles OK, switch reversible |

## Observações

- camera round-trip error is 3e-6 m and fast follow stays under 25 px per step
- sightline reveal is visible in all three scenes with 0 critical unseen
- depth overlay plan reports 0 z-fight, alpha-over-critical and overlay/gameplay conflicts
- native TAA changes the first frame but the region analyzer is identical off/on
- profile cost ordering is quality > balanced > performance in GPU p95 and allocation

## Limitações

- single session, one GPU and driver; static frames for S01/S02/S03/S05
- the temporal analyzer uses 4x4 luminance regions, not per-pixel TAA metrics
- the depth overlay is a deterministic test quad, not production art
- no game, gameplay, M03-M12 renderer or cross-device claim

Gerado por `docs/benchmarks/m02/tools/build_m02_runtime.py`; não é benchmark de jogo.

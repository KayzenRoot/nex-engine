# NEX M09 · M01 temporal stability — RTX 5050

**Status:** `TEMPORAL_STABILITY_OBSERVED / SINGLE_SESSION / STATIC_WORKLOAD / NO_QUALITY_CLAIM`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-temporal` · **Harness SHA:** `22f428aebf43da39750adb6a8c919d0b2721d9a1`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1280×720 · 5 frames por célula · intervalo de 30 frames

## Estabilidade por célula

| Cena | Preset | Frames | SHA-256 únicos | Frame-a-frame mean abs | Pixels alterados | Veredito |
|---|---|---:|---:|---:|---:|---|
| corridor_static | ab-low | 5 | 1 | 0.0000 | 0.000% | estável |
| corridor_static | ab-high | 5 | 1 | 0.0000 | 0.000% | estável |
| arena_combat | ab-low | 5 | 1 | 0.0000 | 0.000% | estável |
| arena_combat | ab-high | 5 | 1 | 0.0000 | 0.000% | estável |
| dense_city | ab-low | 5 | 1 | 0.0000 | 0.000% | estável |
| dense_city | ab-high | 5 | 1 | 0.0000 | 0.000% | estável |

## Resumo

- Células: 6 · frames: 30.
- Todas as frames idênticas: sim.
- Maior diferença frame-a-frame: 0.0000 mean abs.

## Observações

- All five frames of every scene/preset cell are byte-identical (one SHA-256 per cell).
- Every frame-to-frame pixel comparison is exactly zero in this static workload.
- The result covers repeated frames of static compositions only; animation, camera motion and dynamic effects are not covered.
- This is a temporal-stability observation, not a quality ranking or a universal guarantee.

## Limitações

- single session on one RTX 5050; no cross-device, cross-driver or cross-session generalization
- static scenes only; no animation, temporal effects or camera motion
- fillers may overlap base-scene props; this is a stress composition, not a beauty shot
- PNG comparison is exact RGB byte comparison; it does not model human perception or color spaces
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_temporal_stability.py`; não é benchmark nem claim de qualidade.

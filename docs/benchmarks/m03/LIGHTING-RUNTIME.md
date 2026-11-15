# NEX M03 · Cinematic lighting runtime

**Status:** `M03_LIGHTING_REFERENCE_DERIVED / NATIVE_GPU / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `6be39d49d8769ff46a98990c6818c8132e9e5a1d` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · CineLight looks

| Cena | Look | Pixels vs dungeon | Mean abs | GPU p95 |
|---|---|---:|---:|---:|
| corridor_static | dungeon_torch | — | — | 3.129 ms |
| corridor_static | moonlit_exterior | 100.000% | 20.5585 | 3.039 ms |
| corridor_static | boss_arena | 51.311% | 5.1711 | 3.119 ms |
| arena_combat | dungeon_torch | — | — | — |
| arena_combat | moonlit_exterior | 100.000% | 26.4169 | — |
| arena_combat | boss_arena | 81.125% | 8.8848 | — |
| dense_city | dungeon_torch | — | — | — |
| dense_city | moonlit_exterior | 100.000% | 31.1702 | — |
| dense_city | boss_arena | 57.151% | 2.6396 | — |

## S02 · ShadowStability

- Low vs ultra: **1.526 ms → 3.144 ms** (+106.0%).
- Temporal shadow flicker: `NOT_RUN`.

## S03 · GI Atlas

- SDFGI vs off: **1.976 ms → 3.140 ms** (+58.9%); allocation delta **+451.1 MiB**.
- Decisão: SDFGI apenas em perfis de qualidade.

## S04 · FogWeave

- Volumetric vs depth: **3.008 ms → 3.145 ms** (+4.6%).
- Fallback de depth fog documentado para Performance.

## S05 · LightBridge

- 13 checks determinísticos com dois consumidores mock; veredito `PASS`.

## S06 · LightBudget

- 2 vs 4 tochas com sombra: **3.150 ms → 3.020 ms** (-4.1%).
- MVP baseado em energia; distância/visibilidade ainda `RESEARCH_MORE`.

## S07 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| CineLight Bible | **GO** | 3 original dark-fantasy looks rendered in 3 scenes |
| ShadowStability | **GO_WITH_LIMITATIONS** | low/ultra rendered; temporal shadow flicker not measured |
| GI Atlas | **GO_QUALITY_PROFILE_ONLY** | SDFGI +58.9% GPU and +451.1 MiB allocation |
| FogWeave | **GO_WITH_FALLBACK** | volumetric +4.6% GPU vs depth fog |
| LightBridge | **GO** | 13 deterministic checks with two mock consumers |
| LightBudget | **RESEARCH_MORE** | energy-only shadow slots; 2 vs 4 shadowed torches saves 4.1% GPU |

## Observações

- three original looks are rendered at 1920x1080 on the RTX 5050; performance was measured on corridor_static only
- SDFGI is the dominant cost: +58.9% GPU p95 and +473 MiB allocation vs off
- shadow quality from low to ultra roughly doubles GPU p95
- volumetric fog adds only 4.6% over depth fog on this light workload
- the LightBridge passes 13 deterministic checks with two mock consumers

## Limitações

- single session, one GPU and driver; static frames
- the scenes are simple reference geometry, not production art
- SDFGI/LightmapGI/VoxelGI bake and editor-only paths are not exercised
- temporal shadow flicker and combat legibility with real telegraphs are not measured
- no PoE2 parity, FPS or cross-device claim

Gerado por `docs/benchmarks/m03/tools/build_lighting_runtime.py`; não é benchmark de jogo nem paridade com PoE2.

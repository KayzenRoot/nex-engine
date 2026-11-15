# NEX M02 · Scene analysis (S02/S03/S04) — RTX 5050

**Status:** `SCENE_ANALYSIS_DERIVED / HEADLESS / NO_RENDERING_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-analysis` · **Source SHA:** `57f204ef7237243da13af66560f80d4a726c7d56`
**Harness SHA-256:** `b1a1f726c6289059b240e0244a0dd68db6d2ed2971f0670a0a08046a12172b14`

| Cena | Meshes | Occluders | Primitives | Reveals | Z-fight | Alpha/overlay | Temporal |
|---|---:|---:|---:|---:|---:|---|---|
| corridor_static | 17 | 8 | 16 | 1 | 0 | 0/0 | BASELINE_ACCEPTABLE |
| arena_combat | 34 | 8 | 16 | 1 | 4 | 0/0 | BASELINE_ACCEPTABLE |
| dense_city | 23 | 8 | 16 | 1 | 4 | 0/0 | BASELINE_ACCEPTABLE |

## Observações

- the sightline policy reveals the player behind the largest occluder and raises one danger alert in every scene
- no critical actor is left unseen in any scene
- the depth planner reports 0 z-fight risks in corridor and 4 in arena/city; no alpha-over-critical or overlay-gameplay conflicts
- the temporal analyzer returns BASELINE_ACCEPTABLE on the five static frames of all three scenes
- these are headless analysis results over real scene AABBs and static frames, not rendering or quality claims

## Limitações

- meshes are approximated as AABBs or spheres; per-pixel depth, edges, aliasing and transparency are not evaluated
- one deterministic actor layout per scene; no gameplay or animation
- temporal analysis uses 4x4 luminance regions from static frames; real TAA/upscale/compositor remain INCONCLUSIVE_NOT_RUN
- no rendering, GPU, FPS, quality or cross-device claim

Relatório gerado por `docs/benchmarks/m02/tools/build_analysis_integration.py`; não é benchmark nem claim de qualidade.

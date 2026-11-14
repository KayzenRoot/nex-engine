# NEX M09 · Measurement atlas — RTX 5050

**Status:** `MEASUREMENT_CAMPAIGN_INDEXED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Totais:** 8 bundles · 144 capturas de performance · 18 imagens · 330 arquivos de evidência · 8 source SHAs

## Bundles

| Bundle | Tipo | Runs | Arquivos | Source SHA | Verdict |
|---|---|---:|---:|---|---|
| preset-ab | performance | 6 | 15 | `baf818ef934c` | MEASURED_COST_OBSERVED |
| proxy-scaling | performance | 18 | 39 | `4e4719ac504d` | MEASURED_COST_OBSERVED |
| m01-ab | performance | 18 | 39 | `617db53d6752` | MEASURED_COST_OBSERVED |
| m01-visual | visual | 18 | 21 | `952b5a63bc16` | VISUAL_DIFFERENCE_OBSERVED |
| res-scaling | performance | 18 | 39 | `6ebb98e8c7c9` | MEASURED_COST_OBSERVED |
| interaction | performance | 24 | 51 | `2ef072c70189` | MEASURED_COST_OBSERVED |
| cross-scene | performance | 48 | 99 | `2a03cbb799bd` | MEASURED_COST_OBSERVED |
| interaction-200 | performance | 12 | 27 | `c1b73743c0c9` | MEASURED_COST_OBSERVED |

## Achados cross-experiment

- The high preset costs more GPU time than the low preset in every measured scene and cell; the relative cost grows with resolution.
- At 50-200 proxies on arena_combat, resolution dominates GPU cost while proxy count has a small GPU effect and a larger CPU effect.
- The resolution-dominance pattern repeats in corridor_static and dense_city, not only in arena_combat.
- Visual A/A captures are byte-identical within each scene/preset pair; A/B captures differ in 1.745-4.077% of pixels at 1280x720.
- All evidence is single-session on one RTX 5050; no cross-device or cross-session generalization is claimed.

## Perguntas abertas

- 2560x1440 and ultrawide resolutions above 1920x1080 are not measured.
- Other GPUs, drivers and CPU platforms are not measured.
- Animation, temporal effects, camera motion and real game workloads are not covered.
- Preset application in the hub/engine and M09 parent admission remain out of scope.

## Limitações

- synthesis of already integrated evidence; no new capture
- single session and one GPU across all bundles
- measurements are costs and visual pixel differences, not game FPS or quality
- no cross-device or cross-session generalization
- M09 parent remains NOT_ADMITTED

Atlas gerado por `docs/benchmarks/m09/tools/build_measurement_atlas.py`; não é benchmark nem claim de ganho.

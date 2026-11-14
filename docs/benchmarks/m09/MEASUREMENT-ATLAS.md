# NEX M09 · Measurement atlas — RTX 5050

**Status:** `MEASUREMENT_CAMPAIGN_INDEXED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Totais:** 13 bundles · 156 capturas de performance · 84 imagens · 435 arquivos de evidência · 13 source SHAs

## Bundles

| Bundle | Tipo | Runs | Arquivos | Source SHA | Verdict |
|---|---|---:|---:|---|---|
| preset-ab | performance | 6 | 15 | `baf818ef934c` | MEASURED_COST_OBSERVED |
| proxy-scaling | performance | 18 | 39 | `4e4719ac504d` | MEASURED_COST_OBSERVED |
| m01-ab | performance | 18 | 39 | `617db53d6752` | MEASURED_COST_OBSERVED |
| m01-visual | visual | 18 | 21 | `952b5a63bc16` | VISUAL_DIFFERENCE_OBSERVED |
| m01-visual-1920 | visual | 18 | 21 | `06eb6d92da50` | VISUAL_DIFFERENCE_OBSERVED |
| m01-visual-2560 | visual | 18 | 21 | `4f739cd68086` | VISUAL_DIFFERENCE_OBSERVED |
| m01-temporal | visual | 30 | 33 | `22f428aebf43` | TEMPORAL_STABILITY_OBSERVED |
| res-scaling | performance | 18 | 39 | `6ebb98e8c7c9` | MEASURED_COST_OBSERVED |
| interaction | performance | 24 | 51 | `2ef072c70189` | MEASURED_COST_OBSERVED |
| cross-scene | performance | 48 | 99 | `2a03cbb799bd` | MEASURED_COST_OBSERVED |
| interaction-200 | performance | 12 | 27 | `c1b73743c0c9` | MEASURED_COST_OBSERVED |
| interaction-200-720 | performance | 6 | 15 | `99eaad041b84` | MEASURED_COST_OBSERVED |
| res-scaling-1440 | performance | 6 | 15 | `39633b347784` | MEASURED_COST_OBSERVED |

## Achados cross-experiment

- The high preset costs more GPU time than the low preset in every measured scene and cell; the relative cost grows with resolution.
- At 50-200 proxies on arena_combat, resolution dominates GPU cost while proxy count has a small GPU effect and a larger CPU effect.
- At 1280x720, 200 proxies change GPU p95 by only +1.3%/+1.8% versus the 100-proxy context while CPU p95 rises +48.7%/+29.0%; the M03 ab-high prediction remains within 2%.
- At 2560x1440 the high/low ratio is +651.0% and the M03 ab-high prediction is 70.3% below measured; the 2% match is confined to 1280x720.
- The resolution-dominance pattern repeats in corridor_static and dense_city, not only in arena_combat.
- Visual A/A captures are byte-identical within each scene/preset pair; A/B captures differ in 1.745-4.077% of pixels at 1280x720, 1.276-3.367% at 1920x1080 and 1.031-3.074% at 2560x1440.
- All evidence is single-session on one RTX 5050; no cross-device or cross-session generalization is claimed.

## Perguntas abertas

- Resolutions above 2560x1440 and ultrawide aspect ratios are not measured.
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

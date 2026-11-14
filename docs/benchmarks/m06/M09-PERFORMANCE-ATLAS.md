# NEX M06 · M09 performance atlas — RTX 5050

**Status:** `M09_PERFORMANCE_ATLAS_DERIVED / SINGLE_SESSION / NO_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `docs/benchmarks/m06/observations/m09-observations-full.v1.json` · **Observações:** 156 · **Bundles:** 9

## Bundles

| Bundle | Runs | Scenes | Presets | GPU p95 median | CPU p95 median | Pacing p95 median | Max GPU share | Bottleneck |
|---|---:|---|---|---:|---:|---:|---:|---|
| preset-ab | 6 | 1 | 2 | 0.449 | 0.416 | 4.215 | 21.05% | {'pacing': 6} |
| proxy-scaling | 18 | 1 | 2 | 0.462 | 0.378 | 4.264 | 20.68% | {'pacing': 18} |
| m01-ab | 18 | 3 | 2 | 0.239 | 0.393 | 4.229 | 12.87% | {'pacing': 18} |
| res-scaling | 18 | 1 | 2 | 0.236 | 0.387 | 4.242 | 19.40% | {'pacing': 18} |
| interaction | 24 | 1 | 2 | 0.224 | 0.276 | 4.242 | 19.47% | {'pacing': 24} |
| cross-scene | 48 | 2 | 2 | 0.188 | 0.401 | 4.263 | 18.59% | {'pacing': 48} |
| interaction-200 | 12 | 1 | 2 | 0.239 | 0.432 | 4.264 | 19.92% | {'pacing': 12} |
| interaction-200-720 | 6 | 1 | 2 | 0.290 | 0.561 | 4.233 | 11.10% | {'pacing': 6} |
| res-scaling-1440 | 6 | 1 | 2 | 0.877 | 0.442 | 4.268 | 36.29% | {'pacing': 6} |

## Top 10 células por GPU p95

| Bundle | Cena | Preset | Resolução | Proxies | Runs | GPU p95 | CPU p95 | Pacing p95 | GPU share |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| res-scaling-1440 | m01-arena | ab-high | 2560×1440 | 100 | 3 | 1.547 | 0.493 | 4.269 | 36.29% |
| preset-ab | preset-ab | ab-high | 1280×720 | 200 | 3 | 0.881 | 0.472 | 4.222 | 21.05% |
| proxy-scaling | preset-ab | ab-high | 1280×720 | 200 | 3 | 0.879 | 0.457 | 4.256 | 20.68% |
| interaction-200 | m01-arena | ab-high | 1920×1080 | 200 | 3 | 0.845 | 0.518 | 4.294 | 19.92% |
| proxy-scaling | preset-ab | ab-high | 1280×720 | 100 | 3 | 0.833 | 0.444 | 4.274 | 19.56% |
| res-scaling | m01-arena | ab-high | 1920×1080 | 100 | 3 | 0.826 | 0.454 | 4.273 | 19.40% |
| interaction | m01-arena | ab-high | 1920×1080 | 100 | 3 | 0.826 | 0.330 | 4.243 | 19.47% |
| interaction | m01-arena | ab-high | 1920×1080 | 50 | 3 | 0.820 | 0.306 | 4.240 | 19.34% |
| cross-scene | m01-corridor | ab-high | 1920×1080 | 100 | 3 | 0.790 | 0.451 | 4.259 | 18.59% |
| cross-scene | m01-corridor | ab-high | 1920×1080 | 50 | 3 | 0.784 | 0.425 | 4.242 | 18.48% |

## Resumo

- Bottlenecks: {'pacing': 156}.
- GPU p95 global: 0.068–1.550 ms (mediana 0.226).
- Pacing p95: 4.199–4.311 ms.
- Maior GPU share: 36.29%.

## Observações

- All 156 observations classify as pacing at the 240 fps cap.
- The atlas aggregates seven M09 performance bundles by bundle and workload cell.
- GPU p95 varies with scene, preset, resolution and proxy count; the per-bundle cells retain that detail.
- The atlas is a derived index of measured observations, not a new benchmark or a quality claim.

## Limitações

- single session on one RTX 5050 across all bundles
- no cross-device, cross-driver or cross-session generalization
- GPU render timing can describe earlier work and is not frame-aligned
- renderer allocation is session history, not device VRAM
- no FPS gain, quality or universal recommendation is claimed
- M06 bounded admission covers evidence/analysis only

Atlas gerado por `docs/benchmarks/m06/tools/build_m09_atlas.py`; não é benchmark nem claim de ganho.

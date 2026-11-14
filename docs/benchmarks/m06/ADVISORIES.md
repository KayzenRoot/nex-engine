# NEX M06 · Performance advisories — RTX 5050

**Status:** `ADVISORIES_DERIVED_FROM_MEASURED_OBSERVATIONS / SINGLE_SESSION / NO_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `docs/benchmarks/m06/observations/m09-observations.v1.json` · **Observações:** 12

## Resumo

- Bottlenecks: {'pacing': 12}.
- Headroom de render: 3.402–3.914 ms.
- Maior participação GPU no frame: 19.92%.
- Frame alvo a 240 fps: 4.167 ms.

## Advisórios

| Observação | Cena | Proxies | Resolução | GPU ms | CPU ms | Pacing ms | Headroom ms | GPU % | CPU % | Bottleneck |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| m09-preset-ab-low | preset-ab | 200 | 1280×720 | 0.147 | 0.357 | 4.199 | 3.842 | 3.50 | 8.50 | pacing |
| m09-preset-ab-high | preset-ab | 200 | 1280×720 | 0.746 | 0.467 | 4.222 | 3.476 | 17.67 | 11.06 | pacing |
| m09-m01-corridor-low | m01-corridor | 100 | 1280×720 | 0.086 | 0.328 | 4.208 | 3.880 | 2.04 | 7.79 | pacing |
| m09-m01-corridor-high | m01-corridor | 100 | 1280×720 | 0.542 | 0.475 | 4.210 | 3.668 | 12.87 | 11.28 | pacing |
| m09-res-960-low | m01-arena | 100 | 960×540 | 0.096 | 0.318 | 4.225 | 3.907 | 2.27 | 7.53 | pacing |
| m09-res-960-high | m01-arena | 100 | 960×540 | 0.317 | 0.444 | 4.203 | 3.759 | 7.54 | 10.56 | pacing |
| m09-res-1920-low | m01-arena | 100 | 1920×1080 | 0.156 | 0.344 | 4.241 | 3.897 | 3.68 | 8.11 | pacing |
| m09-res-1920-high | m01-arena | 100 | 1920×1080 | 0.826 | 0.446 | 4.273 | 3.447 | 19.33 | 10.44 | pacing |
| m09-i200-960-low | m01-arena | 200 | 960×540 | 0.099 | 0.357 | 4.261 | 3.904 | 2.32 | 8.38 | pacing |
| m09-i200-960-high | m01-arena | 200 | 960×540 | 0.322 | 0.506 | 4.264 | 3.758 | 7.55 | 11.87 | pacing |
| m09-i200-1920-low | m01-arena | 200 | 1920×1080 | 0.157 | 0.361 | 4.275 | 3.914 | 3.67 | 8.44 | pacing |
| m09-i200-1920-high | m01-arena | 200 | 1920×1080 | 0.846 | 0.518 | 4.248 | 3.402 | 19.92 | 12.19 | pacing |

## Recomendações

- `m09-preset-ab-low`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-preset-ab-high`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-corridor-low`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-corridor-high`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-960-low`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-960-high`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-1920-low`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-1920-high`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-i200-960-low`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-i200-960-high`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-i200-1920-low`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-i200-1920-high`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).

## Limitações

- advisories are derived from one session on one RTX 5050; no cross-device or cross-session generalization
- renderer allocation bytes are session history, not device VRAM
- GPU render timing can describe earlier work and is not frame-aligned
- headroom is relative to this capped run and does not prove capacity at another cap or workload
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m06/tools/build_advisories.py`; não é benchmark nem claim de ganho.

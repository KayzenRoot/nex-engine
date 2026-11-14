# NEX M03 · Light budget domain boundary — RTX 5050

**Status:** `CALIBRATION_RESOLUTION_MATCH_ONLY / SINGLE_SESSION / NO_MODEL_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`

**Modelo:** `docs/benchmarks/m03/light-cost-model.v1.json` · **Fonte medida:** `docs/benchmarks/m09/res-scaling.v1.json`
**Workload:** arena_combat · 100 proxies · lights

## Projeções vs medido por resolução

| Preset | Resolução | Omni | Shadowed | Previsto ms | Medido p95 ms | Erro ms | Erro % | Dentro de 2% |
|---|---|---:|---:|---:|---:|---:|---:|---|
| ab-low | 960×540 | 4 | 0 | 0.37900 | 0.096 | +0.28300 | +294.8% | não |
| ab-high | 960×540 | 4 | 4 | 0.46000 | 0.317 | +0.14300 | +45.1% | não |
| ab-low | 1280×720 | 4 | 0 | 0.37900 | 0.106 | +0.27300 | +257.5% | não |
| ab-high | 1280×720 | 4 | 4 | 0.46000 | 0.460 | +0.00000 | +0.0% | sim |
| ab-low | 1920×1080 | 4 | 0 | 0.37900 | 0.156 | +0.22300 | +142.9% | não |
| ab-high | 1920×1080 | 4 | 4 | 0.46000 | 0.826 | -0.36600 | -44.3% | não |

## Sensibilidade à resolução

- Delta previsto 960→1920: 0.000 ms.
- Delta medido ab-low: +0.060 ms (+62.5%).
- Delta medido ab-high: +0.509 ms (+160.6%).

## Robustez a proxies (200/1280)

| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |
|---|---:|---:|---:|---|
| ab-low | 0.379 | 0.111 | +241.4% | não |
| ab-high | 0.460 | 0.468 | -1.7% | sim |

## Alta resolução (2560×1440)

| Preset | Previsto ms | Medido p95 ms | Erro | Dentro de 2% |
|---|---:|---:|---:|---|
| ab-low | 0.379 | 0.206 | +84.0% | não |
| ab-high | 0.460 | 1.547 | -70.3% | não |

## Resumo

- Células: 6 · dentro de 2%: 1.
- Maior erro absoluto: 294.8%.
- Veredito: `CALIBRATION_RESOLUTION_MATCH_ONLY`.

## Observações

- in the resolution grid, only the ab-high cell at 1280x720 is within 2% (+0.0%); the same prediction is off by +45.1% at 960x540 and -44.3% at 1920x1080
- the model is resolution-invariant (predicted delta 960->1920 = 0.000 ms), while measured GPU p95 grows 62.5% (ab-low) and 160.6% (ab-high)
- at 200 proxies and 1280x720 the ab-high prediction remains within 2% (-1.7%), while ab-low is +241.4% above measured
- at 2560x1440 the ab-high prediction is -70.3% and ab-low +84.0%; neither is within 2%
- the 2% match is confined to 1280x720 and is robust to a 100->200 proxy change, but not to resolution changes

## Limitações

- model coefficients are calibrated from one S05 session at 25 proxies and 1280x720
- the model represents lights and shadows only; it does not represent resolution scale, MSAA, glow, atlas or scene geometry
- the resolution grid uses 100 proxies on one arena scene in one session
- the 200/1280 and 2560/1440 evidence comes from separate sessions and is labeled as such
- the comparison uses medians from different sessions and different presets
- no FPS, quality or universal recommendation is claimed
- M03 parent remains NOT_ADMITTED

Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py --domain`; não é benchmark nem claim de ganho.

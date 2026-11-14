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

## Resumo

- Células: 6 · dentro de 2%: 1.
- Maior erro absoluto: 294.8%.
- Veredito: `CALIBRATION_RESOLUTION_MATCH_ONLY`.

## Observações

- only the ab-high cell at 1280x720 is within 2% (+0.0%); the same prediction is off by +45.1% at 960x540 and -44.3% at 1920x1080
- the model is resolution-invariant (predicted delta 960->1920 = 0.000 ms), while measured GPU p95 grows 62.5% (ab-low) and 160.6% (ab-high)
- the 2% match is therefore specific to the calibration resolution, not evidence of general validity
- the low preset is overestimated at every resolution, consistent with unmodeled resolution scale, MSAA and glow

## Limitações

- model coefficients are calibrated from one S05 session at 25 proxies and 1280x720
- the model represents lights and shadows only; it does not represent resolution scale, MSAA, glow, atlas or scene geometry
- the resolution bundle uses 100 proxies on one arena scene in one session
- the comparison uses medians from a different session and different presets
- no FPS, quality or universal recommendation is claimed
- M03 parent remains NOT_ADMITTED

Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py --domain`; não é benchmark nem claim de ganho.

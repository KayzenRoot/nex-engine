# NEX M03 · Light budget validation — RTX 5050

**Status:** `PARTIAL_DOMAIN_MATCH / SINGLE_SESSION / NO_MODEL_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`

**Modelo:** `docs/benchmarks/m03/light-cost-model.v1.json` · **Fonte medida:** `docs/benchmarks/m09/m01-ab.v1.json`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus

## Projeções vs medido

| Cena | Preset | Omni | Shadowed | Previsto ms | Medido p95 ms | Erro ms | Erro % | Dentro de 2% |
|---|---|---:|---:|---:|---:|---:|---:|---|
| corridor_static | ab-low | 3 | 0 | 0.35450 | 0.088 | +0.26650 | +302.8% | não |
| corridor_static | ab-high | 3 | 3 | 0.41525 | 0.423 | -0.00775 | -1.8% | sim |
| arena_combat | ab-low | 4 | 0 | 0.37900 | 0.109 | +0.27000 | +247.7% | não |
| arena_combat | ab-high | 4 | 4 | 0.46000 | 0.462 | -0.00200 | -0.4% | sim |
| dense_city | ab-low | 5 | 0 | 0.40350 | 0.084 | +0.31950 | +380.4% | não |
| dense_city | ab-high | 5 | 4 | 0.48450 | 0.362 | +0.12250 | +33.8% | não |

## Resumo

- Células: 6 · dentro de 2%: 2.
- Maior erro absoluto: 380.4%.
- Veredito: `PARTIAL_DOMAIN_MATCH`.

## Observações

- The model's high-preset projections match the measured corridor and arena GPU p95 within 2%.
- The low-preset projections overestimate measured GPU p95 by 247.7-380.4%, because the low preset also changes resolution scale, MSAA and glow in ways the model does not represent.
- City high differs by +33.8%; the model does not represent scene geometry, resolution scale, MSAA, glow or atlas changes.
- The match for two high-preset cells is a domain-limited coincidence candidate, not proof that the model generalizes.

## Limitações

- model coefficients are calibrated from one S05 session at 25 proxies and 1280x720
- the model represents lights and shadows only; it does not represent resolution scale, MSAA, glow, atlas or scene geometry
- the comparison uses medians from a different session and different presets
- two high-preset cells within 2% do not establish general validity
- no FPS, quality or universal recommendation is claimed
- M03 parent remains NOT_ADMITTED

Relatório gerado por `docs/benchmarks/m03/tools/build_budget_validation.py`; não é benchmark nem claim de ganho.

# NEX M03 · Light budget validation

**Status:** `PARTIAL_DOMAIN_MATCH / SINGLE_SESSION / NO_MODEL_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório compara o modelo `nex_light_cost_model.v1` (M03) com os valores GPU p95 medidos nas três cenas M01 (M09).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `light-cost-model.v1.json` | Snapshot dos coeficientes de `DEFAULT_MODEL` no `light_budget_arbiter.gd`. |
| `budget-validation.v1.json` | 6 células (3 cenas × 2 presets) com previsto, medido, erro e veredito. |
| `BUDGET-VALIDATION.md` | Relatório humano. |
| `tools/build_budget_validation.py` | Builder determinístico com `--check`. |

## Metodologia

1. Lê o snapshot e confere cada coeficiente contra `DEFAULT_MODEL` no GDScript.
2. Lê os medidos `ab-low`/`ab-high` de `docs/benchmarks/m09/m01-ab.v1.json`.
3. Projeta `base + omni*per_omni + directional_shadow + shadowed*per_omni_shadow` para cada cena/preset.
4. Compara com o medido e calcula erro absoluto/percentual.
5. Marca `within_2pct` quando o erro absoluto é ≤ 2%.

## Uso

```powershell
python docs/benchmarks/m03/tools/build_budget_validation.py
python docs/benchmarks/m03/tools/build_budget_validation.py --check
```

## Limitações

- Coeficientes calibrados em uma sessão S05, 25 proxies, 1280×720.
- O modelo representa luzes/sombras; não representa resolução, MSAA, glow, atlas ou geometria.
- A comparação usa medidos de outra sessão e presets diferentes.
- Dois acertos em 2% não provam validade geral.
- Nenhum claim de FPS, qualidade ou recomendação universal.

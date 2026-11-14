# NEX M03 · Light budget validation

**Status:** `PARTIAL_DOMAIN_MATCH / SINGLE_SESSION / NO_MODEL_CHANGE / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório compara o modelo `nex_light_cost_model.v1` (M03) com os valores GPU p95 medidos nas três cenas M01 (M09).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `light-cost-model.v1.json` | Snapshot dos coeficientes de `DEFAULT_MODEL` no `light_budget_arbiter.gd`. |
| `budget-validation.v1.json` | 6 células (3 cenas × 2 presets) com previsto, medido, erro e veredito. |
| `BUDGET-VALIDATION.md` | Relatório humano. |
| `budget-domain-boundary.v1.json` | 6 células da arena em 960×540/1280×720/1920×1080, mais 200/1280 e 2560×1440. |
| `BUDGET-DOMAIN-BOUNDARY.md` | Relatório humano da fronteira de domínio. |
| `tools/build_budget_validation.py` | Builder determinístico com `--check`, `--domain` e `--check-domain`. |

## Metodologia

1. Lê o snapshot e confere cada coeficiente contra `DEFAULT_MODEL` no GDScript.
2. Lê os medidos `ab-low`/`ab-high` de `docs/benchmarks/m09/m01-ab.v1.json`.
3. Projeta `base + omni*per_omni + directional_shadow + shadowed*per_omni_shadow` para cada cena/preset.
4. Compara com o medido e calcula erro absoluto/percentual.
5. Marca `within_2pct` quando o erro absoluto é ≤ 2%.

O modo `--domain` repete a projeção para a arena em 960×540/1280×720/1920×1080 usando `docs/benchmarks/m09/res-scaling.v1.json`, e incorpora **200 proxies em 1280×720** (`interaction-200-720.v1.json`) e **2560×1440** (`res-scaling-1440.v1.json`). Como o modelo não tem termo de resolução nem de proxies, o previsto é constante. O relatório quantifica o delta medido 960→1920 (+62.5% ab-low, +160.6% ab-high), mostra que o único acerto em 2% do grid ocorre em 1280×720, que persiste a 200 proxies (−1.7%) e que não sobrevive a 2560×1440 (−70.3%). Veredito: `CALIBRATION_RESOLUTION_MATCH_ONLY`.

## Uso

```powershell
python docs/benchmarks/m03/tools/build_budget_validation.py
python docs/benchmarks/m03/tools/build_budget_validation.py --check
python docs/benchmarks/m03/tools/build_budget_validation.py --domain
python docs/benchmarks/m03/tools/build_budget_validation.py --check-domain
```

## Limitações

- Coeficientes calibrados em uma sessão S05, 25 proxies, 1280×720.
- O modelo representa luzes/sombras; não representa resolução, MSAA, glow, atlas ou geometria.
- A comparação usa medidos de outra sessão e presets diferentes.
- Os acertos em 2% são a mesma célula ab-high/1280×720 em 100 e 200 proxies; não provam validade geral.
- O recorte de resolução usa uma cena, 100 proxies e uma sessão; não é generalização.
- Os recortes de 200/1280 e 2560×1440 vêm de sessões separadas e são rotulados como tal.
- Nenhum claim de FPS, qualidade ou recomendação universal.

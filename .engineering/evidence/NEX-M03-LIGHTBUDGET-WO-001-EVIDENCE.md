# Evidence Bundle · NEX-M03-LIGHTBUDGET-WO-001 (Lighting-budget arbiter)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_RENDERING / NO_NEW_MEASUREMENT / NO_GENERALIZATION_CLAIM`
**Issue:** #8 · **Base:** `7205f6cb2af590877c84a7654a58cad01ec9e5cd` · **Code SHA:** `26f6ab9334e406ec9e6b834c9eed7aa204bf01e3`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/lighting/budget/`: projeto Godot autocontido com `light_budget_arbiter.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_light_budget_arbiter.py`: 9 testes estruturais (arquivos/projeto, API, modelo versionado e rastreável ao S05, vereditos/escada, ausência de rendering, marcador/evidência, limites documentados, ausência de claim de benchmark).

## Modelo de custo

Coeficientes `nex_light_cost_model.v1`, calibrados pela análise S05 (`nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05/ANALYSIS.md`):

| Coeficiente | Valor (ms) | Âncora S05 |
|---|---:|---|
| `base_gpu_ms` | 0.181 | baseline-25 |
| `per_omni_light_ms` | 0.0245 | lights-25 − baseline |
| `directional_shadow_ms` | 0.100 | ajuste shadows-25 |
| `per_omni_shadow_ms` | 0.02025 | ajuste shadows-25 |
| `per_particle_emitter_ms` | 0.01375 | vfx-25 − baseline |
| `shadow_vfx_interaction_ms` | 0.679 | resíduo combined-25 |

O modelo reproduz os presets de 25 proxies: 0.181 / 0.279 / 0.460 / 0.236 / 1.194 ms.

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/lighting/budget `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M03_LIGHTBUDGET_SMOKE_PASS: 57 checks`** (exit 0), log em `nex_modules/lighting/budget/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 57 checks:
- configuração de orçamento e coeficientes: limites, chaves desconhecidas, negativos, override e reset;
- projeções baseline/lights/shadows/vfx/combined idênticas às âncoras S05;
- breakdown soma a projeção; termo de interação só com sombra direcional + partículas;
- vereditos FIT/TIGHT/OVER_BUDGET e headroom;
- entradas inválidas (contagens negativas, shadowed > lights, partículas acima do limite, chave ausente, flag não booleana) → `INVALID_INPUT` com razão;
- escada de degradação ordenada, clamps de luzes, `fits`, cena recomendada dentro do orçamento e skip de passos inaplicáveis;
- determinismo, último relatório e `clear()` restaurando defaults.

## O que não foi feito / não é alegado

- Nenhuma captura GPU nova, rendering, luz, sombra ou partícula criada.
- Coeficientes vêm de **uma sessão sintética** em RTX 5050 a 25 proxies; não são frame time, FPS ou benchmark, e **não generalizam** para outras cenas/hardware.
- O termo de interação vem de **uma única captura combinada**; é heurística de planejamento.
- A escada de degradação não foi validada visualmente; passos são opções de planejamento.
- Performance/qualidade de cena real: `INCONCLUSIVE_NOT_RUN`.
- M03 parent (#8) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/lighting/budget/**`, `tests/ci/test_light_budget_arbiter.py`, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine, captura ou checkpoint é alterado por este bundle.

## Próximos passos

- Validar a escada em cena real exige WO de rendering/medição com orçamento e repetições.
- M04/M05/M06/M08 permanecem não admitidos.

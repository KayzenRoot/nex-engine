# Evidence Bundle · NEX-M03-SHADOWSTAB-WO-001 (Shadow-stability analyzer)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_RENDERING / NO_SHADOW_IMPLEMENTATION / NO_VISUAL_CLAIM`
**Issue:** #8 · **Base:** `346c6dd6bd85c12e3aad1250d8cae95b195bd605` · **Code SHA:** `6db0a5ee32b695cef9892267301be7157b95c2cc`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/lighting/shadows/`: projeto Godot autocontido com `shadow_stability_analyzer.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_shadow_stability_analyzer.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `lighting.v1`/`lighting.plan.v1`, veredictos, ausência de rendering, marcador/evidência, limites documentados, ausência de claim visual/performance).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/lighting/shadows `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M03_SHADOWSTAB_SMOKE_PASS: 51 checks`** (exit 0), log em `nex_modules/lighting/shadows/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 51 checks:
- configuração de câmera/split lambda: limites, rejeição e restauração;
- plano válido: veredicto `STABLE_CONFIG_HEURISTIC_WITH_NOTES`, contagens, tiles, pressão, splits monotônicos, limitações e determinismo;
- bias baixo/alto: riscos de acne e peter-panning;
- atlas pequeno: pressão e banding de sombra suave;
- orçamento zero/excedido, cascatas ausentes/excedidas, caster sem energia, caster demovido e atribuição ausente;
- workload vazio, análise de observação `lighting.v1`, schemas inválidos e luz malformada → `INCONCLUSIVE` com razão;
- câmera configurada dirige os splits; `clear()` restaura defaults.

## O que não foi feito / não é alegado

- Nenhum shadow map, filtro, luz, shader, cena ou renderer criado; nenhum arquivo em `nex_bench/**`, engine ou CI alterado.
- Acne, peter-panning, shimmer e seams **não medidos**; os achados são heurísticas de planejamento.
- Splits usam esquema prático, não o cascade fitter da engine; pressão de atlas é aritmética.
- Performance/qualidade/frame-time/VRAM: `INCONCLUSIVE_NOT_RUN`.
- M03 parent (#8) permanece `NOT_ADMITTED`; integração real exige WO própria.

## Rollback

Remover `nex_modules/lighting/shadows/**`, `tests/ci/test_shadow_stability_analyzer.py`, este bundle, o delta e a WO/lock correspondentes. Nenhum estado de engine, contrato ou checkpoint é alterado por este bundle.

## Próximos passos

- Validação visual de sombras exige WO de cena/rendering com medição real.
- M03-S03 (GI), S04 (fog) e S05 (LightBridge) seguem não admitidos; o analisador é insumo de planejamento.

# Evidence Bundle · NEX-M08-COMPOSITION-WO-001 (2.5D composition planner)

**Status:** `PROTOTYPE_EVIDENCE / PLANNING_ONLY / NO_RENDERING / NO_VIEWPORT / NO_VISUAL_CLAIM`
**Issue:** #13 · **Base:** `5159d774436015870ab4fec1fe1416d5a8190cd1` · **Code SHA:** `0f1cc07f8175b0f4b17a535721df28a2dcbf3814`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/render2_5d/composition/`: projeto Godot autocontido com `composition_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_composition_planner.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `composition.v1`, vereditos/achados, ausência de rendering, marcador/evidência, limites, ausência de claim visual).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render2_5d/composition `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M08_COMPOSITION_SMOKE_PASS: 69 checks`** (exit 0), log em `nex_modules/render2_5d/composition/evidence/headless-smoke-2026-11-13.log`.

Cobertura dos 69 checks:
- configuração de limites/alpha guard, base plan (none/real/digest), políticas de profundidade/HUD/conflict;
- registro de camadas/entidades, duplicatas, papéis/blends/parallax/alpha/override inválidos e cap;
- plano seguro: ordem background→gameplay→foreground→HUD, draw indexes, parallax efetivo, políticas, entidades ordenadas, determinismo;
- conflitos: parallax fora da banda, alpha sobre entidade crítica, critical guard ausente, HUD cobrindo gameplay (report/block), HUD com depth override, override sob `inherit_3d`, override ausente sob `override_per_layer`, riscos do plano 3D, HUD ausente/referência inválida, reordenação e camada crítica sem entidade;
- estados inválidos: stack vazio, sem entidades críticas, cap de camadas;
- exportação `composition.v1` com performance `UNAVAILABLE`, campos exclusivos omitidos, HUD sem override e proveniência validada;
- `clear()` restaura defaults.

## O que não foi feito / não é alegado

- Nenhuma camada, viewport, shader, cena ou renderer criado; nenhum pixel composto.
- Alpha-over-critical é aritmética de alpha/profundidade, não cobertura de pixel; bandas de parallax são heurísticas.
- Ordem de draw agrupa papéis; o planejador não reordena primitivas 3D.
- Composição visual/edge cases/runtime: `INCONCLUSIVE_NOT_RUN`.
- M08 parent (#13) permanece `NOT_ADMITTED`; integração real exige WO própria.

## Rollback

Remover `nex_modules/render2_5d/composition/**`, `tests/ci/test_composition_planner.py`, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Integração 2.5D em cena/viewport exige WO própria com rendering e medição.
- M09–M12 permanecem não admitidos.

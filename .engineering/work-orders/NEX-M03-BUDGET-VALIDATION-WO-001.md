# NEX-M03-BUDGET-VALIDATION-WO-001 | Validação do light budget contra dados M09

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o contrato M03 existente.
**Base:** `main` `71375d6621bb179abe88fde398fb62a7fe16da80`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (síntese de evidência).
**Lock:** `.engineering/context-locks/NEX-M03-BUDGET-VALIDATION-WO-001-EXECUTION.json`.

## Objetivo

Comparar as projeções do `nex_light_cost_model.v1` com os valores GPU p95 medidos nas três cenas M01 sob `ab-low`/`ab-high` (1280×720), documentando erros e limites de domínio. Isto exercita o modelo M03 contra dados M09 reais, sem nova captura e sem admitir o parent M03.

## Escopo

- `docs/benchmarks/m03/**`: snapshot `light-cost-model.v1.json`, relatório `budget-validation.v1.json`, `BUDGET-VALIDATION.md` e builder.
- `tests/ci/test_m03_budget_validation.py`: coeficientes, projeções, erros, ausência de overclaim e reprodutibilidade.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar o modelo, `light_budget_arbiter.gd`, contrato M03, engine, cenas, `project.godot`, hub ou CI.
- Nova captura, nova medição, recomendação de hardware ou generalização.
- M03 parent admission.

## DoD

- Snapshot do modelo confere com `DEFAULT_MODEL` do GDScript.
- 6 projeções (3 cenas × 2 presets) com medido, previsto, erro absoluto/percentual e veredito de domínio.
- Nenhum claim de FPS, qualidade ou generalização; confounders documentados.
- Builder reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Coeficiente divergir do GDScript, dado M09 ausente, contagem divergir ou builder não reproduzir → parar e registrar.

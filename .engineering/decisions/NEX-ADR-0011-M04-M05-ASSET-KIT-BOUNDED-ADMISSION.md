# NEX-ADR-0011 · Admissão bounded do kit M04 e do dataset M05

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `99437b22e94a6494eaef801872bb8fd0c79c0f1a`

## Contexto

`NEX-ADR-0009` admitiu M04/M05 apenas como contratos e protótipos determinísticos e, na condição 2, exigiu **nova decisão do Owner, novo ADR/ledger e WO específica** para criação real de material/textura ou partícula. Em 2026-11-15 o Owner autorizou o trabalho de feature M04/M05 ("vamos continuar faça as 3 por favor"), incluindo texturas/materiais reais e orçamento de FX. Este ADR registra essa decisão e fixa o escopo estritamente não-rendering.

## Decisão

Admitir, de forma bounded, duas extensões **não-rendering**:

### M04 · kit PBR procedural

- `nex_modules/materials/kit/**`: 12 texturas PNG determinísticas (albedo, normal, ORM) em 128×128, quatro materiais `StandardMaterial3D` em `.tres`, uma observação `material.v1` (`kit.v1.json`), script de validação headless e evidência de carregamento.
- `docs/benchmarks/m04/tools/build_material_kit.py`, `docs/benchmarks/m04/MATERIAL-KIT.md` e `tests/ci/test_material_kit.py`.

### M05 · dataset de orçamento de FX

- `nex_modules/vfx/fxbudget/dataset.gd` e a evidência `fx-budget-dataset-2026-11-15.json`: três arquétipos determinísticos (`skirmish`, `elite`, `boss`) analisados pelo `FXBudgetPlanner` integrado.
- `docs/benchmarks/m05/tools/build_fx_budget_dataset.py`, `docs/benchmarks/m05/FX-BUDGET-DATASET.md`, `fx-budget-dataset.v1.json` e `tests/ci/test_fx_budget_dataset.py`.

## Exclusões explícitas

- Nenhum shader customizado, `ShaderMaterial`, compilação de shader ou alteração de renderer.
- Nenhuma integração em cena, aplicação de material, rendering, captura de frame ou GPU execution.
- Nenhum runtime, hub, engine, `project.godot` principal, gameplay, build nativo ou cena de produção.
- Nenhuma criação de partícula, emissor, luz ou decal; o dataset M05 é apenas planejamento.
- Nenhuma decodificação de textura em runtime, compressão, atlas packing ou pipeline de import/cook de produção.
- Nenhum claim de FPS, frame-time, VRAM, overdraw, qualidade visual, game feel ou generalização cross-device.
- A admissão não relaxa CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. Cada incremento exige WO/Context Lock, evidência e todos os checks.
2. Os builders `build_material_kit.py --check` e `build_fx_budget_dataset.py --check` são obrigatórios no Fast Lane.
3. Integração em renderer, cena ou runtime continua exigindo nova decisão do Owner, novo ADR/ledger e WO específica.
4. Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.

## Consequências

- M04 passa a ter um kit de referência real, carregável por `ResourceLoader`, sem rendering.
- M05 passa a ter um dataset de orçamento que exercita `FIT`, `TIGHT` e `OVER_BUDGET` com plano de redução determinístico.
- Os status dos parents permanecem `BOUNDED_ADMITTED_MATERIALS_PIPELINE` e `BOUNDED_ADMITTED_VFX_PIPELINE`; o escopo admitido é estendido apenas onde este ADR lista.
- O kit não é arte de produção nem prova de qualidade; o dataset não é benchmark de hardware.

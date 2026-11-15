# NEX-ADR-0010 · Admissão bounded dos pipelines M07/M08/M10/M11/M12

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `8bb4bef1b216e71eafe0dc83efe897bb926530ce`

## Contexto

M07 (#12) mantém o contrato e o protótipo de canvas 2D; M08 (#13) mantém o contrato e o protótipo de composição 2.5D; M10 (#15) mantém o contrato e o protótipo de feedback de combate; M11 (#16) mantém o contrato e o protótipo de auditoria de licenças; M12 (#17) mantém o contrato e o validador de identidade. Todos acumularam contratos, documentação, protótipos determinísticos, testes e evidência, mas permaneciam `NOT_ADMITTED`. As admissões M01–M06/M09 já estabeleceram o padrão de escopo bounded sem runtime.

## Decisão

Admitir **de forma bounded** M07, M08, M10, M11 e M12 como pipelines de referência/análise determinística, sem autorizar runtime, renderer, shaders, engine, cenas de produção, geração de assets, aprovação de marca ou claims de performance/qualidade.

**Status por parent:** M07 `BOUNDED_ADMITTED_RENDER2D_PIPELINE`; M08 `BOUNDED_ADMITTED_COMPOSITION_PIPELINE`; M10 `BOUNDED_ADMITTED_ANIMATION_PIPELINE`; M11 `BOUNDED_ADMITTED_ASSET_PIPELINE`; M12 `BOUNDED_ADMITTED_IDENTITY_PIPELINE`.

### M07 · escopo admitido

- `contracts/m07/render2d.v1.schema.json` e `contracts/m07/ownership.v1.json`.
- `docs/contracts/m07.md`.
- `nex_modules/render2d/canvas/**` (planner determinístico, smoke headless e evidência).
- `tests/ci/test_render2d_planner.py` e testes de contrato M07.

### M08 · escopo admitido

- `contracts/m08/composition.v1.schema.json` e `contracts/m08/ownership.v1.json`.
- `docs/contracts/m08.md` e o draft de composição M08.
- `nex_modules/render2_5d/composition/**` (solver determinístico, smoke headless e evidência).
- `tests/ci/test_composition_planner.py` e testes de contrato M08.

### M10 · escopo admitido

- `contracts/m10/feedback.v1.schema.json` e `contracts/m10/ownership.v1.json`.
- `docs/contracts/m10.md`.
- `nex_modules/animation/combat_feedback/**` (planner determinístico, smoke headless e evidência).
- `tests/ci/test_feedback_planner.py` e testes de contrato M10.

### M11 · escopo admitido

- `contracts/m11/asset_pipeline.v1.schema.json` e `contracts/m11/ownership.v1.json`.
- `docs/contracts/m11.md`.
- `nex_modules/assets/license_audit/**` (auditor determinístico, smoke headless e evidência).
- `tests/ci/test_asset_pipeline_auditor.py` e testes de contrato M11.

### M12 · escopo admitido

- `contracts/m12/identity.v1.schema.json` e `contracts/m12/ownership.v1.json`.
- `docs/contracts/m12.md`.
- `nex_modules/brand/tokens/**` (validador determinístico, smoke headless e evidência).
- `tests/ci/test_identity_validator.py` e testes de contrato M12.

## Exclusões explícitas

- Nenhum runtime, hub, engine, renderer, shader, `project.godot`, gameplay ou build nativo.
- Nenhuma renderização real, cena de produção, aplicação de presets ou integração de renderização.
- Nenhuma geração de assets, importação/cozimento, aprovação de marca ou liberação de licenças.
- Nenhum claim de FPS, qualidade visual, game feel, clareza de combate, performance ou ganho.
- M01–M06/M09 permanecem bounded admitted; nenhum parent é promovido a produto completo.
- A admissão não relaxa CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. Cada incremento futuro sob M07/M08/M10/M11/M12 exige WO/Context Lock e todos os checks.
2. Runtime/renderização/geração de assets/aprovação de marca exigem nova decisão do Owner, novo ADR/ledger e WO específica.
3. Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. Claims de performance/qualidade devem citar evidência, sessão e limitações.

## Consequências

- M07/M08/M10/M11/M12 deixam de ser `NOT_ADMITTED` para contratos/protótipos determinísticos, permanecendo **não completos** como produtos.
- Com isso, todos os parents M01–M12 estão bounded admitted em escopo de referência/análise/evidência; nenhum parent permanece `NOT_ADMITTED`.
- O próximo passo legal é um incremento bounded sob qualquer parent admitido ou a preparação de uma admissão de runtime, que exige decisão específica do Owner.
- O checkpoint registra o novo status e a main SHA de admissão.

# NEX-ADR-0009 · Admissão bounded dos pipelines M04/M05

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-14
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `5f801c09ca4148fb9712f84cfd638bd80f3a4372`

## Contexto

M04 (#9) mantém o contrato de materiais PBR e o protótipo determinístico de orçamento de texturas; M05 (#10) mantém o contrato SpellFX e o protótipo determinístico de orçamento de FX. Ambos acumularam contratos, documentação, protótipos headless, testes e evidência, mas permaneciam `NOT_ADMITTED`. As admissões M01/M02/M03/M06/M09 já estabeleceram o padrão de escopo bounded sem runtime.

## Decisão

Admitir **de forma bounded** M04 (#9) e M05 (#10) como `BOUNDED_ADMITTED_MATERIALS_PIPELINE` e `BOUNDED_ADMITTED_VFX_PIPELINE`, respectivamente. A admissão cobre contratos, documentação, protótipos determinísticos, testes e evidência já verificados; **não** autoriza criação de materiais, compilação de shaders, decodificação de texturas, atlas packing, criação de partículas, integração de renderização, runtime, hub, renderer, shaders, `project.godot`, cenas de produção ou claims de performance/qualidade.

### M04 · escopo admitido

- `contracts/m04/material.v1.schema.json` e `contracts/m04/ownership.v1.json`.
- `docs/contracts/m04.md`.
- `nex_modules/materials/texturebudget/**` (planejador determinístico de orçamento de texturas, smoke headless e evidência).
- `tests/ci/test_texture_budget_planner.py` e testes de contrato M04.

### M05 · escopo admitido

- `contracts/m05/spellfx.v1.schema.json` e `contracts/m05/ownership.v1.json`.
- `docs/contracts/m05.md`.
- `nex_modules/vfx/fxbudget/**` (planejador determinístico de orçamento de FX, smoke headless e evidência).
- `tests/ci/test_fx_budget_planner.py` e testes de contrato M05.

## Exclusões explícitas

- Nenhuma criação de material, shader, textura, atlas, partícula, emissor, luz ou decal.
- Nenhuma decodificação de textura, atlas packing, criação de partículas ou integração de renderização.
- Nenhum runtime, hub, renderer, shader, `project.godot`, engine, gameplay ou build nativo.
- Nenhuma renderização real, cena de produção, aplicação de presets ou medição de performance.
- Nenhum claim de FPS, qualidade visual, clareza de combate, game feel ou licenciamento.
- M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- A admissão não relaxa CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. Cada incremento futuro sob M04/M05 exige WO/Context Lock e todos os checks.
2. Criação real de material/shader/partícula, integração de renderização ou runtime exige nova decisão do Owner, novo ADR/ledger e WO específica.
3. Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. Claims de performance/qualidade devem citar evidência, sessão e limitações.

## Consequências

- M04/M05 deixam de ser `NOT_ADMITTED` para contratos/protótipos determinísticos, permanecendo **não completos** como produtos.
- O próximo passo legal é um incremento bounded sob M04/M05 ou a preparação de uma admissão de runtime, que exige decisão específica do Owner.
- O checkpoint registra o novo status e a main SHA de admissão.

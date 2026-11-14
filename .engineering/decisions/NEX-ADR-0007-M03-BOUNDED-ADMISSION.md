# NEX-ADR-0007 · Admissão bounded do pipeline de análise M03

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-14
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `51110ff02eb2c542832b6290a98fdc5f979b58a9`

## Contexto

M03 (#8) acumulou contrato `lighting.v1`, protótipos determinísticos de light rig, shadow stability e light budget, além da validação do modelo de custo contra dados M09. Todos os artefatos têm testes, evidência e checks verdes. A admissão M06/M09 (`NEX-ADR-0006`) já estabeleceu o padrão de admissão bounded por pipeline de evidência/análise.

## Decisão

Admitir **de forma bounded** o pipeline de análise M03 como `BOUNDED_ADMITTED_ANALYSIS_PIPELINE`. A admissão cobre os artefatos verificados abaixo e **não** autoriza runtime, renderer, shaders, cenas, hub, `project.godot`, gameplay ou claims de performance/qualidade.

### Escopo admitido

- `contracts/m03/lighting.v1.schema.json` e `ownership.v1.json`.
- `nex_modules/lighting/light_rig/` (planner determinístico).
- `nex_modules/lighting/shadows/` (shadow stability analyzer).
- `nex_modules/lighting/budget/` (light budget arbiter).
- `docs/benchmarks/m03/` (snapshot do modelo, validação, builder e README).
- Testes M03 de contrato, light rig, shadow stability, light budget e validação.

### Exclusões explícitas

- Nenhum runtime, renderer, shader, cena, hub, `project.godot`, gameplay ou build nativo.
- Nenhuma implementação real de luz/sombra/GI; os protótipos são análise aritmética.
- Nenhuma generalização de performance/qualidade ou claim de FPS.
- M01–M02, M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- A admissão não relaxa CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. Cada incremento futuro sob M03 exige WO/Context Lock e todos os checks.
2. Runtime/renderer/shaders exigem nova decisão do Owner, novo ADR/ledger e WO específica.
3. Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. Claims de performance/qualidade devem citar evidência, sessão e limitações.

## Consequências

- M03 deixa de ser `NOT_ADMITTED` para análise, permanecendo **não completo** como produto.
- M03 pode receber novos enablers de análise/validação sob WO própria.
- O checkpoint registra o novo status e a main SHA de admissão.

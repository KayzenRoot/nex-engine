# NEX-ADR-0006 · Admissão bounded dos pipelines de evidência M06/M09

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-14
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `8ed41bafaf19cff52da9250784f78c3d608ac504`

## Contexto

O Owner instruiu o administrador a executar os três próximos caminhos listados após o ciclo de estabilidade temporal: (1) estabilidade visual temporal, (2) validação do light budget M03 contra dados M09 e (3) admissão bounded dos parents M06/M09. Os dois primeiros foram integrados com PR protegida, checks verdes e checkpoints próprios.

M06 e M09 acumularam contratos, protótipos, medições reais, bundles de evidência, relatórios reproduzíveis, testes e checkpoints, todos com CI e Sonar verdes. A ausência de admissão formal bloqueava apenas o próximo nível de integração, não a verificação do que já existe.

## Decisão

Admitir **de forma bounded** os pipelines de evidência de M06 (#11) e M09 (#14), com status `BOUNDED_ADMITTED_EVIDENCE_PIPELINE`. A admissão cobre os artefatos verificados abaixo e **não** autoriza integração de runtime, mudanças de renderer/engine, aplicação de presets no hub, cenas de produção ou qualquer claim de qualidade/FPS.

### M06 · admitted scope

- `contracts/m06/performance.v1.schema.json` e `ownership.v1.json`.
- `docs/benchmarks/m06/atlas.v1.json` / `ATLAS.md` (S05).
- `docs/benchmarks/m06/observations/m09-observations.v1.json` e conversor.
- `docs/benchmarks/m06/advisories.v1.json` / `ADVISORIES.md` e builder.
- Testes `tests/contracts/test_m06_performance_contract.py`, `tests/ci/test_m06_atlas.py`, `tests/ci/test_m06_observations.py`, `tests/ci/test_m06_advisories.py`.

### M09 · admitted scope

- `contracts/m09/preset_pack.v1.schema.json` e `ownership.v1.json`.
- `nex_modules/tools/preset_resolver/` (protótipo).
- Harness `nex_bench/scenes/preset_ab/` e presets `ab-low`/`ab-high`.
- Todos os bundles M09 de evidência: preset-ab, preset-scaling, m01-ab, m01-visual, m01-visual-1920, m01-temporal, res-scaling, interaction, cross-scene e interaction-200.
- `docs/benchmarks/m09/**`, incluindo `measurement-atlas.v1.json` e builders.
- Testes M09 associados.

## Exclusões explícitas

- Nenhuma aplicação de preset no hub, `project.godot`, renderer, shaders ou engine.
- Nenhuma mudança em cenas base M01, HUD, input, gameplay ou build nativo.
- Nenhuma generalização de performance/qualidade para outras GPUs, drivers, resoluções, cenas ou sessões.
- Nenhum claim de FPS de jogo, ganho universal ou qualidade visual.
- M01–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- A admissão não relaxa CI, segurança, testes, locks, ruleset, revisão semântica ou squash protegido.
- Trabalho futuro sob M06/M09 continua exigindo Work Order, Context Lock, evidência, testes e checks.

## Condições e gates

1. Cada incremento futuro deve ter WO e Context Lock próprios, com base/HEAD atuais.
2. Aplicam-se os checks obrigatórios e o squash protegido; CI vermelha/pendente bloqueia.
3. Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`; não há aprovação independente fictícia.
4. Expansão para runtime/hub/engine exige nova decisão do Owner, novo ADR/ledger e WO específica.
5. Qualquer claim de performance/qualidade deve citar o bundle, a sessão e as limitações.

## Consequências

- M06 e M09 deixam de ser `NOT_ADMITTED` para o escopo de evidência, permanecendo **não completos** como produtos.
- O próximo passo legal é um incremento bounded sob um desses pipelines ou uma nova decisão de escopo; a admissão não autoriza automaticamente M01–M05/M07–M08/M10–M12.
- O checkpoint registra o novo status e a main SHA de admissão.

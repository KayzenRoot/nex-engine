# NEX-ADR-0008 · Admissão bounded das referências M01/M02

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-14
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `e729774583eb8ce3b75271aea66589bb9e04a587`

## Contexto

M01 (#6) mantém as cenas base e o laboratório visual isométrico; M02 (#7) mantém os contratos e protótipos de câmera, profundidade, sightline, temporal e perfis de render. Ambos acumularam contratos, cenas de referência, protótipos determinísticos, QA, testes e evidência, mas permaneciam `NOT_ADMITTED`. As admissões M03/M06/M09 já estabeleceram o padrão de escopo bounded sem runtime.

## Decisão

Admitir **de forma bounded** M01 (#6) e M02 (#7) como `BOUNDED_ADMITTED_REFERENCE_PIPELINE`. A admissão cobre referências, contratos e análise determinística; **não** autoriza runtime, hub, renderer, shaders, `project.godot`, engine, gameplay, cenas de produção ou claims de performance/qualidade.

### M01 · escopo admitido

- `contracts/m01/**` (scene_manifest, telemetry_run, ownership).
- Cenas base `nex_bench/scenes/base/**` (corridor_static, arena_combat, dense_city) como referência.
- `docs/benchmarks/m01/**` (baseline, budget, deviações, riscos, manifest, tools).
- Testes M01 de baseline, density ladder, câmera isométrica e medições M01.
- Bundles M09 de cenas M01 já admitidos são referência, não re-medidos.

### M02 · escopo admitido

- `contracts/m02/**` (render_core, ownership).
- `nex_modules/render3d/camera/`, `depth_composition/`, `profiles/`, `sightline/`, `temporal/`.
- `docs/benchmarks/m02/**` (QA ledger, contrato, regressão, interface M03/M06).
- Testes M02 de render profiles, câmera, depth composition, sightline e temporal guard.

## Exclusões explícitas

- Nenhum runtime, hub, renderer, shader, `project.godot`, engine, gameplay ou build nativo.
- Nenhuma renderização real, implementação de câmera/render thread ou alteração de cenas.
- `nex_modules/render2d/**` e M07 permanecem fora desta admissão.
- Nenhuma generalização de performance/qualidade ou claim de FPS.
- M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- A admissão não relaxa CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. Cada incremento futuro sob M01/M02 exige WO/Context Lock e todos os checks.
2. Runtime/hub/renderer/shaders exigem nova decisão do Owner, novo ADR/ledger e WO específica.
3. Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. Claims de performance/qualidade devem citar evidência, sessão e limitações.

## Consequências

- M01/M02 deixam de ser `NOT_ADMITTED` para referência/análise, permanecendo **não completos** como produtos.
- O próximo passo legal é um incremento bounded de referência/análise sob M01/M02 ou a preparação de uma admissão de runtime, que exige decisão específica do Owner.
- O checkpoint registra o novo status e a main SHA de admissão.

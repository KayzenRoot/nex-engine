# NEX M03 · Final cinematic-lighting gate

**Status:** `M03_LIGHTING_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-15 · **Base:** `6be39d49d8769ff46a98990c6818c8132e9e5a1d`
**Parent:** #8 · **Sub-issues:** #36 S01, #37 S02, #38 S03, #39 S04, #40 S05, #41 S06, #42 S07, #43 S08.

## O que foi concluído

| Sub-issue | Entrega | Evidência |
|---|---|---|
| #36 CineLight | 3 looks originais de dark fantasy em 3 cenas | `lighting-runtime.v1.json` S01; bundle `...m03-looks` |
| #37 ShadowStability | Low vs ultra, atlas 1024/4096, 4 shadowed torches | S02; bundle `...m03-shadows` |
| #38 GI Atlas | SDFGI on/off e custo | S03; bundle `...m03-gi` |
| #39 FogWeave | Volumetric vs depth vs off | S04; bundle `...m03-fog` |
| #40 LightBridge | API versionada com 2 consumidores mock e 13 checks | S05; `bridge-smoke-2026-11-15.json` |
| #41 LightBudget | 2 vs 4 tochas com sombra | S06; bundle `...m03-budget` |
| #42 R&D | Matriz GO/NO_GO | S07 |
| #43 QA | Este gate e evidência consolidada | `lighting-runtime.v1.json` |

## Resultado

- **CineLight:** 9 capturas 1920×1080 (3 looks × 3 cenas); GPU p95 **3.039–3.129 ms** no corredor.
- **ShadowStability:** low **1.526 ms** → ultra **3.144 ms** (+106.0%); estabilidade temporal `NOT_RUN`.
- **GI Atlas:** off **1.976 ms** → SDFGI **3.140 ms** (+58.9%); alocação **+451.1 MiB**. SDFGI apenas em perfis de qualidade.
- **FogWeave:** depth **3.008 ms** → volumetric **3.145 ms** (+4.6%); fallback de depth fog para Performance.
- **LightBridge:** **13/13 checks** com dois consumidores mock.
- **LightBudget:** 2 vs 4 tochas com sombra, **3.150 ms → 3.020 ms** (-4.1%); MVP baseado em energia, `RESEARCH_MORE`.

## Decisões

- **GO:** CineLight, LightBridge.
- **GO com limitações:** ShadowStability (sem flicker temporal), FogWeave (fallback depth), GI (SDFGI só em qualidade).
- **RESEARCH_MORE:** LightBudget (distância/visibilidade ainda não implementadas).
- **Nenhuma paridade com PoE2 é alegada.** Os looks são originais e usam geometria de referência.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; frames estáticos.
- Cenas são geometria simples de referência, não arte de produção.
- LightmapGI/VoxelGI bake/editor e oclusão dinâmica não foram exercitados.
- Flicker temporal de sombras e legibilidade com telegraphs reais não foram medidos.
- Nenhum claim de FPS, qualidade cross-device ou paridade com PoE2.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, as issues **#36–#43 e #8** podem ser fechadas como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M04** (materiais PBR e shader library), que deve consumir o kit procedural e o baseline de iluminação M03.

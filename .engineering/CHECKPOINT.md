# Checkpoint · NEX Engine

## Current verified scope | 2026-11-13 · M10 combat feedback contract v1

**Contrato M10 v1 integrado** por PR #167, squash `5ad895d5d51bf0858c4873884a0a314b23218847` (código `97c80641`). `contracts/m10/feedback.v1.schema.json` define fases de ataque, hit events, canais (hit-stop, shake, flash, recoil, damage number), prioridade/intensidade, orçamentos de hit-stop/shake/concorrência/total, performance e proveniência. Ownership prospectivo de `nex_modules/animation/**`, docs e **20 testes novos** (suíte de contratos 150 OK; total 501 em worktree LF limpo).

**Parent M10 (#15) continua NOT_ADMITTED.** Nenhuma animação, câmera, shader, cena, engine ou CI alterado; game feel/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M08-COMPOSITION planner prototype

**M08-COMPOSITION integrado como protótipo isolado** por PR #165, squash `8dada408436766009e66fa57830f08b06e99f1bb` (código `0f1cc07f`). Em `nex_modules/render2_5d/composition/`, o planejador determinístico consome `composition.v1`: stack de camadas/entidades críticas, políticas de profundidade/alpha/HUD, ordem de draw por papel, conflitos (alpha sobre crítico, HUD cobrindo gameplay, overrides, riscos do plano 3D) e exportação de observação. **69 asserts headless** e 9 testes estruturais.

**Parent M08 (#13) continua NOT_ADMITTED.** Sem camada/viewport/shader/cena/rendering; alpha-over-critical é aritmético, não pixel coverage; composição visual/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M08 2.5D composition contract v1

**Contrato M08 v1 integrado** por PR #163, squash `5814115e19dbd6d9756482f6c0eabf3a9397da11` (código `53c38b35`). `contracts/m08/composition.v1.schema.json` formaliza o rascunho DepthWeave: referência ao plano 3D, stack de camadas 2.5D, política de profundidade, alpha guard, HUD/overlay safety, entidades críticas, performance e proveniência. Ownership prospectivo de `nex_modules/render2_5d/**`, docs e **20 testes novos** (suíte de contratos 130 OK; total 472 em worktree LF limpo).

**Parent M08 (#13) continua NOT_ADMITTED.** Nenhuma camada, viewport, shader, cena, engine ou CI alterado; performance/visual `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M06 Bottleneck Atlas (S05)

**M06-BOTTLENECK-ATLAS integrado** por PR #159, squash `9f0cd8440de26c660e451ee6a3bda89729aa73cc` (código `99c9fcb4`). Em `docs/benchmarks/m06/`, o builder determinístico recomputa as 15 capturas S05, verifica 32 hashes do bundle, confere os JSONs de validação e gera `atlas.v1.json` + `ATLAS.md` com referências baseline, deltas e classificação no vocabulário `performance.v1`. **12 testes** de estrutura/reprodutibilidade; `--check` detecta artefatos defasados.

**Resultados derivados:** 15/15 runs `pacing` (vsync 60 Hz); GPU p95 máximo **1.194 ms** em `combined-25`; deltas GPU p95 vs baseline-25: lights +54.1%, shadows +154.1%, vfx +30.4%, combined +559.7%; spread baseline-25 **0.002 ms**. Nenhuma captura ou medição nova; não é benchmark, FPS ou generalização. Parent M06 (#11) continua **NOT_ADMITTED**.

**Reparação PR #161** (`3e336b77`): removeu o `.pyc` rastreado e os 14 code smells introduzidos (S9454 ×6, S6353 ×6, S3776, S7500); `atlas.v1.json`/`ATLAS.md` permanecem byte-idênticos e os 12 testes seguem verdes. Sonar main voltou a **23 code smells**, A/A/A.


## Current verified scope | 2026-11-13 · M06 performance contract v1

**Contrato M06 v1 integrado** por PR #157, squash `7e21d7087097de4bcceca6d328d4edfe341e977e` (código `78af311c`). `contracts/m06/performance.v1.schema.json` define workload, frame interval, timings GPU/CPU/pacing, recursos, classificação de gargalo com evidência/confiança e comparação opcional. Ownership prospectivo de atlas/LOD/culling/streaming/framepacer, docs e **17 testes novos** (suíte de contratos 110 OK; total 440 em worktree LF limpo). A cadeia de interfaces M03–M06 está definida.

**Parent M06 (#11) continua NOT_ADMITTED.** Nenhuma captura, medição, benchmark, engine ou CI alterado; nenhum claim de FPS/regressão. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M05-FXBUDGET planner prototype

**M05-FXBUDGET integrado como protótipo isolado** por PR #155, squash `ae134a408b8777a9970acb6f165429bd0d439c38` (código `10ecb58a`). Em `nex_modules/vfx/fxbudget/`, o planejador determinístico consome `spellfx.v1`, valida identidade/fases/emissores/autoridade/light bridge/decal policy, agrega emissores/partículas/GPU/decals e gera planos de redução de partículas e conversão GPU→CPU. **57 asserts headless** e 9 testes estruturais.

**Parent M05 (#10) continua NOT_ADMITTED.** Nenhuma partícula/emissor/luz/decal, cena, engine ou CI; totais aritméticos, conversão não medida; qualidade/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M04-TEXTUREBUDGET planner prototype

**M04-TEXTUREBUDGET integrado como protótipo isolado** por PR #153, squash `253afe6c8dc8efad5060b739425ca45612df8023` (código `658ee86f`). Em `nex_modules/materials/texturebudget/`, o planejador determinístico consome descritores `material.v1`, deduplica por SHA-256, estima bytes decodificados com mips, calcula pressão de atlas, emite achados e gera plano de downscale guloso. **55 asserts headless** e 9 testes estruturais.

**Parent M04 (#9) continua NOT_ADMITTED.** Nenhum decoding/upload/atlas packing, material, shader ou rendering; bytes/tiles são aritméticos, não VRAM; qualidade/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M04/M05 contracts v1

**Contratos M04/M05 integrados** por PR #151, squash `bc404723a77a7941ef0d820a58894021cd3e7c2f` (código `e1d89ade`). `contracts/m04/material.v1.schema.json` define observação PBR (superfície, alpha/cull, variantes, texturas com slot/SHA-256/dimensões, orçamento) e `contracts/m05/spellfx.v1.schema.json` define magias (fases, emissores, gameplay authority, light bridge, decal policy, orçamento FX). Ownership prospectivo, docs e **36 testes novos** (suíte de contratos 93 OK; total 405 em worktree LF limpo).

**Parents M04 (#9) e M05 (#10) continuam NOT_ADMITTED.** Nenhum material, shader, textura, partícula, VFX, cena, engine ou CI alterado; performance/visual `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M03-LIGHTBUDGET arbiter prototype

**M03-LIGHTBUDGET integrado como protótipo isolado** por PR #149, squash `efa7c29766ffa807ee6a793bb790ef7af87e8f9c` (código `26f6ab93`). Em `nex_modules/lighting/budget/`, o árbitro determinístico calibra `nex_light_cost_model.v1` pelas capturas reais S05 (RTX 5050, sessão única, GPU p95 a 25 proxies), projeta custo com breakdown, veredito `FIT`/`TIGHT`/`OVER_BUDGET` e escada de degradação ordenada com `recommended_step`. **57 asserts headless** e 9 testes estruturais.

**Parent M03 (#8) continua NOT_ADMITTED.** Nenhuma captura ou rendering novo; coeficientes não generalizam para outras cenas/hardware; projeção não é frame time nem benchmark. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M03-SHADOWSTAB analyzer prototype

**M03-SHADOWSTAB integrado como protótipo isolado** por PR #147, squash `fa1acb3a6e0f0c01f6551e49b0266d8d584b5ef9` (código `6db0a5ee`). Em `nex_modules/lighting/shadows/`, o analisador determinístico consome `lighting.plan.v1`/`lighting.v1` e reporta splits de cascata, pressão de atlas, heurísticas de bias/softness, orçamento e coerência de casters, com veredictos `STABLE_CONFIG_HEURISTIC`, `STABLE_CONFIG_HEURISTIC_WITH_NOTES`, `RISK_REPRODUCED` ou `INCONCLUSIVE`. **51 asserts headless** e 9 testes estruturais.

**Parent M03 (#8) continua NOT_ADMITTED.** Sem rendering/shadow map/filtro/shader/cena; acne, peter-panning e shimmer **não medidos**; qualidade/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M03-LIGHTRIG light-rig planner prototype

**M03-LIGHTRIG integrado como protótipo isolado** por PR #144, squash `a61df5d2cef2ca8780361b52db09b73ea206fed1` (código `9c252e80`). Em `nex_modules/lighting/light_rig/`, o `LightRigPlanner` cobre ambiente (ambient/tonemap/glow/fog/GI), registro `directional`/`omni`/`spot` com coerência por tipo, orçamento de sombras/cascatas, política determinística de slots e exportação `lighting.v1` com performance `UNAVAILABLE`. **70 asserts headless** e 10 testes estruturais.

**Parent M03 (#8) continua NOT_ADMITTED.** Sem rendering, light/shadow/GI reais, shader ou cena; `estimated_shadow_maps` é estimativa aritmética; performance/qualidade `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M03 lighting contract v1

**Contrato M03 v1 integrado** por PR #142, squash `9c75340d4609df939907ecabea535ffa9b6665c4` (código `38e1d4cb`). `contracts/m03/lighting.v1.schema.json` define ambiente (ambient/tonemap/glow/fog/GI), 1–128 luzes (`directional`/`omni`/`spot`) com bias/softness/cull mask e campos condicionais por tipo, orçamento de sombra, performance com disponibilidade explícita e proveniência. `ownership.v1.json` mapeia paths prospectivos sem admissão implícita; `docs/contracts/m03.md` fixa invariantes. **16 testes novos** (suíte de contratos 57 OK; total 341 em worktree LF limpo).

**Parent M03 (#8) continua NOT_ADMITTED.** Sem implementação de luz/sombra/GI, shader, cena, engine ou CI; performance/qualidade `INCONCLUSIVE_NOT_RUN`. Contratos M01/M02/M07 inalterados. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M07-S01 canvas/batching prototype

**M07-S01 integrado como protótipo isolado** por PR #140, squash `02b24c60750da20d657e8c131a025d4755bc5a52` (código `817cfcfd`). Em `nex_modules/render2d/canvas/`, o planejador determinístico cobre camadas/materiais/luzes/partículas, ordenação por z, batching por material+blend, estimativas de draw calls/state changes e avisos de orçamento, alinhado ao contrato `render2d.v1`. **46 asserts headless** e 8 testes estruturais.

**Parent M07 (#12) continua NOT_ADMITTED.** Sem rendering/shaders/2.5D/engine; draw calls são estimativa determinística; performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta. A autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M02-S07 QA/integration gate

**M02-S07 integrado** por PR #138, squash `c2bed9581719b0e1b7c930d9bc06f017c4a3f6d2`. O QA pack em `docs/benchmarks/m02/` versiona o contrato de QA, um ledger hasheado de S01–S06 e a interface M03–M06. **Structural PASS** nos 6 componentes; **comparação de cena e performance `INCONCLUSIVE_NOT_RUN`** — as 3 cenas M01 não foram executadas com as melhorias; metas 1080p60/120 permanecem não medidas. Defeitos HIGH/CRITICAL: 0; integração serial sem conflitos; nenhum claim medido.

**Parent M02 (#7) continua NOT_ADMITTED.** Próximas ações: Owner decide as hipóteses do atlas; A/B/A real nas 3 cenas exige WO própria; M03–M06 consomem a interface com evidência própria. Nenhum checkpoint é promovido por este delta.


## Current verified scope | 2026-11-13 · M02-S06 R&D decision atlas

**M02-S06 integrado como pesquisa/planejamento** por PR #135, squash `23deddb50259850dc243c37c7f09b786d6a3a2de`; limpeza de bytecode gerado na PR #136 (`4ce2b7f3`). O atlas em `docs/research/nex-m02/` traz 5 hipóteses refutáveis (IsoDirector, Sightline, DepthWeave, TemporalGuard, RenderPassport) com gap nativo, alternativa simples, contrato de dados, custo/risco, compatibilidade 2.5D, rollback e A/B/A. O motor determinístico recomenda **4× RESEARCH_MORE** (features sem gap medido) e **1× GO** (RenderPassport como ferramenta de processo); **5 redundâncias** são `NO_GO`. Contratos C1–C4 são `DRAFT_NOT_PROMOTED`.

**Todas as decisões do Owner permanecem PENDING.** Nenhuma implementação, shader, addon, compositor, 2.5D, contrato promovido ou alteração de engine/CI/`project.godot`. Parent M02 (#7) continua **NOT_ADMITTED**; M02-S07 (QA/integração) permanece não admitido.


## Current verified scope | 2026-11-13 · M02-S05 RenderPassport prototype

**M02-S05 integrado como protótipo isolado** por PR #133, squash `043a0124a803753a8521f397d7d3f1d370cba630` (código `2613f51d`). Em `nex_modules/render3d/profiles/`, a matriz de 9 capacidades com fontes oficiais, o RenderPassport (inventário + probe runtime + fallback Vulkan→D3D12→GL) e os perfis Quality/Balanced/Performance reversíveis foram verificados com **87 asserts headless** e 9 testes estruturais. Flags explícitas: sem escrita de `project.godot`, sem coleta remota, GPU não implica capacidade.

**Parent M02 (#7) continua NOT_ADMITTED.** Estados de capacidade são documentação-derivados e `INCONCLUSIVE_NOT_PROBED` sem probe; nenhum claim de FPS/VRAM. M02-S06 (R&D 3D) ou S07 (QA/integração) podem consumir o passport como mock sob WO própria. M03–M12 seguem sem admissão.


## Current verified scope | 2026-11-13 · M02-S04 TemporalGuard prototype

**M02-S04 integrado como protótipo isolado** por PR #131, squash `fae4f9a88e352709ca6ccab7b0d377cd6adacb66` (código `9a1bdde1`). Em `nex_modules/render3d/temporal/`, o analisador determinístico cobre ghosting, flicker, shimmer, render scale e sharpness, emitindo `BASELINE_ACCEPTABLE` / `DEFECT_REPRODUCED` / `INCONCLUSIVE` e ações `KEEP_NATIVE` / `EVALUATE_COMPOSITOR` / `NO_GO`, com toggle de postprocess guardado e rollback. **51 asserts headless** e 8 testes estruturais.

**Decisão de risco ELEVATED registrada:** análise/gate apenas; sem render thread, CompositorEffect, shader ou renderer core; nenhuma operação irreversível. Qualidade temporal real é `INCONCLUSIVE_NOT_RUN`; compositor/render-thread exigem WO separada do Owner e ABI review. Parent M02 (#7) continua **NOT_ADMITTED**; M02-S05 pode consumir o gate como mock sob WO própria. M03–M12 seguem sem admissão.


## Current verified scope | 2026-11-13 · M02-S03 DepthWeave prototype

**M02-S03 integrado como protótipo isolado** por PR #129, squash `9adc0e68b3f2b3f3c5508ac2557a134455d3f0b8` (código `68378db6`). O planejador em `nex_modules/render3d/depth_composition/` cobre passes opaco/alfa/overlay, riscos de Z-fighting, histerese contra flicker, conflitos alfa×crítico e overlay×gameplay, com **37 asserts headless** e 8 testes estruturais. Draft de contrato M08 2.5D anexado como `DRAFT_NOT_PROMOTED`.

`Visual/edge/aliasing/frame-time = INCONCLUSIVE_NOT_RUN` (sem rendering). Parent M02 (#7) continua **NOT_ADMITTED**; M02-S04 (TemporalGuard) pode consumir o plano/histerese com mocks sob WO própria. M03–M12 seguem sem admissão.


## Current verified scope | 2026-11-13 · M02-S02 Sightline prototype

**M02-S02 integrado como protótipo isolado** por PR #127, squash `6b4ba4d5ccdc50bdcb0b825c4571058bbb81a0d6` (código `6057c1da`). O controlador Sightline em `nex_modules/render3d/sightline/` implementa oclusão por AABB, prioridades jogador→ameaça→decoração, fade/silhueta com histerese, cap de reveals, visibilidade de gameplay separada da legibilidade visual e alerta de ameaça bloqueada. **49 asserts headless** e 9 testes estruturais.

`Performance/frame-time/VRAM = INCONCLUSIVE_NOT_RUN` (sem rendering; cenas reais não executadas; AABBs mock). Parent M02 (#7) continua **NOT_ADMITTED**; M02-S03 (DepthWeave) pode consumir a API com mocks sob WO própria. M03–M12 seguem sem admissão.


## Current verified scope | 2026-11-13 · M02-S01 camera prototype

**M02-S01 integrado como protótipo isolado** por PR #125, squash `9fea0f384f933b7619f0bd68b3b1f28747a1b9f7` (código `9f8d4ce`). O rig isométrico determinístico vive em `nex_modules/render3d/camera/` (perspectiva inclinada e ortográfica, dead zone, bounds, zoom, sincronização mundo↔tela, enquadramento por aspect e replay), com **32 asserts headless** e 10 testes estruturais. O estado segue o contrato `render_core.v1`; **nenhuma integração no engine** foi feita.

`Performance/FPS A/B = INCONCLUSIVE_NOT_RUN` (sem mudança de rendering). Parent M02 (#7) continua **NOT_ADMITTED**; S02/S03 (Sightline/DepthWeave) podem consumir a API com mocks, mas exigem WO própria e admissão do Owner. M03–M12 permanecem sem admissão.


## Current verified scope | 2026-11-13 · M01 baseline audit pack (S07)

**S07 integrado** por PR #123, squash `ed72f90e341c9e0d1dc136354ea4d8f53ce2f583`. O audit pack em `docs/benchmarks/m01/` congela o baseline M01 como **instrumento verificável**: manifesto de 71 artefatos com SHA-256 de blobs Git (`build_manifest.py --check` → `MANIFEST_OK`), baseline, orçamento **proposto**, riscos, desvios, links de CI e insumos de pesquisa.

O orçamento de performance é `PROPOSED_PENDING_OWNER_APPROVAL`; metas 1080p60/120 permanecem `ASPIRATIONAL_NOT_MEASURED`. O Checkpoint Delta do S07 é **proposto, não promovido**. O parent M01 continua **NOT_ADMITTED**; M02–M12 seguem sem admissão de implementação. A correção `QA-FINDING-001` está integrada (PR #122). Próximo passo legal: admissão explícita do Owner para M02-S01 (câmera isométrica) ou outra Work Order.


## Current verified scope | 2026-11-13 · NEX-WAVE-001 (six fronts integrated)

Onda paralela admitida pelo Owner (PR #114, `3653a1b`) e executada sob `ADMIN_SOLO / NOT_INDEPENDENT` (NEX-ADR-0004 / NEX-D-014). Seis frentes independentes integradas por squash protegido, cada uma com checks verdes e evidência própria:

- **M01-S05** (#25, PR #120) — estação de medição Lighting Matrix (5 presets nativos × 25/100/200 proxies), código medido `0b8388faba69358027780a2cc0ea73d3449eab6d`; capturas COMPLETE validadas pelo validador S05 (proveniência Lighting Matrix + delegação ao canônico S04). **Não é benchmark nem admissão do parent M01.**
- **M01-S06** (#26, PR #119) — Radar R&D com 10 candidatos, hipóteses e critérios GO/NO_GO; sem medições inventadas.
- **QA Audit** (#20, PR #117) — 67 casos de robustez, 0 aceitações indevidas; achado `QA-FINDING-001` (LOW, aberto) em `framepulse`.
- **M12-S01** (#17, PR #118) — brand master provisório (SVG, paleta, ícones); sem integração com engine.
- **Contrato M02** (#7, PR #115) — `render_core.v1` e ownership prospectivo; contrato apenas.
- **Contrato M07** (#12, PR #116) — `render2d.v1` e ownership prospectivo; contrato apenas.

Main observada: `9f44b73e7fe9cc71983bb399a30fd01e83807677`. S07 (#27) passa a ter seus pré-requisitos técnicos (S01–S06), mas permanece **NOT_ADMITTED** até admissão explícita do Owner. M01 parent, S07 e M02–M12 continuam sem admissão de implementação.


## Current verified scope | 2026-11-13 · ADMIN_SOLO security correction

Desenvolvimento sob **NEX-ADR-0004 / NEX-D-014** (`ADMIN_SOLO / NOT_INDEPENDENT`; nenhum revisor humano externo exigido). NEX-GOV-SOLO-WO-001 (#108) promovido por PR #109 em `47f95521821f71196ec54c8d74b20fa9c3a2a4a5`.

M01-S04 GPU Profiler integrado por PR #107 em `4d69b7bd264f4814317c6e5fe98eaccdc2b620e0`, com correção de importação de evidências na PR #110 (`71d6750fc63a7ff2431bc77aada9f1330016d2de`). Matriz física RTX 5050: **12/12 COMPLETE** no código medido `d59c94da13839ba1c6c2e894d4d1147ff3fddc78`; limitações documentadas: resize-negative não exercitável sob `canvas_items` e pacing não comparável entre sessões de ~75 e ~60 callbacks/s. Isso **não** admite o parent M01 #6 nem M02–M12.

O **Security Rating C** do SonarCloud na main (3 vulnerabilidades MAJOR em `tooling/godot/ci_build.py`: `pythonsecurity:S5144` SSRF e `pythonsecurity:S6350` ×2 command argument injection) foi corrigido na PR #112, squash `0d8e562fa63d291b910f4f9756eb04ac52ffebd1`. HEAD exato `ee717eab47f6d00f18e87fedad1c1a3d17e8d220` com **16/16 checks SUCCESS**, incluindo build nativo Windows e smoke Ubuntu oficiais; análise Sonar do PR: **0 novas vulnerabilidades / new_security_rating A**; pós-merge na main: `security_rating=1.0`, `vulnerabilities=0`. Sem supressão, sem alteração de quality gate, workflow ou ruleset. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

M00 baseline, contracts e S02 permanecem verificados conforme o histórico abaixo. M01 parent, S01, S05+ e M02–M12 permanecem **NOT_ADMITTED**.


## Current verified scope | Stage B proposed checkpoint reconciliation (2026-10-12)

Contracts v1 #19 are **integrated** via protected [PR #93](https://github.com/KayzenRoot/nex-engine/pull/93), main `60c826e41aac061bcdee72e4f793508c661de933`. S02 synthetic-only FramePulse #22 is **integrated** via protected [PR #95](https://github.com/KayzenRoot/nex-engine/pull/95), main `ef20ad4e03e3fd588ec6f6386fd88ce45e1dd6cd`, identical reviewed Git tree `ee8d5695c1cc94416aa155e19dbfd776b710645c`, 10/10 postmerge checks and 5/5 workflows successful. Stage A governance lock PR #97 promoted to `6192ebb0e77e5e706466ab25e438955efad35f37`, 37/37 pins valid. [S02 attestation](https://github.com/KayzenRoot/nex-engine/issues/22#issuecomment-6127892436), [contracts audit](https://github.com/KayzenRoot/nex-engine/issues/19#issuecomment-6124229771).

**M00 remains verified; M01 parent #6, S01 #21 and other modules remain NOT_ADMITTED/NOT_STARTED.** Synthetic FramePulse is `SYNTHETIC_NOT_MEASURED`, NOT real FPS/GPU/VRAM profiling. Its 31 local tests were Codex-reported, not independently replayed; required CI does not execute `tests/telemetry`/`tests/contracts` (QA #20); Sonar new-code instrumented coverage was reported 0%. Existing `mainObservedSha` is a historical authority snapshot, not a live runtime main SHA. This Stage B update becomes canonical only after **separate Owner exact-head squash consent and postmerge audit**. Historical content below is deliberately retained, but superseded for current-state labels by these verified facts.

Status: **M00_BASELINE_VERIFIED**, protected checkpoint PR #79 merged as `2090cb28df2385b995666c8fc4d3015e11f6c407`; exact reviewed Git tree equality and 6/6 post-merge checks verified. This Source Pack revision corrects the five historical M00 status contradictions in Issue #81; its canonical effect requires protected promotion and postmerge verification. **M01 NOT_ADMITTED and NOT_STARTED.**

## Authority and preserved history
- Source Pack planning PR #2 squash `a238f610f0c1bfc2e45b33b38c45dec2ab39ca3c`; governance PR #72 squash `55f92d1942e810e75aac6faf8231427a6b11c346`; protection PR #73 squash `bd2b0073dc8121290c696647e9c631cadc83c881`.
- Active GitHub Ruleset #24864413 requires protected PR/squash, exact checks, resolved threads and no bypass. ChatGPT self-review is NOT_INDEPENDENT.
- GEF 1.1.2 Bootstrap implemented by PR #74, squash `570d0671ed57f5cd29932baf0bac26345efca279`; checkpoint promotion PR #75 and exact-head/post-merge Windows+Ubuntu GEF, Governance, Sonar, Socket, CodeRabbit all verified.
- GEF prior `npm audit signatures` E404 remains INCONCLUSIVE; GEF doctor security.dependency/security.github are REVIEW, not PASS.

## M00 Godot native desktop baseline · VERIFIED
- Owner approved M00 in Issue #5, execution governance PR #76 squash `10054a2d7038b2677bc00fa9279a754e08adc5fb`, execution-lock PR #77 squash `c4174573086df365aadc72967e4722b2cbe6f3ac`, 21/21 authority-base fingerprints and promoted delta verified.
- M00 implementation [PR #78](https://github.com/KayzenRoot/nex-engine/pull/78) reviewed at HEAD `8c26ecc019b05edef5839f21c43b4af72bb34d9c`, squash merged into `main` as `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861` with expected parent `c4174573086df365aadc72967e4722b2cbe6f3ac`.
- Exact reviewed PR tree and merged `main` tree are IDENTICAL: `fedcac4bfbc06dce2d21aa3d5d6ce4a19826fdac`; GitHub comparison shows exactly eight allowed M00 files and zero extras. Owner explicitly accepted the Git-tree proof for postmerge verification.
- Official unmodified Godot `4.7.2-stable`, upstream commit `ed1daf0bf001b61586d9930840f2f1394092c079`, source archive SHA-256 `a18ce0ccec3ecc40b0dd6c4f5132ca934e9fb7c2979717940ff32aee1eb35481`, required third-party notices and dependencies verified.
- [Exact-head M00 CI](https://github.com/KayzenRoot/nex-engine/actions/runs/38175760924): native MSVC/SCons Windows source build exit 0 (~5236s), verified editor/console binaries and Windows smokes, Ubuntu headless smokes, negative tests. Local Python suite 17/17 PASS; CodeRabbit SUCCESS, 10/10 HEAD checks SUCCESS, no unresolved review threads.
- CD-003: 5/5 fresh-user-data and 5/5 warm-user-data Windows editor starts exited 0 with zero reproduced crashes. Historical `0xC0000005` root cause UNKNOWN, explicitly accepted as residual risk by Owner. Raw local logs and indices preserved, NOT independently read byte-for-byte by ChatGPT.
- [Actual post-merge GEF Windows/Ubuntu](https://github.com/KayzenRoot/nex-engine/actions/runs/38185193893) and [Governance Source Pack/PowerShell](https://github.com/KayzenRoot/nex-engine/actions/runs/38185193916) SUCCESS, plus SonarCloud and Socket Project Report: **6/6** checks on `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`.
- At the time of M00 source and checkpoint validation, the native workflow triggered on pull_request; **NO** additional native Windows source build is claimed on the squash commit. Exact reviewed-tree equivalence binds validated PR evidence to identical integrated content. Workflow updates in separate Fast Lane PR #83 are not retroactive M00 verification.
- Full [post-merge evidence](evidence/NEX-M00-WO-001-POSTMERGE-EVIDENCE.md) and [Issue #5 audit](https://github.com/KayzenRoot/nex-engine/issues/5#issuecomment-6115221416).

## Boundaries / Next legal action
- M00 verified is only a **native Godot baseline**; it is not a finished NEX Engine release, custom renderer, playable game or performance benchmark. The engine-wide DoD/completion percentage remains NOT_BASELINED.
- M01, NexLabs Flow, renderer/game development and M02–M12 remain NOT_ADMITTED. A separate Owner-approved M01 Work Order, contracts and fresh Context Lock are required; **do not execute M01 automatically**.
- Checkpoint PR #79 has completed exact-head CI/CodeRabbit, Owner-authorized protected squash and six post-merge main checks. Fast Lane PR #83 was squash merged as `a14de0c2f2c94e2c4a7a444e7a7fd777ca2a5a56` with exact Git tree, but its first postmerge batch sentinel failed and is separately tracked by Issue #85. The batch sentinel was corrected in PR #86 (protected squash `ef401a3cfc1571804a529ef576dcc7494ad394c6`), with all six applicable postmerge main checks SUCCESS and real native batch sentinel [run #38227526228](https://github.com/KayzenRoot/nex-engine/actions/runs/38227526228) SUCCESS at zero accepted modules, without a new Windows Godot build. Fast Lane migration PR #90 protected-squash merged as `84063a0f7e4b216e0787b6c458408367067d40e7`: SonarCloud, Socket x2, Governance, NEX Free Review / Static and Fast Lane plus the postmerge native batch sentinel passed. Live ruleset #24864413 is active, no bypass, squash-only, now requires six deterministic/free gates and does NOT require CodeRabbit. This proposed consolidated documentation revision closes issues #81/#87/#89 only AFTER its own protected merge and postmerge audit. M01 remains NOT_ADMITTED and needs its own new Work Order, frozen contracts and Context Lock.

## NEX-CONTRACT-WO-001 Owner scope admission (promotion and attestation are separate gates)
- Owner approved bounded six-file contracts-only WO #19 on 2026-10-12; [record](https://github.com/KayzenRoot/nex-engine/issues/19#issuecomment-6122906159). **Approval of scope is NOT an active execution lock.**
- Governance lock `.engineering/context-locks/NEX-CONTRACT-WO-001-EXECUTION.json` stores protected authority base `d0f148f324d714fb064e3da5e19854d6be5454c8` plus exact canonical Git blob fingerprints; proposed promotion requires its own protected merge/postmerge audit and Issue #19 actual new-main SHA attestation, then Steward lease before Codex Desktop LOCAL may implement the six contracts.
- The `mainObservedSha` field is a HISTORICAL authority snapshot, not runtime execution SHA. Do not execute with a guessed future squash SHA. Existing M00 evidence, Fast Lane and free review unchanged.
- **M01 remains NOT_ADMITTED / NOT_STARTED**; no M01 agent dispatch or benchmark.

## S02 synthetic-only child approval | execution lock promotion pending
Owner separately authorized S02 FOUR-file synthetic FramePulse scope [Issue #22](https://github.com/KayzenRoot/nex-engine/issues/22#issuecomment-6124456702). Lock proposal `.engineering/context-locks/NEX-M01-S02-WO-001-EXECUTION.json` is based on protected main `60c826e41aac061bcdee72e4f793508c661de933` with 28 real Git blob fingerprints. Exact four implementation paths: `nex_bench/telemetry/framepulse.py`, `nex_bench/telemetry/fixtures/synthetic_run.v1.json`, `tests/telemetry/test_framepulse.py`, `nex_bench/telemetry/README.md`.
Execution forbidden until protected lock promotion/complete postmerge audit/actual runtime main SHA attestation and exclusive local Integration Steward Windows lease. M01 parent and S01/other modules stay NOT_ADMITTED / NOT_STARTED. Neither this governance PR nor the owner scope permission authorizes an implementation merge.

# Checkpoint · NEX Engine

## Current verified scope | 2026-11-17 · reference build Windows x86_64

**Reference build concluído** por PR #301, squash `8a23e418f251cca167cc611f439ce5c96db1ed0f`, sob `NEX-ADR-0024` / `NEX-D-035`, bounded ao visual lab unificado. O build gera **`build/NEXEngine.exe`** de **109522728 bytes** com Godot 4.7.2-stable e templates oficiais, usando staging que remove os `project.godot` aninhados e os entry points standalone.

**Resultado:** smoke staged **PASS**; export release **PASS**; executável headless **PASS**; GUI **PASS** com **5 capturas 1296×759** (corridor, arena, dense city, density ladder, diagnostics). O diagnóstico observou **Forward+ / Vulkan**, **RTX 5050**, 60 FPS observado (não benchmark), 28 draw calls, 766 objetos 3D e 88.0 MiB de renderer allocation. O artefato **não é versionado**; `build/` é ignorado e o build é reproduzível com `python scripts/build_reference_export.py --build --gui`. A issue **#300** foi fechada como `COMPLETED` após squash protegido e **14/14 checks pós-merge SUCCESS**. **Nenhuma paridade com PoE2 é alegada**; não há installer, code signing, distribuição, alteração de engine/renderer, claim de FPS/qualidade ou aprovação de marca. Distribuição/trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-17 · M12 brand system complete

**M12 finalizado** por PR #297, squash `0bc10ef448af46c00bf22f1e3782beca7a1621eb`, sob `NEX-ADR-0023` / `NEX-D-034`, bounded ao sistema de marca de referência. O wordmark NEX ENGINE agora usa **paths outline sem dependência de fonte**, a paleta tem **5 tokens canônicos**, os app icons têm **9 PNGs + ICO + ICNS**, os UI icons são **10** e o `identity.v1` foi validado com **14 checks** e veredito **READY_FOR_UI**.

**Resultado:** Mist/Graphite **16.48:1**; Cobalt/Graphite **4.27:1**; Cyan **10.63:1**; Amber **10.51:1**; ICO **47845 bytes**; ICNS **45394 bytes**; **0 findings**. A issue **#17** foi fechada como `COMPLETED` após squash protegido e **11/12 checks pós-merge SUCCESS**; o **Socket Project Report** retornou `neutral` por erro externo do serviço, sem mudança de código ou dependências, e os demais checks obrigatórios passaram. **Nenhuma paridade com PoE2 é alegada**; M12 é o décimo segundo módulo base concluído como **sistema de marca de referência**, não como rebranding da engine. Nenhuma integração com editor UI, launcher, installer, hub, renderer ou binário é admitida; distribuição e trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-17 · M11 asset pipeline complete

**M11 finalizado** por PR #295, squash `5793dcf52a94f2520ccc55e0a27438d3c6a2788e`, sob `NEX-ADR-0022` / `NEX-D-033`. O pipeline de assets agora tem **AssetPipelineAuditor com 43 checks**, **AssetManifest**, **CookPlanner**, **LicenseLedger**, **AssetQualityGate**, **3 fixtures** e **39 checks** no smoke.

**Resultado:** AssetManifest **8 assets / 2 errors / 2 warns / 270592 bytes**; CookPlanner **5 accepted / 1 rejected / 1 noop / 1 conflict** sem escrita; LicenseLedger **2 third-party / 1 unverified / 2 rejected / 2 attribution** com veredito **BLOCKED**; AssetQualityGate **0 errors / 5 warns / 2 info** com **REVIEW_REQUIRED**; kit audit **12 assets / 0 failed stages**. A issue **#16** foi fechada como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M11 é o décimo primeiro módulo base concluído como **pipeline de assets de referência**, não como jogo. M12 continua bounded e dependente de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-17 · M10 animation and feedback complete

**M10 finalizado** por PR #292, squash `335516041a94b8e04e62fd5990975fdf65846509`, sob `NEX-ADR-0021` / `NEX-D-032`. O módulo de animação agora tem **FeedbackPlanner com 66 checks**, **9 runs nativos**, **9 capturas** e laboratório com AnimationPlayer/AnimationTree blending, hit reaction, hit-stop visual, câmera suave, sincronização M05 VFX e perfis low/high.

**Resultado:** baseline GPU p95 **0.256 ms**; blend **0.264 ms** (+3.13%, 0.493% de pixels); attack **0.256 ms** (0.931%); hit **0.256 ms** (0.414%); hit-stop **0.255 ms** com **0.000%** de pose vs attack; camera **0.273 ms** (+6.64%, 2.661%); vfx **0.262 ms** (+2.34%, 3.681%); quality low/high **0.264/0.274 ms**. A issue **#15** foi fechada como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M10 é o décimo módulo base concluído como **animação e feedback de referência**, não como jogo. M11–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-17 · M09 editor tools complete

**M09 finalizado** por PR #290, squash `818759d5e6daaa3d3f9be922331b0d39d5cd4f5c`, sob `NEX-ADR-0020` / `NEX-D-031`. O módulo de ferramentas agora tem **PresetResolver com 50 checks**, **PerfLint com 42 checks e 13 findings**, **ImportGuard** com plano determinístico sem escrita, **BenchmarkRecipe** reproduzível, **4 fixtures** e relatório/gate.

**Resultado:** PerfLint reporta **13 findings** (4 errors, 9 warns) em 12 códigos; ImportGuard planeja **1 accepted / 3 rejected / 2 noop / 1 conflict**; BenchmarkRecipe gera `m09-corridor_static-ab-high-4101` com driver vulkan e 3 runs; total **92 checks** e **0 assets de terceiros**. A issue **#14** foi fechada como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M09 é o nono módulo base concluído como **ferramentas de editor de referência**, não como jogo. M10–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-16 · M08 2.5D composition complete

**M08 finalizado** por PR #287, squash `cd3f1cc92ac47e2eff6dc15c1490ee6422aa9740`, sob `NEX-ADR-0019` / `NEX-D-030`. O módulo 2.5D agora tem **CompositionPlanner com 69 checks**, **9 runs nativos**, **9 capturas** e laboratório híbrido com câmera ortográfica/perspectiva, Sprite3D billboards, sorting, sombras 3D, overlay 2D e perfis low/high.

**Resultado:** baseline GPU p95 **0.390 ms**; sprites **0.400 ms** (+2.56%, 6.463% de pixels); sorted **0.401 ms** com **0.000%** de diferença vs sprites → sorter customizado **NO_GO**; shadows **0.498 ms** (+27.69%, 15.477% de pixels); overlay **0.411 ms** (+5.38%, 22.789% de pixels); hybrid **0.508 ms** (+30.26%, 31.714% de pixels); perspective **0.332 ms** (-14.87% vs ortho); quality low/high **0.397/0.497 ms**. A issue **#13** foi fechada como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M08 é o oitavo módulo base concluído como **composição 2.5D de referência**, não como jogo. M09–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-16 · M07 render2d reference complete

**M07 finalizado** por PR #285, squash `79521ad3c41b1cae374ef9ffb3227838b9a14795`, sob `NEX-ADR-0018` / `NEX-D-029`. O módulo 2D agora tem **CanvasPlanner com 46 checks**, **9 runs nativos**, **9 capturas** e laboratório para luzes, sombras, normal maps, partículas, parallax e perfis low/medium/high.

**Resultado:** baseline GPU p95 **0.060 ms**; lighting **0.075 ms** (+25.00%, 16.218% de pixels); shadows **0.100 ms** (9.028% vs lighting); normal maps **0.082 ms** (14.542% vs lighting); particles **0.071 ms** (0.979% de pixels); parallax **0.070 ms** (23.006% de pixels); quality low/medium/high **0.065/0.081/0.153 ms**. A issue **#12** foi fechada como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M07 é o sétimo módulo base concluído como **render2d de referência**, não como jogo. M08–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-16 · M06 performance reference complete

**M06 finalizado** por PR #282, squash `aa6256a82f6cd34e347b05ac43375ac4042d2ede`, sob `NEX-ADR-0017` / `NEX-D-028`. O módulo de performance agora tem **33 runs nativos**, **27 capturas**, **3 smokes** (`78 + 17 + 9` checks) e laboratório para BatchWeave, LOD Governor, Occlusion Mapper, StreamGuard, FramePacer, VRAM Sentinel e FillRate X-Ray.

**Resultado:** MultiMesh reduz draw calls **385→223** no corredor com **0.000%** de diferença visual; LOD Governor reduz GPU p95 **8.17%/7.10%/1.00%** com **3.458%/4.314%/0.967%** de pixels; render scale 0.85/0.70 reduz GPU **15.41%/28.23%**; 22 texturas adicionam **198.9 MB** de engine video memory; 1440p custa **+135.9%** vs 720p em 1 evento. O mapper de frustum customizado é **NO_GO** e a oclusão baked permanece `INCONCLUSIVE_NOT_BAKED`. As issues **#59–#68 e #11** foram fechadas como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M06 é o sexto módulo base concluído como **performance de referência**, não como jogo. M07–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-16 · M05 VFX reference complete

**M05 finalizado** por PR #280, squash `80a31160da74340c2250170af63a778ff0b73f5c`, sob `NEX-ADR-0016` / `NEX-D-027`. O módulo de VFX agora tem **SpellFX `spellfx.v1`** com 12 checks, **seis efeitos elementais originais**, integração com LightBridge M03, **19 capturas** nativas 1920×1080, **3 baselines**, **9 runs de stress** (1/25/100 eventos) e **3 runs baseline**.

**Resultado:** 25 eventos com 8 luzes alteram **28.055%** do frame da arena; GPU p95 **3.620/3.839/3.992 ms** e 1% low **220.73/221.40/104.48 FPS** para 1/25/100 eventos; baseline **3.210 ms / 219.73 FPS**. As issues **#52–#58 e #10** foram fechadas como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M05 é o quinto módulo base concluído como **VFX de referência**, não como jogo. Não há hit autoritativo, física de projétil, colisão, telegraphs, redução de flashes ou ThreatBudget. M06–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M04 materials reference complete

**M04 finalizado** por PR #278, squash `110e35834c51cd625b2e01d9584ff607c875cd40`, sob `NEX-ADR-0015` / `NEX-D-026`. O módulo de materiais agora tem **8 materiais PBR originais**, **24 texturas 256×256**, galeria nativa 1920×1080, shader triplanar/wet, Decal3D e escala 1K/2K/4K.

**Resultado:** triplanar on/off **3.102%** de pixels (PSNR 33.618 dB); Decal3D **4.286%** de pixels com API **12/12 checks**; scaling 1K **4.2/5.6 MB**, 2K **16.8/22.4 MB**, 4K albedo **67.1/89.5 MB**. As issues **#44–#51 e #9** foram fechadas como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M04 é o quarto módulo base concluído como **materiais de referência**, não como jogo. M05–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M03 cinematic lighting complete

**M03 finalizado** por PR #276, squash `19c1542c12385b370e045d766d650bdddce5f623`, sob `NEX-ADR-0014` / `NEX-D-025`. A iluminação de referência tem **3 looks originais de dark fantasy**, **36 capturas** nativas, **11 runs** de performance e **13 checks** de LightBridge.

**Resultado:** CineLight GPU p95 **3.039–3.129 ms**; ShadowStability low **1.526 ms** → ultra **3.144 ms** (+106.0%); SDFGI off **1.976 ms** → on **3.140 ms** (+58.9%, +451.1 MiB); FogWeave depth **3.008 ms** → volumetric **3.145 ms** (+4.6%); LightBudget 4→2 tochas **3.150 → 3.020 ms** (-4.1%). SDFGI restrito a qualidade; volumetric fog com fallback depth; LightBudget `RESEARCH_MORE`. As issues **#36–#43 e #8** foram fechadas como `COMPLETED`. **Nenhuma paridade com PoE2 é alegada**; M03 é o terceiro módulo base concluído como **iluminação de referência**, não como jogo. M04–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M02 reference renderer complete

**M02 finalizado** por PR #274, squash `f95f7b00a6b73671d71bf1d79923e6e4c07533c5`, sob `NEX-ADR-0013` / `NEX-D-023`. O renderer de referência agora tem **27 runs nativos** validados, câmera com 4 aspect ratios, sightline renderizado, overlay de profundidade, TAA nativo off/on e perfis quality/balanced/performance.

**Resultado:** S01 round-trip **3e-6 m** e fast follow **24.325 px**; S02 reveal **0→1** com GPU delta **+6.0–8.6%**; S03 overlay com **0 conflitos** e GPU delta **+0.0–3.3%**; S04 TAA nativo off/on com métricas idênticas e compositor customizado **NO_GO**; S05 passport **RUNTIME_PROBED** e GPU p95 **0.758/0.571/0.182 ms**. QA ledger S01/S02/S03/S05 `PASS`+`MEASURED`; S04 `PASS`+`INCONCLUSIVE_NOT_RUN`. As issues **#28–#34 e #7** foram fechadas como `COMPLETED`. M02 é o segundo módulo base concluído como **renderer de referência**, não como jogo. M03–M12 continuam bounded; M12 depende de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M01 reference lab complete

**M01 finalizado** por PR #272, squash `7b2c497c37ba9fc8078b0a894e04c9e27c3828fb`, sob `NEX-ADR-0012` / `NEX-D-022`. O laboratório de referência agora tem **18 capturas nativas 1920×1080** (3 cenas × 2 presets × 3 repetições) com A/A byte-idêntico, A/B full + 5 regiões e **9 runs de performance 1080p** validados 9/9.

**Resultado:** GPU p95 **0.139/0.151/0.122 ms**; CPU p95 **0.395/0.382/0.363 ms**; pacing p95 **4.273/4.291/4.255 ms**; 1% low **223.26/224.27/223.76 FPS**. Budget 1080p **`OWNER_APPROVED`**; meta experimental 120 FPS medida no workload de referência. `LICENSE-AUDIT.md` registra **0 assets de terceiros**. As issues **#21, #23, #27 e #6** foram fechadas como `COMPLETED`; #22/#24/#25/#26 já estavam concluídas. M01 é o primeiro módulo base concluído **como laboratório de referência**, não como jogo. M02–M12 continuam bounded e exigem WO própria para rendering/runtime; M12 continua dependente de aprovação de marca. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · Evidence checksum validator

**Validador global de evidência** por PR #270, squash `1dc2c7ca96847cb9d405c2836d1728576423093e`. O `validate_evidence.py --check` verifica **27 bundles / 803 entradas** de `SHA256SUMS.txt`, aceitando variantes LF/CRLF de bundles históricos e resolvendo caminhos relativos ao bundle ou à raiz.

**Resultado:** **1 divergência histórica real** encontrada e corrigida de forma transparente: `GPU-DEVICE-SNAPSHOT.txt` (`ad93615…` → `f3488105…`), com `CORRECTION.md` no bundle; os bytes da evidência não foram alterados. `EVIDENCE_SUMS_OK` após a correção; 7 testes do validador e **627 testes CI OK**; terceiro validador cross-module no Fast Lane. O checkpoint M08 teve um `HTTP 500` transitório da API no `NEX Native Batch` e passou no re-run; todos os checks pós-merge ficaram SUCCESS. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M08 scene composition

**Composição 2.5D M08** por PR #268, squash `7549ad3bb588349969a92e08255f84ced2e17bc1`. O `CompositionPlanner` integrado planejou **quatro camadas** (`background`, `gameplay`, `foreground`, `hud`) com entidades críticas `player`/`threat` para as três cenas M01, a partir da análise M02.

**Resultado:** `corridor_static` **`SAFE_CONFIG_HEURISTIC`** sem conflitos; `arena_combat` e `dense_city` **`CONFLICTS_REPORTED`** com exatamente um `base_z_fight_risk` medium cada. Zero conflitos high, alpha-over-critical ou overlay/gameplay. Builder `build_scene_composition.py --check` reproduz JSON/Markdown; enforcement no Fast Lane em **31 arquivos / 34 comandos**; suíte CI **620 testes OK**. Nenhuma camada, viewport, shader, cena ou renderer criado; nenhum claim visual. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M10 archetype feedback

**Feedback de combate M10** por PR #266, squash `6ecea44372376a881cb31671eba7dbb2992652e8`. O `FeedbackPlanner` integrado planejou **10 spells** do dataset M05 (2 skirmish + 3 elite + 5 boss), todos `SAFE_CONFIG_HEURISTIC` com **0 conflitos**.

**Resultado:** 5 canais por spell; pico de concorrência **5/5**; hit-stop **40/60/100 ms**; shake máximo **0.313**; dano determinístico **32/64/128/225/75**, com críticos em `storm-lance` e `meteor-storm`. O dataset M05 ganhou o campo aditivo `spells` para consumo downstream. Builder `build_archetype_feedback.py --check` reproduz JSON/Markdown; enforcement no Fast Lane em **30 arquivos / 33 comandos**; suíte CI **613 testes OK**. Nenhuma animação, câmera, shader, partícula, cena ou renderer criado; nenhum claim de game feel. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M11 kit asset audit

**Auditoria M11 do kit M04** por PR #264, squash `2fa50a7223482b734007953b59e0720dfb56cb11`. O `AssetPipelineAuditor` integrado auditou **12 assets** do kit (788.844 bytes), com **0 estágios falhos** e **0 pendentes**.

**Resultado:** **0 findings high**; **12 medium `license_unverified`** e **12 low `texture_uncompressed`**; veredito **`REVIEW_REQUIRED`** com recomendações de verificação de licença e compressão. `kit_sha256` confere com o `kit.v1.json`; nenhuma textura foi importada, cozinhada, carregada ou renderizada, e nenhuma licença foi declarada verificada. Builder `build_kit_audit.py --check` reproduz JSON/Markdown; enforcement no Fast Lane em **29 arquivos / 32 comandos**; suíte CI **606 testes OK**. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M04 kit texture budget

**Orçamento do kit M04 medido** por PR #262, squash `2a2151815b997c3464292fcdae23596909a25c7f`. O `TextureBudgetPlanner` integrado analisou a observação `material.v1` do kit: **4 materiais**, **12 texturas únicas**, **0 refs duplicadas**, **1.048.572 bytes** decodificados/deduplicados e pressão de atlas **0.047** (12 de 256 tiles).

**Resultado:** veredito **FIT**, nenhum finding; `kit_sha256` confere com o `kit.v1.json` commitado. Builder `build_kit_budget.py --check` reproduz JSON/Markdown; enforcement no Fast Lane em **28 arquivos / 31 comandos**; suíte CI **600 testes OK**. Nenhuma textura foi decodificada, comprimida, empacotada, importada ou renderizada; nenhum contrato, planner, kit, cena, preset, renderer, shader ou `project.godot` alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M04/M05 non-rendering asset kit

**M04/M05 estendidos** por PR #260, squash `420680b391e7ca3b23d9e065452cf52d85711740`, sob `NEX-ADR-0011` / `NEX-D-021`. O kit M04 contém **12 PNGs determinísticos 128×128** (albedo, normal, ORM), **quatro `StandardMaterial3D`** `.tres`, uma observação `material.v1` e validação headless por `ResourceLoader` (`KIT_LOAD_OK 28 checks`). O dataset M05 contém **três arquétipos** analisados pelo `FXBudgetPlanner`: `skirmish` **FIT** (484 partículas, 7 emitters), `elite` **TIGHT** (1047/1100) e `boss` **OVER_BUDGET** (2753/2000) com plano de redução de 3 passos e projeção 1834.

**Resultado:** builders `--check` reproduzem todos os bytes; enforcement no Fast Lane em **27 arquivos / 30 comandos**; suíte CI **594 testes OK**. Nenhum shader customizado, `ShaderMaterial`, compilação de shader, renderer, cena, partícula, emissor, luz, decal, runtime, hub, engine, `project.godot` principal ou gameplay foi criado. Nenhum claim de FPS, frame-time, VRAM, overdraw, qualidade visual ou game feel. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · M02-S02/S03/S04 scene analysis

**M02-S02/S03/S04 integrados** por PR #258, squash `8827b7605a5c0d93aa3a8cb5150b7768ba59fd28`. Os protótipos `SightlineController`, `DepthCompositionSolver` e `TemporalGuardAnalyzer` foram vendorizados em `nex_bench/scenes/m02_analysis/` e executados headless sobre geometria real das três cenas M01 e sobre os cinco frames estáticos integrados.

**Resultado:** 17/34/23 meshes; 8 occluders e 16 primitivas por cena; **1 reveal e 1 danger alert** por cena, nenhum ator crítico não visto; **0 z-fight risks** em corridor e **4** em arena/city; 0 alpha-over-critical e 0 overlay-gameplay conflicts; temporal `BASELINE_ACCEPTABLE` em 5 frames e 16 regiões. QA ledger: S02–S04 `scene_analysis=PASS`; `scene_comparison` e `performance` permanecem `INCONCLUSIVE_NOT_RUN` porque não há rendering. 3 runs hasheados; suíte CI **573 testes OK**; 30 comandos de builder/validator. Nenhuma cena base, preset, contrato, renderer, shader ou `project.godot` alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-15 · All parents bounded admitted

**M07 (#12), M08 (#13), M10 (#15), M11 (#16) e M12 (#17) admitidos** como `BOUNDED_ADMITTED_RENDER2D_PIPELINE`, `BOUNDED_ADMITTED_COMPOSITION_PIPELINE`, `BOUNDED_ADMITTED_ANIMATION_PIPELINE`, `BOUNDED_ADMITTED_ASSET_PIPELINE` e `BOUNDED_ADMITTED_IDENTITY_PIPELINE` por `NEX-ADR-0010` / `NEX-D-020`, sobre a base `8bb4bef1b216e71eafe0dc83efe897bb926530ce`. A admissão cobre contratos, documentação, protótipos determinísticos, smoke headless, testes e evidência já verificados.

**Status:** `ALL_PARENTS_BOUNDED_ADMITTED_M01_..._M12`; nenhum parent permanece `NOT_ADMITTED`. **Não admitido:** runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção, renderização real, geração de assets, importação/cozimento, aprovação de marca, performance/FPS/qualidade/game feel. M01–M06/M09 seguem bounded admitted em referência/análise/evidência. A admissão não relaxa CI, segurança, testes, locks ou ruleset. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

**Integração:** PR #256 squash `4a095ef0f9b292ac5c5acf4fa1ebfcbf5fd1a0a9`; árvore idêntica à revisada e checks pós-merge SUCCESS.

## Current verified scope | 2026-11-15 · M02-S01 camera integration

**M02-S01 integrado** por PR #254, squash `7ab8d4abdaf72b8a33921e9c3bf82bca782c4d7e`. O `IsometricCameraRig` foi vendorizado no harness como modo aditivo `baseline|rig`; 18 PNGs visuais e 18 capturas de performance A/B/A nas três cenas M01.

**Resultado:** A/A byte-idêntico; A/B mean abs **0.002/0.0003/0.0** e changed pixels **0.013%/0.003%/0.0%** — o rig reproduz o enquadramento baseline. GPU p95 delta **0.0%/+0.94%/+1.25%**; CPU **0.0%/+13.3%/+12.94%**. QA ledger: S01 `scene_comparison=PASS` e `performance=MEASURED`; S02–S05 permanecem `INCONCLUSIVE_NOT_RUN`; S06 research-only. Nenhuma cena base, preset, contrato, renderer, shader ou `project.godot` alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · Checkpoint schema validator

**NEX-CP-SCHEMA integrado** por PR #252, squash `cf179d7d9ea21ec73fe2698606b4006c2c800720`. O validador `validate_checkpoint.py --check` roda no job requerido e cobre **62 blocos de proveniência**.

**Resultado:** falha em SHA inválido, `pr` sem merge SHA, aprovação independente falsa, bloco de admissão ausente, merge SHAs duplicados e contagem de proveniência incoerente. O checkpoint e o índice permanecem coerentes; nenhum checkpoint, admissão, medição, harness, contrato, modelo ou ruleset alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M09 1600×900

**M09-RES-1600 integrado** por PR #250, squash `b3eaaee65c0f9128510307c041d90deba6b12aac`. Nova sessão de **6 capturas** em `arena_combat`, 100 proxies, 1600×900, A/B/A, todas PASS no validador dedicado.

**Resultado:** GPU p95 **0.133 ms** (ab-low) e **0.632 ms** (ab-high), high/low **+375.2%**. Deltas 1280→1600 **+25.5%/+37.4%**; 1600→1920 **+17.3%/+30.7%**. Modelo M03: **ab-high −27.2%** (entre o match de 1280 e o erro de 1920); ab-low +185.0%. M06 atualizado para **162 observações / 10 bundles**; atlas M09 em **15 bundles / 162 capturas / 114 imagens / 483 arquivos**. Nenhum harness, cena, preset, contrato, modelo, renderer, shader ou `project.godot` alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M09 camera-motion sequence

**M09-CAMERA-MOTION integrado** por PR #248, squash `1feb0863234bf12bcceb048736270fb33e9a5d1f`. Flag aditiva `NEX_PRESET_AB_CAMERA_MOTION` com órbita determinística de **3° por frame capturado**; **30 PNGs** (3 cenas × 2 presets × 5 frames) a 1280×720.

**Resultado:** todos os pares consecutivos diferem; changed pixels **3.132–19.766%**; mean abs médio por célula **1.80–5.16**. Atlas M09 em **14 bundles / 114 imagens / 468 arquivos**. Flag desligada mantém o comportamento estático existente; a estabilidade temporal estática continua em bundle separado. Nenhuma cena base, preset, contrato, renderer, shader ou `project.godot` alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M04/M05 bounded admission

**M04 (#9) e M05 (#10) admitidos** como `BOUNDED_ADMITTED_MATERIALS_PIPELINE` e `BOUNDED_ADMITTED_VFX_PIPELINE` por `NEX-ADR-0009` / `NEX-D-019`, sobre a base `5f801c09ca4148fb9712f84cfd638bd80f3a4372`. A admissão cobre contratos `material.v1`/`spellfx.v1`, documentação, protótipos determinísticos de orçamento de texturas/FX, smoke headless, testes e evidência já verificados.

**Escopo:** contratos e protótipos determinísticos. **Não admitido:** criação de material/shader/textura/atlas/partícula/emissor/luz/decal, decodificação de textura, atlas packing, criação de partículas, integração de renderização, runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção, renderização real, generalização ou claims de FPS/qualidade. M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M01/M02/M03/M04/M05/M06/M09 seguem bounded admitted. A admissão não relaxa CI, segurança, testes, locks ou ruleset. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

**Integração:** PR #246 squash `cd7474c4ebcc5a8275f47cb58235ed14dc0d6150`; árvore idêntica à revisada e checks pós-merge SUCCESS.

## Current verified scope | 2026-11-14 · Provenance index

**NEX-PROVENANCE-INDEX integrado** por PR #243, squash `0bdd8736c18a4035605d20123ef30d75d8802bd3`. O índice deriva do `CHECKPOINT.json` **64 entradas** com PR protegida e merge SHA, PRs **112–256**, 64 merge SHAs únicos.

**Resultado:** cada entrada traz bloco, ID, PR, merge SHA, issues, veredito/status e rótulo de auditoria; todos os rótulos são `ADMIN_SOLO_NOT_INDEPENDENT` e nenhum `INDEPENDENT_APPROVED`. O índice é uma ferramenta de navegação; o checkpoint permanece a autoridade. Nenhum checkpoint, admissão, medição, harness, contrato, modelo ou ruleset alterado. Todos os parents M01–M12 seguem bounded admitted em referência/análise/evidência. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M09 resolution campaign closure

**M09-CAMPAIGN-CLOSURE registrado** por PR #241, squash `ffbfba8e695beca782a97ccdacff2407efddee9a`. Uma tentativa de **3840×2160** foi clampada pelo desktop **2560×1080** para **2560×1009** e rejeitada como `INVALID`; a captura inválida não foi commitada.

**Resultado:** a campanha de resolução está formalmente encerrada em **2560×1440** neste ambiente; acima disso exige display/ambiente com viewport maior. O atlas permanece com 13 bundles / 84 imagens / 435 arquivos. Nenhum harness, cena, preset, contrato, modelo, bundle M09 ou ruleset alterado. O `NEX Native Batch` teve um 502 transitório da API e passou no re-run. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M09 visual truth at 2560×1440

**M09-VISUAL-2560 integrado** por PR #239, squash `9ab06ca44c4648dd0dc7c1df922feba772ba369c`. Nova sessão visual de **18 PNGs** em `corridor_static`, `arena_combat` e `dense_city`, 2560×1440, 2 presets × 3 repetições.

**Resultado:** A/A byte-idêntico por SHA; A/B changed pixels **2.996%/3.074%/1.031%**; mean abs **0.3694/0.3863/0.1524**; Δ mean abs vs 1920 **−11.4%/−8.4%/−14.6%**. Atlas M09 em **13 bundles / 84 imagens / 435 arquivos**. Núcleo `visual_truth.py` compartilhado; saída do relatório 1920 byte-idêntica. Nenhum harness, cena, preset, contrato, renderer, shader ou `project.godot` alterado. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M03 domain consolidation

**M03-DOMAIN-CONSOLIDATION integrado** por PR #237, squash `b0320147c6a9836631dbb5a167efd2aab73b88da`. O relatório `--domain` passa a incluir o grid de resolução (6 células), **200 proxies em 1280×720** (2 células) e **2560×1440** (2 células).

**Resultado:** `ab-high`/1280×720 dentro de 2% em 100 e 200 proxies; 2560×1440 sem acertos; `within_2pct_total = 2`. Veredito **`CALIBRATION_RESOLUTION_MATCH_ONLY`** reforçado — o acerto é específico de 1280×720, robusto a proxies e não sobrevive a 2560×1440. Nenhum modelo, coeficiente, GDScript, bundle M09, contrato, cena, harness ou ruleset alterado. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M06 full refresh (156 observações)

**M06-FULL-REFRESH integrado** por PR #235, squash `db3df0fa454d03dfdf6d11c0f921d95be95c3c3e`. A cadeia M06 passa a cobrir as duas novas medições M09: **156 observações** de **9 bundles**, todas `pacing`.

**Resultado:** atlas com GPU p95 **0.068–1.55 ms** (mediana 0.226), pacing **4.199–4.311 ms** e maior GPU share **36.29%**; advisories com **156** entradas e headroom **2.716–4.009 ms**. Top cell `res-scaling-1440`/`ab-high`/2560×1440/100 proxies/1.547 ms. Saída curada de 12 observações/advisórios inalterada. Nenhuma nova medição, bundle M09, contrato, modelo, cena, harness ou ruleset alterado. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M09 2560×1440

**M09-RES-1440 integrado** por PR #233, squash `586883e2c4416ea3fd4ce3c8cf66879664e5ff55`. Nova sessão de **6 capturas** em `arena_combat`, 100 proxies, 2560×1440, A/B/A, todas PASS no validador dedicado.

**Resultado:** GPU p95 **0.206 ms** (ab-low) e **1.547 ms** (ab-high), high/low **+651.0%**. Deltas 1920→2560 **+32.1%/+87.3%**; 960→2560 **+114.6%/+388.0%**. Modelo M03: **ab-high −70.3%** e **ab-low +84.0%**, ambos fora de 2% — o acerto é específico de 1280×720. Atlas M09 em **12 bundles / 156 capturas / 414 arquivos**. Núcleo `arena_resolution.py` compartilhado; saída do relatório 200/720 byte-idêntica. Nenhum harness, cena, preset, contrato, modelo, renderer, shader ou `project.godot` alterado. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M09 200 proxies at 1280×720

**M09-200-720 integrado** por PR #231, squash `c9196541e6a854ed186cac27cb9820582e4f64fb`. Nova sessão de **6 capturas** em `arena_combat`, 200 proxies, 1280×720, A/B/A, todas PASS no validador dedicado.

**Resultado:** GPU p95 **0.111 ms** (ab-low) e **0.468 ms** (ab-high), high/low **+321.6%**. Contexto 100→200: GPU p95 **+1.8%/+1.3%** e CPU p95 **+29.0%/+48.7%**. Modelo M03: **ab-high −1.7% (dentro de 2%)**, ab-low +241.4% — o acerto de calibração é robusto à mudança de proxies. Atlas M09 em **11 bundles / 150 capturas / 399 arquivos**. Nenhum harness, cena, preset, contrato, modelo, renderer, shader ou `project.godot` alterado. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M03 domain boundary

**M03-DOMAIN-BOUNDARY integrado** por PR #229, squash `c2b7c96ac154376ab2de997f64f4e2b448eaad36`. O modo `--domain` compara o modelo de luz com 6 células da arena em 960×540/1280×720/1920×1080.

**Resultado:** previsto invariante (0.379/0.460 ms); medido cresce **+62.5%** (ab-low) e **+160.6%** (ab-high) de 960 para 1920; único acerto em 2% em **ab-high/1280×720**. Veredito **`CALIBRATION_RESOLUTION_MATCH_ONLY`**: o match é específico da resolução de calibração, não validade geral. Nenhum coeficiente, snapshot, GDScript, bundle M09, contrato, cena ou medição alterado. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M06 full-dataset advisories

**M06-FULL-ADVISORIES integrado** por PR #227, squash `59c799a5fe0715a7a8da0548367b68f21d5d5ddb`. O modo `--full` deriva **144 advisórios** das 144 observações `performance.v1`; `--check-full` foi adicionado ao check obrigatório.

**Resultado:** 144/144 `pacing`; headroom **3.327–4.009 ms**; maior GPU share **21.05%**; frame alvo **4.167 ms**; recomendações `LOW` com `requires_measurement`. A saída curada de 12 advisórios permanece byte-idêntica. Nenhuma nova medição, captura, renderização ou mudança de observação/atlas/contrato. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · CI builder reproducibility enforcement

**CI-BUILDER-CHECK integrado** por PR #223, squash `c972864af21a0e416b335c10c936af2ea6be2d44`, e estendido a M01/M02 por PR #225, squash `e9f8f0172a7c183b57fd203dc1053af099c63bec`. O check obrigatório `NEX Fast Lane / Batch Policy Tests` passa a executar **27 comandos `--check`** dos builders determinísticos de M01/M02/M03/M06/M09 (24 arquivos; `convert_m09_observations.py` e `build_advisories.py` cobrem `--check`/`--check-full`; `build_budget_validation.py` cobre `--check`/`--check-domain`).

**Guard:** `tests/ci/test_builder_check_enforcement.py` falha se um builder novo não for listado, se algum comando usar modo escrita ou se o job deixar de ser required context. Nenhum builder, artefato, dado, contrato, medição ou ruleset foi alterado; nenhuma nova medição. M01/M02/M03/M06/M09 seguem bounded admitted e M04–M05, M07–M08 e M10–M12 `NOT_ADMITTED`. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Current verified scope | 2026-11-14 · M01/M02 bounded admission

**M01 (#6) e M02 (#7) admitidos como `BOUNDED_ADMITTED_REFERENCE_PIPELINE`** por `NEX-ADR-0008` / `NEX-D-018`, sobre a base `e729774583eb8ce3b75271aea66589bb9e04a587`. A admissão cobre contratos M01/M02, cenas base de referência, docs/QA, protótipos de câmera/profundidade/perfis/sightline/temporal e testes associados.

**Escopo:** referência e análise determinística. **Não admitido:** runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção, renderização real, `nex_modules/render2d`/M07, generalização ou claims de FPS. M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M01/M02/M03/M06/M09 estão bounded admitted. A admissão não relaxa CI, segurança, testes, locks ou ruleset. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

**Integração:** PR #221 squash `3e8dbc0af90102ceebc1cac3e4901418d07771cf`; árvore idêntica à revisada e checks pós-merge SUCCESS.


## Current verified scope | 2026-11-14 · M03 bounded admission

**M03 (#8) admitido como `BOUNDED_ADMITTED_ANALYSIS_PIPELINE`** por `NEX-ADR-0007` / `NEX-D-017`, sobre a base `51110ff02eb2c542832b6290a98fdc5f979b58a9`. A admissão cobre o contrato `lighting.v1`, light rig, shadow stability, light budget e a validação do modelo contra M09, com docs, builders e testes.

**Escopo:** análise determinística de iluminação e orçamento. **Não admitido:** runtime, renderer, shaders, cenas, hub, `project.godot`, implementação real de luz/sombra/GI, generalização ou claims de FPS. M01–M02, M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`. M03/M06/M09 estão bounded admitted; a admissão não relaxa CI, segurança, testes, locks ou ruleset. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

**Integração:** PR #219 squash `d8ad6152eec96aa9d303f4987c5742af665b16ec`; árvore idêntica à revisada e checks pós-merge SUCCESS.


## Current verified scope | 2026-11-14 · M06 full dataset + atlas

**M06-FULL-ATLAS integrado** por PR #217, squash `373d6e7a4eb3cceffe86d9eb491f518c1f558228`. O conversor `--full` gerou **144 observações `performance.v1`** dos sete bundles de performance M09; o atlas agrega essas observações por bundle e célula de workload.

**Resultado:** 144/144 observações válidas e classificadas como `pacing` no cap de 240 fps; GPU p95 global **0.068–0.887 ms** (mediana 0.196), pacing p95 **4.199–4.301 ms**, maior GPU share **21.05%**. Sem nova medição, runtime ou mudança de contrato. M06/M09 permanecem `BOUNDED_ADMITTED_EVIDENCE_PIPELINE`; os demais parents seguem `NOT_ADMITTED`.


## Current verified scope | 2026-11-14 · M06/M09 bounded admission

**M06 (#11) e M09 (#14) admitidos como `BOUNDED_ADMITTED_EVIDENCE_PIPELINE`** por `NEX-ADR-0006` / `NEX-D-016`, sobre a base `8ed41bafaf19cff52da9250784f78c3d608ac504`. A admissão cobre contratos, protótipos, harnesses, bundles de evidência, relatórios, builders e testes já verificados.

**Escopo:** M06 (performance.v1, atlas S05, observações M09, advisórios) e M09 (preset_pack.v1, resolver, harness A/B, todos os bundles de medição, atlas). **Não admitido:** runtime, hub, engine, renderer, shaders, cenas de produção, aplicação de presets, generalização de performance/qualidade ou claims de FPS. M01–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`. A admissão não relaxa CI, segurança, testes, locks ou ruleset; trabalho futuro sob M06/M09 exige WO/Context Lock e checks. Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

**Integração:** PR #215 squash `8a59aa8a4f6b52becad3503922b9a1e4cdf6127c`; árvore idêntica à revisada e checks pós-merge SUCCESS.


## Current verified scope | 2026-11-14 · M03 light-budget validation

**M03-BUDGET-VALIDATION integrado** por PR #213, squash `f1e458e9442ac8d1cb534e606ceb788a1237e449`. O snapshot do `nex_light_cost_model.v1` foi conferido contra o GDScript e comparado a 6 células M01 (3 cenas × 2 presets) medidas em M09.

**Resultado:** 2/6 células dentro de 2% (corridor e arena no `ab-high`); o low preset é superestimado em 247.7–380.4% e city high difere +33.8%. Veredito **`PARTIAL_DOMAIN_MATCH`**: o modelo representa luzes/sombras, não resolução, MSAA, glow, atlas ou geometria; os acertos em 2% são candidatos a coincidência de domínio, não prova de generalização. Parent M03 (#43) continua **NOT_ADMITTED**; nenhuma mudança de modelo, contrato, engine, cenas ou CI.


## Current verified scope | 2026-11-14 · M09 temporal stability

**M09-TEMPORAL integrado** por PR #211, squash `cf9ae9c0207544aab342545451255520158eadf4` (harness `22f428a`). O harness ganhou modo de sequência visual determinístico: **30 PNGs** (3 cenas × 2 presets × 5 frames) a 1280×720, com intervalo de 30 frames após warmup.

**Medição:** todas as cinco frames de cada célula são byte-idênticas; todas as comparações frame-a-frame são exatamente zero no workload estático. O atlas M09 foi atualizado para **10 bundles, 66 imagens e 384 arquivos**. Isto é estabilidade temporal de frames estáticos, não qualidade visual ou generalização para animação/efeitos dinâmicos. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 visual truth 1920×1080

**M09-VISUAL-1920 integrado** por PR #209, squash `1eb6b4471402cb0a2b040f2e75a5c24255df9362` (harness `06eb6d92`). As três cenas M01 foram capturadas em 1920×1080 sob `ab-low`/`ab-high`, 3 repetições por célula: **18 PNGs**, A/A byte-idêntico e 21 arquivos com `SHA256SUMS`.

**Medição:** A/B mean abs 0.4168/0.4215/0.1785 e pixels alterados 3.367%/3.354%/1.276% (corridor/arena/city); as diferenças são ligeiramente menores que em 1280×720 (−18.8%/−13.9%/−23.0% em mean abs). O atlas M09 foi atualizado para **9 bundles, 36 imagens e 351 arquivos**. Isto é diferença de pixels, não ranking de qualidade. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M06 performance advisories

**M06-ADVISOR integrado** por PR #207, squash `4def973f3c5170f1d9087ae3ae97d05aaa522592`. O builder deriva **12 advisórios** das observações `performance.v1`: headroom de render **3.402–3.914 ms**, frame alvo **4.167 ms** a 240 fps, maior participação GPU no frame **19.92%** e recomendação de baixo risco que exige nova medição.

**Semântica:** todos os 12 advisórios são `pacing` no cap de 240 fps; o texto explicita que headroom não prova capacidade em cap menor e que não há claim de FPS, qualidade ou ganho. Isto é **síntese de evidência**, não nova medição. Parent M06 (#59) continua **NOT_ADMITTED**; nenhum contrato, engine, cena, `project.godot`, hub ou CI alterado.


## Current verified scope | 2026-11-14 · M06 performance.v1 observations

**M06-OBS integrado** por PR #205, squash `6c18c45cf9de938e5138ca188c5b321b23d35bbd`. O conversor determinístico transformou **12 capturas M09** já integradas em observações `performance.v1` com IDs únicos, proveniência e `evidence_uri`: 4 de `preset-ab`, 2 de `m01-ab`, 4 de `res-scaling` e 2 de `interaction-200`.

**Semântica:** GPU/CPU/pacing p95 e alocação p50 medidos; `frame_interval`, draw calls, objetos renderizados e VRAM marcados `UNAVAILABLE` com razão explícita. As 12 observações passam o schema e o consumidor de coerência M06 e classificam `pacing` no cap de 240 fps. Isto é **conversão de evidência**, não nova medição, FPS de jogo ou generalização. Parent M06 (#59) continua **NOT_ADMITTED**; nenhum contrato, engine, cena, `project.godot`, hub ou CI alterado.


## Current verified scope | 2026-11-14 · M09 measurement atlas

**M09-ATLAS integrado** por PR #203, squash `db6efc12834e0e99b4b71103d6a94d3844d562af`. O atlas indexa os oito bundles M09 com verificação de runs, arquivos e source SHA: **144 capturas de performance**, **18 imagens**, **330 arquivos de evidência** e **8 source SHAs**.

**Síntese:** o preset high custa mais GPU que o low em todas as cenas/células; a resolução domina o custo GPU em 50–200 proxies e o delta do preset cresce com a resolução; proxies afetam mais o CPU; capturas visuais A/A são byte-idênticas e A/B difere em 1.745–4.077% dos pixels a 1280×720. Tudo é sessão única em uma RTX 5050, sem generalização cross-device ou cross-session. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança de engine, cenas, `project.godot`, hub ou CI.


## Current verified scope | 2026-11-14 · M09 200-proxy interaction

**M09-INTERACTION-200 integrado** por PR #201, squash `48ce7e16ca0b74107143eeefcf1f8dc414fa5801` (source medido `c1b73743`). A cena `arena_combat` foi medida com 200 proxies em 960×540/1920×1080, viewport nativo, 3 runs por preset por resolução: **12 capturas COMPLETE/validadas**, 27 arquivos com `SHA256SUMS`, análise e relatório reproduzível.

**Medição:** GPU p95 high vs low **+228.6% (960×540)** e **+438.2% (1920×1080)**; resolução 960→1920 **+60.2% (low)** e **+162.4% (high)**; 100→200 proxies **+2.1–9.0%** (contexto de sessão separada, rotulado). O padrão pixel-bound se mantém no limite de 200 proxies. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 cross-scene interaction

**M09-CROSS-SCENE integrado** por PR #199, squash `ddf9996c29652f7d2b85931ed4682718b5d646c5` (source medido `2a03cbb7`). `corridor_static` e `dense_city` foram medidas em 50/100 proxies × 960×540/1920×1080, viewport nativo, 3 runs por preset por célula: **48 capturas COMPLETE/validadas**, 99 arquivos com `SHA256SUMS`, análise e relatório reproduzível.

**Medição:** GPU p95 high vs low **+294.4%/+464.3–476.5% (corridor)** e **+245.6–249.3%/+457.3–461.5% (city)**; resolução 960→1920 **+79.4–97.2% (low)** e **+180.0–191.5% (high)**; proxies 50→100 **0.0–2.9% no GPU**. O padrão pixel-bound de `arena_combat` se repete nas duas cenas; resolução domina o GPU e proxies afetam mais o CPU. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 proxies × resolução

**M09-INTERACTION integrado** por PR #197, squash `369afd850bbd2fc70a3b8951225aa52c27279786` (source medido `2ef072c`). A cena M01 `arena_combat` foi medida em 50/100 proxies × 960×540/1920×1080, viewport nativo, 3 runs por preset por célula: **24 capturas COMPLETE/validadas**, 51 arquivos com `SHA256SUMS`, análise e relatório reproduzível.

**Medição:** GPU p95 high vs low **+219.8% (50/960×540)**, **+469.4% (50/1920×1080)**, **+227.1% (100/960×540)**, **+473.6% (100/1920×1080)**. Resolução 960→1920: `ab-low` +50.0%; `ab-high` +167.1% (50) e +163.1% (100). Proxies 50→100: 0.0–2.3% no GPU e +4.2–7.8% no CPU. Leitura: no range de 50–100 meshes, o custo GPU é dominado por resolução e a contagem de proxies afeta principalmente CPU. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 preset resolution scaling

**M09-RES-SCALING integrado** por PR #195, squash `ebe006d58a5b28bdcdfa34d7a116e68aa535aa8a` (source medido `6ebb98e`). A cena M01 `arena_combat` foi medida em 960×540, 1280×720 e 1920×1080 com viewport nativo (`NEX_PRESET_AB_NATIVE_RESOLUTION=1`), 3 runs por preset por resolução: **18 capturas COMPLETE/validadas**, 39 arquivos com `SHA256SUMS`, análise e relatório reproduzível.

**Medição:** GPU p95 high vs low **+230.2% (960×540)**, **+334.0% (1280×720)**, **+429.5% (1920×1080)**; escala 960→1920 **+62.5% (low)** e **+160.6% (high)**; pacing ~4.2 ms no cap de 240 fps. A primeira tentativa sem viewport nativo registrou 1280×720 lógico e foi descartada antes da evidência. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 M01 visual truth

**M09-M01-VISUAL integrado** por PR #193, squash `40528ee06e092739822c420d60b7c81400aca9ff` (harness `952b5a6`). O harness `preset_ab` ganhou um modo visual determinístico que espera 180 frames, lê o viewport após `RenderingServer.frame_post_draw` e salva PNG 1280×720. Foram capturadas **18 imagens** das três cenas M01 sob `ab-low`/`ab-high` (3 repetições por célula), com 21 arquivos cobertos por `SHA256SUMS`, análise e relatório reproduzível.

**Medição:** todas as repetições de cada par cena/preset são byte-idênticas (mesmo SHA-256); todas as comparações A/A são exatamente zero. O `ab-high` altera a imagem em todas as cenas: **4.077% (corridor)**, **3.884% (arena)** e **1.745% (city)** de pixels com diferença > 2; mean abs 0.5135/0.4898/0.2317 e PSNR 37.406/36.386/39.763 dB. Isto confirma mudança de estado de rendering, **não** ranking de qualidade. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 M01 scene A/B/A

**M09-M01-AB integrado** por PR #191, squash `d657afad0dbabdcfb1d2143fee71e71d448b07c9` (source medido `617db53d`). O harness A/B/A ganhou `NEX_PRESET_AB_SCENE` para `corridor_static`, `arena_combat` e `dense_city`; cada cena reutiliza câmera/luzes e recebe fillers determinísticos até 100 meshes totais. Foram medidas **18 capturas reais** na RTX 5050 (3 runs por preset por cena), todas COMPLETE/validadas, com `SHA256SUMS` de 39 arquivos, manifesto, análise e relatório reproduzível.

**Medição:** GPU p95 high vs low **+380.7% (corridor)**, **+323.9% (arena)**, **+331.0% (city)**; spread A/A de GPU p95 1.2–7.3%; pacing ~4.2 ms no cap de 240 fps. O primeiro run ab-high do corridor é um outlier documentado (0.542 ms vs 0.421/0.423 ms); medianas reportadas. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M09 preset scaling 25/100/200

**M09-PRESET-SCALING integrado** por PR #189, squash `109a17af4724b8c5236991551538a62e3fa1f3b1` (source medido `4e4719ac`). O harness foi parametrizado por `NEX_PRESET_AB_PROXY_COUNT` (25/50/100/200) e mediu **18 capturas reais** na RTX 5050: 3 runs por preset em cada contagem. Todas COMPLETE/validadas; `SHA256SUMS` de 39 arquivos; relatório e builder reproduzíveis.

**Medição:** GPU p95 high vs low **+504.7% (25)**, **+499.3% (100)**, **+478.3% (200)**; escala 25→200 +18.7% (low) e +13.6% (high); pacing ~4.267 ms no cap de 240 fps. Uma run 200/low tem 1% low outlier (157.39); medianas reportadas. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança em `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · Autonomia contínua registrada

**NEX-ADR-0005 / NEX-D-015 integrados** por PR #187, squash `6e99caa2049bda2646ae16df0b26bef09e5ce3d5`. O administrador pode escolher e executar o próximo incremento bounded de forma contínua, em ciclos longos, sem confirmação por incremento. A autonomia para somente em bloqueio técnico real, dependência não admitida, risco grave, operação irreversível sem autorização, CI vermelha/pendente, Context Lock STALE, base/HEAD divergente, defeito HIGH/CRITICAL, conflito de escrita ou exigência de plataforma. Não admite parents PLANNING_ONLY, não relaxa CI/testes/locks/ruleset e mantém `ADMIN_SOLO / NOT_INDEPENDENT`.


## Current verified scope | 2026-11-14 · M09-PRESET-AB measured A/B/A

**M09-PRESET-AB integrado** por PRs #183/#185, squashes `cb0ac796008273d4aa9a6f987a577cb1c478ea2a` e `9fd83a27b3acf830d5713429e73035198a7dcf63` (source medido `baf818ef`). A cena isolada `nex_bench/scenes/preset_ab/` aplica presets `preset_pack.v1` em runtime (resolução, MSAA, sombras, atlas, glow, tonemap, target fps), desliga vsync, limita a 240 fps e captura pelo profiler existente. **6 capturas COMPLETE/validadas** na RTX 5050 (3 por preset), `SHA256SUMS` de 15 arquivos, relatório e builder reproduzíveis.

**Medição:** GPU p95 mediano **0.147 → 0.881 ms (+499.3%)** do `ab-low` para o `ab-high` em 200 proxies/1280×720; CPU p95 +32.2%, pacing +0.4%, 1% low −0.8%; spread A/A de GPU p95 3.4%. Isto é **custo medido**, não FPS de jogo ou ganho universal. Parent M09 (#14) continua **NOT_ADMITTED**; nenhuma mudança em `project.godot`, hub, renderer, shaders, engine ou CI.


## Current verified scope | 2026-11-14 · M12-VALIDATOR prototype

**M12-VALIDATOR integrado como protótipo isolado** por PR #181, squash `e1bd1aa2228386d6c9557e32c1dd073a048a28aa` (código `0df75884`). Em `nex_modules/brand/tokens/`, o validador determinístico consome `identity.v1`: paleta/papéis, contraste WCAG calculado dos hex, tipografia, logo viewBox/digests, spacing, acessibilidade e proveniência; emite `READY_FOR_UI`, `REVIEW_REQUIRED`, `BLOCKED` ou `INVALID_INPUT` com recomendações. **36 asserts headless** e 9 testes estruturais.

**Parent M12 (#17) continua NOT_ADMITTED.** Nenhum logo/tema/SVG gerado ou aprovado; contraste não é medido em tela; marca/trademark fora de escopo. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-14 · M11-AUDIT prototype

**M11-AUDIT integrado como protótipo isolado** por PR #179, squash `46b7f4ff0480b8cffb9f931e340d785bcd34ce2d` (código `30b3f211`). Em `nex_modules/assets/license_audit/`, o auditor determinístico consome `asset_pipeline.v1`: valida estágios raw→imported→cooked→validated, licenças SPDX/atribuição/verificação, dependências/ciclos, orçamentos e heurísticas de qualidade; emite `READY_FOR_INTEGRATION`, `REVIEW_REQUIRED`, `BLOCKED` ou `INVALID_INPUT` com recomendações. **43 asserts headless** e 9 testes estruturais.

**Parent M11 (#16) continua NOT_ADMITTED.** Nenhum asset importado/cookado/carregado; verificação de licença é declarada, não executada; qualidade/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M09-RESOLVER prototype

**M09-RESOLVER integrado como protótipo isolado** por PR #177, squash `affae5d67e0c75a2b0dd1c85924cc6d981f20d03` (código `bb320b3c`). Em `nex_modules/tools/preset_resolver/`, o resolvedor determinístico carrega `preset_pack.v1`, valida tiers/settings/monotonicidade, checa hardware/Godot/contratos, resolve por tier ou id, faz merge profundo de overrides e valida reduced motion. **50 asserts headless** e 9 testes estruturais.

**Parent M09 (#14) continua NOT_ADMITTED.** Nenhum preset aplicado a engine/`project.godot`; compatibilidade é declarada, não probada; FPS/qualidade `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M09 preset pack contract v1

**Contrato M09 v1 integrado** por PR #175, squash `4b3271f2c5f102e18a910658955ca9bffa8dcd5d` (código `80ee24bd`). `contracts/m09/preset_pack.v1.schema.json` define tiers low→ultra/custom, blocos de render/luz/performance/2.5D/feedback/acessibilidade, compatibilidade e proveniência. Ownership prospectivo de `nex_modules/tools/**`, docs e **16 testes novos** (suíte de contratos 203 OK; total 563 em worktree LF limpo). Com M09, todos os módulos M01–M12 têm interface versionada.

**Parent M09 (#14) continua NOT_ADMITTED.** Nenhum preset aplicado, `project.godot` alterado, UI de editor criada ou runtime medido; `target_fps` é alvo, não medição. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M12 visual identity contract v1

**Contrato M12 v1 integrado** por PR #173, squash `caa98a9c330b826a906840006536ffa6241a2ea0` (código `1dcc0605`). `contracts/m12/identity.v1.schema.json` define paleta com papéis e contraste WCAG, tipografia, logo SVG com digests/viewBox, spacing, acessibilidade e proveniência. Ownership prospectivo de `nex_modules/brand/**`, docs e **18 testes novos** (suíte de contratos 187 OK; total 547 em worktree LF limpo).

**Parent M12 (#17) continua NOT_ADMITTED.** Nenhum logo/SVG/tema gerado, marca aprovada, engine ou CI alterado; contraste é calculado dos hex, não medido em tela. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M11 asset pipeline contract v1

**Contrato M11 v1 integrado** por PR #171, squash `92ede8238e91a3e75456a03d9557310f33199527` (código `292c8ac4`). `contracts/m11/asset_pipeline.v1.schema.json` define estágios raw→imported→cooked→validated, licença SPDX/atribuição/verificação, import settings, dependências, política de licenciamento, orçamentos e proveniência. Ownership prospectivo de `nex_modules/assets/**`, docs e **19 testes novos** (suíte de contratos 169 OK; total 529 em worktree LF limpo).

**Parent M11 (#16) continua NOT_ADMITTED.** Nenhum asset importado/cookado/carregado, licença verificada, engine ou CI alterado; licenciamento/qualidade `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


## Current verified scope | 2026-11-13 · M10-FEEDBACK planner prototype

**M10-FEEDBACK integrado como protótipo isolado** por PR #169, squash `0709923347d8bd145046e69c997f6a6fa8ef81ed` (código `e62d9290`). Em `nex_modules/animation/combat_feedback/`, o planejador determinístico consome `feedback.v1`: fases do ataque, hit events, timeline priorizada, budgets de hit-stop/shake/concorrência, conflitos e exportação de observação para planos seguros. **66 asserts headless** e 9 testes estruturais.

**Parent M10 (#15) continua NOT_ADMITTED.** Sem animação, câmera, shader, cena ou rendering; budgets são aritméticos; game feel/performance `INCONCLUSIVE_NOT_RUN`. Nenhum checkpoint é promovido por este delta; a autorização permanente do Owner permite seguir para o próximo incremento independente.


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

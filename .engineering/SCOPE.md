# Scope · NEX Bootstrap

## Current bounded admission | all parents M01–M12 (2026-11-15)

**Status bounded:** M01/M02 `BOUNDED_ADMITTED_REFERENCE_PIPELINE`; M03 `BOUNDED_ADMITTED_ANALYSIS_PIPELINE`; M04 `BOUNDED_ADMITTED_MATERIALS_PIPELINE`; M05 `BOUNDED_ADMITTED_VFX_PIPELINE`; M06/M09 `BOUNDED_ADMITTED_EVIDENCE_PIPELINE`; M07 `BOUNDED_ADMITTED_RENDER2D_PIPELINE`; M08 `BOUNDED_ADMITTED_COMPOSITION_PIPELINE`; M10 `BOUNDED_ADMITTED_ANIMATION_PIPELINE`; M11 `BOUNDED_ADMITTED_ASSET_PIPELINE`; M12 `BOUNDED_ADMITTED_IDENTITY_PIPELINE`, conforme `NEX-ADR-0006` a `NEX-ADR-0010` e `NEX-D-016` a `NEX-D-020`, sobre a base `8bb4bef1b216e71eafe0dc83efe897bb926530ce`. Admitidos: contratos, cenas base de referência, protótipos, harnesses, bundles de evidência, relatórios, builders e testes já verificados. Não admitidos: runtime, hub, engine, renderer, shaders, cenas de produção, aplicação de presets, implementação real de luz/sombra/GI, criação de materiais/texturas/partículas, renderização real, geração de assets, aprovação de marca, generalização ou claims de FPS/qualidade. Nenhum parent permanece `NOT_ADMITTED`; os doze estão bounded admitted em referência/análise/evidência. A admissão não relaxa CI, segurança, testes, locks ou ruleset; trabalho futuro exige WO/Context Lock e checks.

### M01 full reference | laboratório concluído (2026-11-15)

`NEX-ADR-0012` / `NEX-D-022` admitem, de forma bounded ao laboratório M01, as três cenas base, o harness nativo, a golden matrix 1920×1080, o budget 1080p aprovado, a auditoria de licenças e o gate final. As issues #21, #23, #27 e #6 podem ser fechadas após integração protegida. M01 é o primeiro módulo base concluído como **laboratório de referência**, não como jogo. M02–M12 continuam bounded e exigem WO própria para rendering/runtime; M12 depende de aprovação de marca. A base desta extensão é `900d2b2d031a87048702625a1e98bc50905bc663`.

### M02 full reference | renderer concluído (2026-11-15)

`NEX-ADR-0013` / `NEX-D-023` admitem o M02 como renderer de referência bounded: câmera S01, sightline S02, DepthWeave S03, TemporalGuard S04 com TAA nativo e compositor customizado NO_GO, RenderPassport S05, R&D S06 e QA S07. As issues #28–#34 e #7 podem ser fechadas após integração protegida. M02 é o segundo módulo base concluído como **renderer de referência**, não como jogo. M03–M12 continuam bounded e exigem WO própria; M12 depende de aprovação de marca. A base desta extensão é `fa1adae7ab67e38c2556d126627006c338e2e8f4`.

### M03 full reference | iluminação cinematográfica concluída (2026-11-15)

`NEX-ADR-0014` / `NEX-D-025` admitem o M03 como iluminação de referência bounded: três looks CineLight originais, ShadowStability low/ultra, SDFGI on/off, FogWeave volumetric/depth/off, LightBridge com dois consumidores mock e LightBudget MVP por energia. As issues #36–#43 e #8 podem ser fechadas após integração protegida. M03 é o terceiro módulo base concluído como **iluminação de referência**, não como jogo; **nenhuma paridade com PoE2 é alegada**. M04–M12 continuam bounded e exigem WO própria; M12 depende de aprovação de marca. A base desta extensão é `6be39d49d8769ff46a98990c6818c8132e9e5a1d`.

### M04 full reference | materiais concluídos (2026-11-15)

`NEX-ADR-0015` / `NEX-D-026` admitem o M04 como materiais de referência bounded: atlas PBR de 8 materiais originais, 24 texturas 256×256, galeria nativa, shader triplanar/wet, Decal3D com API de requests e escala 1K/2K/4K em memória. As issues #44–#51 e #9 podem ser fechadas após integração protegida. M04 é o quarto módulo base concluído como **materiais de referência**, não como jogo; **nenhuma paridade com PoE2 é alegada**. M05–M12 continuam bounded e exigem WO própria; M12 depende de aprovação de marca. A base desta extensão é `e09cce2f4332e00a0f51eacb346f5763fe228db9`.

### Extensão bounded M04/M05 | kit não-rendering (2026-11-15)

`NEX-ADR-0011` / `NEX-D-021` estendem o escopo de M04/M05, sem mudar o status dos parents, para o kit PBR procedural `nex_modules/materials/kit/**` (12 PNGs 128×128, quatro `StandardMaterial3D` `.tres`, observação `material.v1`, validação headless) e o dataset `nex_modules/vfx/fxbudget/dataset.gd` com três arquétipos de orçamento de FX. Continua não admitido: shader customizado, `ShaderMaterial`, compilação de shader, renderer, integração/aplicação em cena, rendering, runtime, hub, engine, `project.godot` principal, gameplay, cenas de produção, partículas/emissores/luzes/decais reais, decodificação/compressão/atlas packing, pipeline de import/cook, generalização e claims de FPS/qualidade. A base desta extensão é `99437b22e94a6494eaef801872bb8fd0c79c0f1a`.

## Historical bounded scope clarification | Stage B checkpoint only

**Historical record.** This section predates the M06/M09 bounded admission and is not current status.

Contracts v1 #19 and synthetic FramePulse S02 #22 are independently protected-integrated (PR #93 and PR #95). Stage A governance lock PR #97 passed 37/37 blob pins and fully audited postmerge CI. Current Stage B corrects **seven canonical status files only**, not execution privileges; M01 parent/S01/other children remain NOT_ADMITTED. No real GPU/FPS benchmark, Godot renderer modification, CI change or native release. All former decisions and immutable scopes below remain valid as historical records. Separate exact-head Owner consent and postmerge audit required for Stage B promotion.

Status: CANONICAL GEF BOOTSTRAP VERIFIED + BOUNDED M00 GODOT NATIVE BASELINE VERIFIED (PR #78 implementation, PR #79 checkpoint). M01 NOT_ADMITTED.
HISTORICAL GEF BOOTSTRAP: Source Pack, bounded Work Order/Context Lock, pinned GEF CLI v1.1.2, safe init, doctor/status, evidence and checkpoint audit. THIS SOURCE PACK REVISION: corrects the five historic M00 current-status contradictions identified by Issue #81, subject to exact-head review, separately Owner-authorized protected merge and postmerge audit. Fast Lane PR #83 merged in `a14de0c2f2c94e2c4a7a444e7a7fd777ca2a5a56`; sentinel correction PR #86 merged in `ef401a3cfc1571804a529ef576dcc7494ad394c6`, with native batch runtime SUCCESS on protected main. Five-module threshold has not been exercised with five accepted modules. Free static/security review migration PR #90 is protected-promoted at `84063a0f7e4b216e0787b6c458408367067d40e7`; CodeRabbit is no longer a mandatory live ruleset check, with six free checks in its place. Static review is not a substitute for a substantive semantic review for higher-risk changes. No M01 implementation admitted.
IMPORTANT LATER: compare Godot-native renderer and advanced 3D scene visual benchmarks against reference targets.
FUTURE: custom lighting, volumetrics, GPU VFX, PBR, streaming/LOD, shader tools, 2D/2.5D pipeline, game and multiplayer systems.
OUT OF SCOPE of the completed GEF-only WO: downloading/building Godot. M00 was subsequently separately admitted, Context-Locked, implemented in PR #78 and checkpoint-promoted by PR #79. Still forbidden: browser game, engine core modifications, gameplay, auth, paid/cloud runtime, high-risk cleanup, expanding GEF.
Only NECESSARY is automatically admitted in this phase. All future work requires distinct decision, scope and Work Order.

## NEX-M00-WO-001 bounded scope (historical, admitted and completed)
Native Godot 4.7.2-stable editor/runtime baseline, reproducible minimal source/toolchain, verified official release checksum, Windows build/smoke and Ubuntu headless smoke, build manifest and evidence. No rendering improvements, new GDExtensions, custom engine fork/core patch, or M01 performance/visual claims. Exact FILES_ALLOWED, shared-file writer and STOP gates: `.engineering/m00/M00-SCOPE-AND-DOD.md` and the promoted M00 execution Context Lock. No M01 admission implied.

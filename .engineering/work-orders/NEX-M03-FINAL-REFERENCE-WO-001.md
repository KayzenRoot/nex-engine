# NEX-M03-FINAL-REFERENCE-WO-001 | Fechamento da iluminação cinematográfica M03

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0014` / `NEX-D-025`; instrução do Owner de 2026-11-15 para finalizar o M03 com qualidade cinematográfica, sem paridade com PoE2.
**Base:** `main` `6be39d49d8769ff46a98990c6818c8132e9e5a1d`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (capturas e medições de iluminação).
**Lock:** `.engineering/context-locks/NEX-M03-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M03 como iluminação de referência: três looks CineLight originais, ShadowStability low/ultra, SDFGI on/off, FogWeave volumetric/depth/off, LightBridge com dois consumidores mock e LightBudget MVP; produzir R&D/QA e fechar #36–#43 e #8 após integração protegida.

## Escopo

- Flags aditivas no harness `preset_ab.gd`: look, GI, fog, torches, light budget.
- `nex_bench/scenes/m03_lighting/light_rig_planner.gd` (vendorizado), `light_bridge.gd`, `bridge_smoke.gd`.
- Evidence bundles `windows-rtx5050-2026-11-15-m03-looks`, `...-gi`, `...-fog`, `...-shadows`, `...-budget`, `...-perf`, `...-bridge`.
- `docs/benchmarks/m03/tools/build_lighting_runtime.py`, `lighting-runtime.v1.json`, `LIGHTING-RUNTIME.md`, `M03-FINAL-GATE.md`.
- `tests/ci/test_m03_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de issues.

## Fora de escopo

- Assets, shaders, cenas ou paridade com PoE2.
- Arte de produção, personagens, VFX/telegraphs reais.
- Bake LightmapGI/VoxelGI, GI dinâmica completa, oclusão dinâmica.
- Renderer/runtime M04–M12, jogo, gameplay, rede, cloud.
- Claims generalizados de FPS/qualidade ou cross-device.

## DoD

- 9 capturas de looks (3 × 3 cenas); GPU p95 3.039–3.129 ms no corredor.
- Shadow low/ultra: 1.526 → 3.144 ms; temporal `NOT_RUN`.
- SDFGI off/on: 1.976 → 3.140 ms (+58.9%), +451.1 MiB; decisão qualidade-only.
- Fog volumetric/depth: +4.6%; fallback depth.
- LightBridge: 13/13 checks com dois consumidores mock.
- LightBudget 2 vs 4 tochas: 3.150 → 3.020 ms (-4.1%); `RESEARCH_MORE`.
- Builder `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issues #36–#43 e #8 fechadas com comentário de evidência.

## STOP

- Base/HEAD divergente, captura não determinística, smoke falhando, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.

# Evidence Bundle · NEX-M03-FINAL-REFERENCE-WO-001

**Status:** `M03_LIGHTING_REFERENCE_EVIDENCE / NATIVE_GPU / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M03 #8 · **Base:** `6be39d49d8769ff46a98990c6818c8132e9e5a1d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **CineLight:** 9 capturas 1920×1080 (3 looks × 3 cenas) em `...m03-looks`.
- **ShadowStability:** 6 capturas low/ultra em `...m03-shadows`.
- **GI Atlas:** 6 capturas SDFGI/off em `...m03-gi`.
- **FogWeave:** 9 capturas volumetric/depth/off em `...m03-fog`.
- **LightBudget:** 6 capturas budget on/off em `...m03-budget`.
- **Performance:** 11 runs nativos em `...m03-perf`, validados 11/11.
- **LightBridge:** `bridge-smoke-2026-11-15.json`, 13/13 checks.
- **Builder:** `build_lighting_runtime.py`, `lighting-runtime.v1.json` e `LIGHTING-RUNTIME.md`.
- **Gate:** `M03-FINAL-GATE.md`; issues #36–#43 e #8 fechadas após integração.
- **Governança:** `NEX-ADR-0014`, `NEX-D-025`, WO/lock/evidência/delta.

## Resultado

- **CineLight:** 3 looks originais; GPU p95 **3.039–3.129 ms** no corredor; moonlit/boss diferem de dungeon em 51–100% dos pixels.
- **ShadowStability:** low **1.526 ms** → ultra **3.144 ms** (+106.0%); temporal `NOT_RUN`.
- **GI:** off **1.976 ms** → SDFGI **3.140 ms** (+58.9%); alocação **+451.1 MiB**; decisão qualidade-only.
- **Fog:** depth **3.008 ms** → volumetric **3.145 ms** (+4.6%); fallback depth.
- **LightBridge:** 13/13 checks com dois consumidores mock.
- **LightBudget:** 4→2 tochas com sombra, **3.150 → 3.020 ms** (-4.1%); `RESEARCH_MORE`.
- **36 capturas** e **11 runs** nativos; nenhum asset de terceiros.

## Verificação

- `build_lighting_runtime.py --check`: `M03_LIGHTING_RUNTIME_CHECK_PASS: 11 runs`.
- LightBridge smoke: `M03_LIGHT_BRIDGE_SMOKE_PASS 13 checks`.
- Validação canônica dos 11 runs: PASS.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum asset, shader, cena ou paridade com PoE2.
- Nenhuma arte de produção, personagem, VFX/telegraph real.
- Nenhum bake LightmapGI/VoxelGI, GI dinâmica completa ou oclusão dinâmica.
- Nenhum renderer/runtime M04–M12, jogo, gameplay ou rede.
- Nenhum claim generalizado de FPS/qualidade ou cross-device.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter as flags de look/GI/fog/torch/budget, os evidence bundles, o LightBridge, o builder/relatórios, o teste, o workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento das issues.

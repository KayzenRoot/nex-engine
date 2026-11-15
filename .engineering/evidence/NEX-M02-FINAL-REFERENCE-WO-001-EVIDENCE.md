# Evidence Bundle · NEX-M02-FINAL-REFERENCE-WO-001

**Status:** `M02_RENDERER_REFERENCE_EVIDENCE / NATIVE_GPU / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M02 #7 · **Base:** `fa1adae7ab67e38c2556d126627006c338e2e8f4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **S01:** camera math (round-trip, fast follow, aspect extents) e 4 capturas de aspect ratio.
- **S02:** 6 capturas hidden/revealed nas 3 cenas + 9 runs de performance.
- **S03:** 6 capturas overlay off/on nas 3 cenas + 9 runs de performance.
- **S04:** 10 frames de TAA off/on + 2 análises temporais.
- **S05:** 9 capturas de perfis + 9 runs de performance + capability passport runtime.
- **Builder:** `build_m02_runtime.py`, `runtime.v1.json` e `RUNTIME.md`.
- **QA ledger:** S01–S05 com `scene_comparison=PASS` e evidência; S04 performance `INCONCLUSIVE_NOT_RUN`.
- **Gate:** `M02-FINAL-GATE.md`; issues #28–#34 e #7 fechadas após integração.
- **Governança:** `NEX-ADR-0013`, `NEX-D-023`, WO/lock/evidência/delta.

## Resultado

- **S01:** round-trip **3e-6 m**; fast follow **24.325 px**; 16:9, 16:10, 21:9 e 4:3 capturados.
- **S02:** reveals **0→1**; pixels alterados **1.141%/0.456%/0.123%**; GPU delta **+8.6%/+6.0%/+8.2%**.
- **S03:** pixels alterados **0.370%/0.556%/0.741%**; 0 z-fight/alpha/overlay; GPU delta **+1.4%/+0.0%/+3.3%**.
- **S04:** TAA off/on com ghosting 0.0, flicker 0.667, shimmer 0.050/0.053; **NO_GO_CUSTOM_COMPOSITOR**.
- **S05:** passport **RUNTIME_PROBED** em Forward+/Vulkan; GPU p95 **0.758/0.571/0.182 ms**; alocação **219.7/130.6/47.4 MiB**.
- **27 runs** de performance validados 9/9 por bundle.

## Verificação

- `build_m02_runtime.py --check`: `M02_RUNTIME_CHECK_PASS: 27 runs`.
- `qa_ledger.py --check`: `QA_LEDGER_OK`.
- Validação canônica dos 27 runs: PASS.
- Suíte CI completa e builders/validadores verdes antes da PR.
- Nenhuma cena base, contrato, renderer de M03–M12 ou shader customizado alterado.

## O que não foi feito / não é alegado

- Nenhum renderer/runtime de M03–M12, compositor customizado, GI, sombra/VFX real.
- Nenhum jogo, gameplay, rede ou cena de produção.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou input-to-photon.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; não há revisor independente.

## Rollback

Reverter as flags do harness, os evidence bundles, builders/relatórios, QA ledger, testes, workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento das issues.

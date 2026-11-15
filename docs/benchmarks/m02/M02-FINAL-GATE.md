# NEX M02 · Final reference gate

**Status:** `M02_RUNTIME_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-15 · **Base:** `fa1adae7ab67e38c2556d126627006c338e2e8f4`
**Parent:** #7 · **Sub-issues:** #28 S01, #29 S02, #30 S03, #31 S04, #32 S05, #33 S06, #34 S07.

## O que foi concluído

| Sub-issue | Entrega | Evidência |
|---|---|---|
| #28 S01 | Câmera estável, 3D↔tela, fast follow, 4 aspect ratios | `runtime.v1.json` S01; `camera-math-2026-11-15.json` |
| #29 S02 | Reveal renderizado com parede de teste, fade e GPU delta | `runtime.v1.json` S02; bundle `...m02-sightline` |
| #30 S03 | Overlay alpha renderizado, sorting e conflitos | `runtime.v1.json` S03; bundle `...m02-depth` |
| #31 S04 | TAA nativo off/on em sequência de câmera | `runtime.v1.json` S04; bundle `...m02-temporal-taa` |
| #32 S05 | Capability passport runtime e três perfis | `runtime.v1.json` S05; `runtime-probe-2026-11-15.json` |
| #33 S06 | Matriz de decisões GO/NO_GO | `runtime.v1.json` S06 |
| #34 S07 | QA ledger S01–S05, interface e gate | `qa-ledger.v1.json`; este gate |

## Resultado

- **S01:** round-trip 3D↔tela **3e-6 m**; fast follow máximo **24.325 px** por passo; 4 aspect ratios capturados.
- **S02:** reveals **0→1** nas três cenas; pixels alterados **1.141%/0.456%/0.123%**; GPU delta **+8.6%/+6.0%/+8.2%**.
- **S03:** pixels alterados **0.370%/0.556%/0.741%**; 0 z-fight, 0 alpha-over-critical, 0 overlay/gameplay; GPU delta **+1.4%/+0.0%/+3.3%**.
- **S04:** TAA off/on com ghosting 0.0, flicker 0.667, shimmer 0.050/0.053; métricas idênticas; **`NO_GO_CUSTOM_COMPOSITOR`**.
- **S05:** passport **RUNTIME_PROBED** em Forward+/Vulkan; perfis quality/balanced/performance com GPU p95 **0.758/0.571/0.182 ms** e alocação **219.7/130.6/47.4 MiB**.

## Decisões

- **GO:** IsoDirector (câmera), Sightline, DepthWeave, RenderPassport.
- **NO_GO:** TemporalGuard custom compositor; TAA nativo permanece disponível.
- **Pesquisa:** S06 mantém a matriz de hipóteses e rejeita redundâncias.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; frames estáticos para S01/S02/S03/S05.
- O analyzer temporal usa regiões 4×4 de luminância, não buffers por pixel.
- O overlay de profundidade e a parede de sightline são fixtures determinísticas, não arte de produção.
- Nenhum claim de jogo, gameplay, M03–M12 ou cross-device.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; não há revisor independente.

## Fechamento

Com este gate, as issues **#28, #29, #30, #31, #32, #33, #34 e #7** podem ser fechadas como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M03** (iluminação cinematográfica e volumetria), que deve consumir este baseline e o budget M01.

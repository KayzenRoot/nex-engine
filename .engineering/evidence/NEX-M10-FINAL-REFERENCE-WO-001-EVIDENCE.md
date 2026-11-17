# Evidence Bundle · NEX-M10-FINAL-REFERENCE-WO-001

**Status:** `M10_ANIMATION_REFERENCE_EVIDENCE / NATIVE_ANIMATION_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M10 #15 · **Base:** `de81ee67b1c469636678df5a437cfc6fd77f06b8`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **FeedbackPlanner:** 66 checks headless; fases, hits, canais e budgets.
- **AnimationTree blending:** rig proxy de dois ossos, `AnimationPlayer` e `AnimationNodeBlend2`.
- **Hit reaction:** recuo animado no rig.
- **Visual hit-stop:** pausa visual de 80 ms, sem física/gameplay.
- **Smooth camera:** follow suave com captura nativa.
- **M05 VFX sync:** impacto M05 via contrato SpellFX.
- **Quality profiles:** low/high com proxies animados.
- **Evidência:** 9 runs nativos validados, 9 capturas 1920×1080, manifest e SHA256SUMS.
- **Builder/Gate:** `build_m10_runtime.py`, `M10-RUNTIME.md`, `m10-runtime.v1.json`, `M10-FINAL-GATE.md`.
- **Governança:** `NEX-ADR-0021`, `NEX-D-032`, WO/lock/evidência/delta.

## Resultado

- **S01:** FeedbackPlanner 66 checks.
- **S02:** baseline **0.256 ms**; blend **0.264 ms** (+3.13%, 0.493% de pixels); attack **0.256 ms** (0.931%).
- **S03:** hit **0.256 ms**; **0.414%** de pixels.
- **S04:** hit-stop **0.255 ms** vs attack **0.256 ms**; **0.000%** de pose; timing/pacing apenas.
- **S05:** camera **0.273 ms** (+6.64%); **2.661%** de pixels.
- **S06:** VFX **0.262 ms** (+2.34%); **3.681%** de pixels; SpellFX event accepted.
- **S07:** quality low/high **0.264/0.274 ms**.
- **S08:** 9 runs, 9 imagens, 66 checks, 0 assets de terceiros.

## Verificação

- `m10_lab.gd`: `NEX_M10_LAB` em 9 modos; `NEX_M10_CAPTURE` em 9 runs.
- `validate_m10_lab.py`: 9/9 runs `PASS`.
- `build_m10_runtime.py --check`: `M10_ANIMATION_RUNTIME_CHECK_PASS: 9 runs`.
- FeedbackPlanner: `NEX_M10_FEEDBACK_SMOKE_PASS: 66 checks`.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum dano, hitbox, física, netcode ou gameplay.
- Nenhum personagem de produção, skin, rig completo ou asset de terceiros.
- Nenhum M11/M12, renderer core, shader customizado ou cena de produção.
- Nenhum input-to-photon, VRAM, cross-device ou claim generalizado.
- Nenhum asset, shader, cena ou paridade com PoE2.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter o laboratório M10, o layout no `session.gd`, as evidências, o builder/relatórios, o teste, o workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento da issue.

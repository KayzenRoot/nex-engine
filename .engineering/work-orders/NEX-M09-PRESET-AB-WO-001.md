# NEX-M09-PRESET-AB-WO-001 | Harness A/B/A de presets com medição real

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; integração de medição A/B/A sobre `preset_pack.v1`.
**Base:** `main` `0cb02ec87fe950bc63f23b707120098993b71007`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada; sem mudança de renderer/engine).
**Lock:** `.engineering/context-locks/NEX-M09-PRESET-AB-WO-001-EXECUTION.json` (31 fingerprints).

## Objetivo

Adicionar uma cena de medição A/B/A autocontida ao `nex_bench`, aplicar presets `preset_pack.v1` em runtime (resolução, MSAA, sombras, atlas, glow, tonemap), desligar vsync, limitar a 240 fps e capturar três runs (`ab-low`, `ab-high`, `ab-low`) com o profiler existente na RTX 5050. Produzir análise reproduzível com deltas e limitações.

## Escopo

- `nex_bench/scenes/preset_ab/**`: cena, script, validador dedicado e README.
- `nex_bench/presets/preset_ab/presets.v1.json`.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/**`: 3 capturas, validações, SHA-256, fatos da sessão e análise.
- `docs/benchmarks/m09/**`: relatório A/B/A e builder reproduzível.
- `tests/ci/test_preset_ab_harness.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar `nex_bench/project.godot`, `hub.gd`, renderer, shaders, engine ou CI.
- Claims de ganho geral, FPS de jogo ou generalização entre cenas/hardware.
- M09 parent admission.

## DoD

- Harness determinístico e validador dedicado delegando ao validador canônico.
- Três capturas COMPLETE na RTX 5050 com SHA-256 e análise de deltas.
- Builder reproduzível e testes estruturais verdes.
- Suítes completas verdes em worktree LF limpo; PR com checks verdes, squash protegido e checkpoint.

## STOP

- Captura falhar/incompleta, viewport mudar, validador rejeitar ou risco de generalização → parar e registrar.

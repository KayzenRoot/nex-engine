# NEX-M10-FINAL-REFERENCE-WO-001 | Fechamento da animação e feedback M10

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0021` / `NEX-D-032`; instrução do Owner de 2026-11-17 para finalizar o M10 com animação nativa, sem paridade com PoE2.
**Base:** `main` `de81ee67b1c469636678df5a437cfc6fd77f06b8`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (9 runs nativos e capturas).
**Lock:** `.engineering/context-locks/NEX-M10-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M10 como animação e feedback de referência: rig proxy com AnimationPlayer/AnimationTree, blending, hit reaction, hit-stop visual, câmera suave, sincronização M05 VFX e perfis de qualidade; 9 runs, 9 capturas, validador, relatório/gate e fechamento de #15.

## Escopo

- `nex_bench/scenes/m10_animation/m10_lab.gd`, `m10_lab.tscn`, `validate_m10_lab.py`.
- `nex_bench/gpu_profile/session.gd`: layout `M10 animation and feedback lab` permitido.
- Evidence `windows-rtx5050-2026-11-17-m10/`: 9 runs, 9 imagens, logs, manifest e SHA256SUMS.
- `docs/benchmarks/m10/tools/build_m10_runtime.py`, `M10-RUNTIME.md`, `m10-runtime.v1.json`, `M10-FINAL-GATE.md`.
- `tests/ci/test_m10_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #15.

## Fora de escopo

- Dano, hitbox, física, netcode ou gameplay.
- Personagem de produção, skin, rig completo, asset de terceiros.
- M11/M12, renderer core, shader customizado, cena de produção.
- Input-to-photon, VRAM, cross-device, PoE2 ou claims generalizados.

## DoD

- 9 runs validados e 9 imagens 1920×1080; FeedbackPlanner 66 checks.
- Baseline GPU p95 **0.256 ms**; blend **0.264 ms**; attack **0.256 ms**; hit **0.256 ms**; hitstop **0.255 ms**; camera **0.273 ms**; vfx **0.262 ms**.
- Quality low/high **0.264/0.274 ms**.
- Diffs: blend **0.493%**; attack **0.931%**; hit **0.414%**; camera **2.661%**; vfx **3.681%**; quality_high **7.934%**.
- Hit-stop vs attack: **0.000%** de pose; timing/pacing apenas.
- Builders `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issue #15 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, run não validado, imagem ausente, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.

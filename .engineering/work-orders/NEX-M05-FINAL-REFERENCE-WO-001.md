# NEX-M05-FINAL-REFERENCE-WO-001 | Fechamento dos VFX de referência M05

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0016` / `NEX-D-027`; instrução do Owner de 2026-11-15 para finalizar o M05 com qualidade, sem paridade com PoE2.
**Base:** `main` `dd840f86023057a4dc8af92148cdf36911175613`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** ELEVATED (partículas nativas, luzes dinâmicas e stress de 100 eventos).
**Lock:** `.engineering/context-locks/NEX-M05-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M05 como VFX de referência: ponte SpellFX com autoridade data-only, biblioteca elemental nativa de seis efeitos, integração com LightBridge, capturas em três cenas, stress de 1/25/100 eventos com baseline, R&D/QA e fechamento de #52–#58 e #10 após integração protegida.

## Escopo

- `nex_bench/scenes/m05_vfx/spell_fx.gd`, `fx_library.gd`, `spell_fx_smoke.gd`.
- `nex_bench/scenes/preset_ab/preset_ab.gd`: flags `NEX_PRESET_AB_VFX`/`NEX_PRESET_AB_VFX_COUNT` e integração SpellFX/LightBridge.
- Evidence `windows-rtx5050-2026-11-15-m05-vfx/`: 19 PNGs + logs + smoke.
- Evidence `windows-rtx5050-2026-11-15-m05-vfx-perf/`: 9 runs + validações + manifest + SHA256SUMS.
- Evidence `windows-rtx5050-2026-11-15-m05-vfx-baseline/`: 3 runs sem VFX.
- `docs/benchmarks/m05/tools/build_m05_runtime.py`, `VFX-RUNTIME.md`, `vfx-runtime.v1.json`, `M05-FINAL-GATE.md`.
- `tests/ci/test_m05_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de issues.

## Fora de escopo

- Assets, shaders, cenas ou paridade com PoE2.
- Hit autoritativo, física/colisão de projétil, dano ou hitbox.
- Telegraphs, redução de flashes, ThreatBudget Scheduler ou acessibilidade.
- Warm pool, prewarm de shader, overdraw, VRAM ou import/cook.
- Renderer/runtime M06–M12, jogo, gameplay, rede ou cloud.
- Claims generalizados de FPS/qualidade ou cinematográfico.

## DoD

- SpellFX smoke `12/12 checks` PASS; autoridade de gameplay data-only.
- Seis elementos renderizados em três cenas; 19 capturas 1920×1080; todas com pixels alterados > 0.
- 25 eventos com 8 luzes alteram 28.055% do frame da arena.
- Stress 1/25/100: GPU p95 **3.620/3.839/3.992 ms**; 1% low **220.73/221.40/104.48 FPS**; baseline **3.210 ms / 219.73 FPS**.
- Builders `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issues #52–#58 e #10 fechadas com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, captura sem efeito, validação de stress falhando, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.

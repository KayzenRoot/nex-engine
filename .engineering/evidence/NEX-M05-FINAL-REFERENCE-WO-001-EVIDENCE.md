# Evidence Bundle · NEX-M05-FINAL-REFERENCE-WO-001

**Status:** `M05_VFX_REFERENCE_EVIDENCE / NATIVE_CAPTURES / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M05 #10 · **Base:** `dd840f86023057a4dc8af92148cdf36911175613`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** ELEVATED

## Entregue

- **SpellFX:** `spell_fx.gd` com idempotência, autoridade data-only, budgets 128/64, tiers e ciclo de vida; `spell-fx-smoke-2026-11-15.json` com **12/12 checks**.
- **Biblioteca elemental:** `fx_library.gd` com fire/frost/lightning/smoke/impact/projectile em `GPUParticles3D` nativo e textura radial procedural.
- **Integração:** `preset_ab.gd` com `NEX_PRESET_AB_VFX`, `NEX_PRESET_AB_VFX_COUNT`, SpellFX e LightBridge M03.
- **Capturas:** 19 PNGs 1920×1080 (6 elementos × 3 cenas + 25 eventos na arena) e 3 baselines sem VFX.
- **Stress:** 9 runs (1/25/100 eventos × 3) e 3 runs baseline, com validação canônica, `runs.v1.json` e `SHA256SUMS.txt`.
- **Builder/Gate:** `build_m05_runtime.py`, `VFX-RUNTIME.md`, `vfx-runtime.v1.json`, `M05-FINAL-GATE.md`.
- **Governança:** `NEX-ADR-0016`, `NEX-D-027`, WO/lock/evidência/delta.

## Resultado

- **S01:** 12 checks PASS; 6 eventos e 6 luzes na captura; dano/hit permanecem gameplay-owned.
- **S02:** 6 elementos originais; diferença mediana por elemento 1.000–7.065% (máximo 36.666% no lightning do corredor).
- **S03:** projétil com 24 partículas + 2 meshes; impacto com 40 partículas; sem hit autoritativo ou colisão.
- **S04:** 25 eventos com 8 luzes alteram **28.055%** do frame da arena; sem telegraphs ou redução de flashes.
- **S05:** GPU p95 **3.620/3.839/3.992 ms** para 1/25/100 eventos; 1% low **220.73/221.40/104.48 FPS**; baseline **3.210 ms / 219.73 FPS**.
- **Alocação:** +44.944 B (1), +1.776.912 B (25), +8.422.816 B (100) versus baseline.
- Nenhum asset de terceiros; textura radial e materiais são procedurais.

## Verificação

- `spell_fx_smoke.gd`: `M05_SPELLFX_SMOKE_PASS 12 checks`.
- `build_fx_budget_dataset.py --check`: `M05_FX_BUDGET_DATASET_CHECK_PASS: 3 archetypes`.
- `build_m05_runtime.py --check`: `M05_VFX_RUNTIME_CHECK_PASS: 12 runs`.
- `validate_preset_ab.py`: 9/9 stress e 3/3 baseline `PASS`.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum asset, shader, cena ou paridade com PoE2.
- Nenhum hit autoritativo, física de projétil, dano, hitbox ou colisão de partícula.
- Nenhum telegraph, redução de flashes, ThreatBudget Scheduler ou acessibilidade.
- Nenhum warm pool, prewarm de shader, overdraw, VRAM ou import/cook.
- Nenhum renderer/runtime M06–M12, jogo, gameplay, rede ou cloud.
- Nenhum claim generalizado de FPS/qualidade, cinematográfico ou cross-device.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter SpellFX, biblioteca, integração no harness, evidências, builder/relatórios, teste, workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento das issues.

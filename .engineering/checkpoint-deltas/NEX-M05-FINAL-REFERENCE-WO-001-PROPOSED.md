# Checkpoint Delta · NEX-M05-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `dd840f86023057a4dc8af92148cdf36911175613`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M05 full reference admitido:** `NEX-ADR-0016` / `NEX-D-027`, bounded aos VFX de referência.
2. **SpellFX:** ponte `spellfx.v1` com 12 checks, idempotência, autoridade data-only, budgets 128/64 e ciclo de vida.
3. **Biblioteca elemental:** seis efeitos originais em `GPUParticles3D` nativo; 19 capturas em três cenas e 3 baselines.
4. **LightBridge:** 6 luzes para 6 eventos e 8 luzes para 25/100 eventos, sem sombras.
5. **Stress:** GPU p95 **3.620/3.839/3.992 ms** e 1% low **220.73/221.40/104.48 FPS** para 1/25/100 eventos; baseline **3.210 ms / 219.73 FPS**.
6. **Combat clarity:** 25 eventos com 8 luzes alteram 28.055% do frame; telegraphs/flash reduction não implementados.
7. **Gate:** `M05-FINAL-GATE.md`; issues #52–#58 e #10 fechadas após squash e checks.
8. **Sem assets/shaders/cenas de PoE2, sem paridade com PoE2, sem hit autoritativo ou física de projétil.**

## O que NÃO muda

- M06–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime de jogo, gameplay ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M05-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/scenes/m05_vfx/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx-perf/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx-baseline/`
- `docs/benchmarks/m05/vfx-runtime.v1.json`
- `docs/benchmarks/m05/M05-FINAL-GATE.md`
- `tests/ci/test_m05_final.py`

# Checkpoint Delta · NEX-M10-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `de81ee67b1c469636678df5a437cfc6fd77f06b8`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M10 full reference admitido:** `NEX-ADR-0021` / `NEX-D-032`, bounded à animação e feedback de referência.
2. **FeedbackPlanner:** 66 checks headless.
3. **AnimationTree blending:** blend 0.5 em 0.493% de pixels, +3.13% GPU.
4. **Hit reaction:** 0.414% de pixels; GPU neutro no lab.
5. **Visual hit-stop:** 0.000% de pose vs attack; timing/pacing apenas.
6. **Smooth camera:** +6.64% GPU e 2.661% de pixels.
7. **M05 VFX sync:** +2.34% GPU e 3.681% de pixels; SpellFX event accepted.
8. **Quality profiles:** low/high 0.264/0.274 ms.
9. **Gate:** `M10-FINAL-GATE.md`; issue #15 fechada após squash e checks.

## O que NÃO muda

- M11–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum dano, física, netcode, gameplay, personagem de produção ou asset de terceiros é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M10-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/scenes/m10_animation/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-17-m10/`
- `docs/benchmarks/m10/m10-runtime.v1.json`
- `docs/benchmarks/m10/M10-FINAL-GATE.md`
- `tests/ci/test_m10_final.py`

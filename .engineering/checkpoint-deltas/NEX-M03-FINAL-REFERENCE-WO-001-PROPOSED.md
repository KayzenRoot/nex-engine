# Checkpoint Delta · NEX-M03-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `6be39d49d8769ff46a98990c6818c8132e9e5a1d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03 full reference admitido:** `NEX-ADR-0014` / `NEX-D-025`, bounded à iluminação cinematográfica.
2. **CineLight:** 3 looks originais de dark fantasy × 3 cenas; GPU p95 3.039–3.129 ms.
3. **ShadowStability:** low 1.526 ms → ultra 3.144 ms (+106.0%); temporal `NOT_RUN`.
4. **GI Atlas:** off 1.976 ms → SDFGI 3.140 ms (+58.9%), +451.1 MiB; qualidade-only.
5. **FogWeave:** volumetric +4.6% vs depth; fallback depth.
6. **LightBridge:** 13/13 checks com dois consumidores mock.
7. **LightBudget:** 2 vs 4 tochas, -4.1% GPU; `RESEARCH_MORE`.
8. **Gate:** `M03-FINAL-GATE.md`; issues #36–#43 e #8 fechadas após squash e checks.
9. **Sem assets/shaders/cenas de PoE2, sem paridade com PoE2, sem arte de produção.**

## O que NÃO muda

- M04–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime de jogo, gameplay ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m03-*`
- `docs/benchmarks/m03/lighting-runtime.v1.json`
- `docs/benchmarks/m03/M03-FINAL-GATE.md`
- `tests/ci/test_m03_final.py`

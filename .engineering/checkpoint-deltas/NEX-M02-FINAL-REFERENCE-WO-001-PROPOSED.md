# Checkpoint Delta · NEX-M02-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `fa1adae7ab67e38c2556d126627006c338e2e8f4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M02 full reference admitido:** `NEX-ADR-0013` / `NEX-D-023`, bounded ao renderer de referência.
2. **S01:** round-trip 3e-6 m, fast follow 24.325 px, 4 aspect ratios.
3. **S02:** reveal renderizado 0→1 nas 3 cenas; GPU delta +6.0–8.6%.
4. **S03:** overlay alpha com 0 conflitos; GPU delta +0.0–3.3%.
5. **S04:** TAA nativo off/on; compositor customizado NO_GO; performance INCONCLUSIVE.
6. **S05:** passport RUNTIME_PROBED; perfis quality/balanced/performance com GPU p95 0.758/0.571/0.182 ms.
7. **QA ledger:** S01–S05 rendered/measured; S04 performance INCONCLUSIVE.
8. **Gate:** `M02-FINAL-GATE.md`; issues #28–#34 e #7 fechadas após squash e checks.
9. **Sem mudança de cena base, contrato, renderer M03–M12, shader customizado, ruleset ou permissão de CI.**

## O que NÃO muda

- M03–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime de jogo, gameplay ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-*`
- `docs/benchmarks/m02/runtime.v1.json`
- `docs/benchmarks/m02/M02-FINAL-GATE.md`
- `docs/benchmarks/m02/qa-ledger.v1.json`
- `tests/ci/test_m02_final.py`

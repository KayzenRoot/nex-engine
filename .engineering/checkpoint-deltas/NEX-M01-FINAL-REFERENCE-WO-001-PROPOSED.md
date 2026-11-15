# Checkpoint Delta · NEX-M01-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `900d2b2d031a87048702625a1e98bc50905bc663`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M01 full reference admitido:** `NEX-ADR-0012` / `NEX-D-022`, bounded ao laboratório M01.
2. **S01/S03:** golden matrix 1920×1080 com 18 capturas, A/A byte-idêntico, A/B full + 5 regiões e 3 imagens de aceitação.
3. **S07:** 9 runs de performance validados; budget 1080p `OWNER_APPROVED`; meta experimental 120 FPS medida no workload de referência.
4. **Licenças:** 0 assets de terceiros; materiais originais.
5. **Gate final:** `M01-FINAL-GATE.md`; issues #21/#23/#27/#6 fechadas após squash e checks.
6. **Sem mudança de cena/harness/preset/contrato/renderer/shader; sem claim generalizado de FPS/qualidade.**

## O que NÃO muda

- M02–M12 continuam bounded e exigem WO própria para rendering/runtime.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime de jogo, gameplay ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M01-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-golden/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-perf-1080/`
- `docs/benchmarks/m01/golden-matrix.v1.json`
- `docs/benchmarks/m01/final-budget.v1.json`
- `docs/benchmarks/m01/LICENSE-AUDIT.md`
- `docs/benchmarks/m01/M01-FINAL-GATE.md`
- `tests/ci/test_m01_final.py`

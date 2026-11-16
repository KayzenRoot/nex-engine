# Checkpoint Delta · NEX-M06-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `c763319d04d0bf353c15db8378872bdf8fab1734`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06 full reference admitido:** `NEX-ADR-0017` / `NEX-D-028`, bounded à performance de referência.
2. **Bottleneck Atlas:** 33 runs nativos, 22 GPU e 11 pacing.
3. **BatchWeave:** draw calls 385→223 no corredor, diff visual 0.000% e CPU -6.1%.
4. **LOD Governor:** GPU p95 -8.17%/-7.10%/-1.00%; pixels 3.458%/4.314%/0.967%.
5. **Occlusion Mapper:** **NO_GO** para frustum customizado; arena false-hide 2.284%; oclusão baked `INCONCLUSIVE`.
6. **StreamGuard:** 17 checks; cargas frias 14.0–21.0 ms.
7. **FramePacer:** render scale 0.85/0.70 com GPU -15.41%/-28.23%; pixels 2.478%/3.748%.
8. **VRAM Sentinel:** 12.6 MB → 211.5 MB ao carregar 22 texturas (+198.9 MB).
9. **FillRate X-Ray:** 1440p +135.9% vs 720p em 1 evento; 100 vs 1 evento em 1080p +11.1%.
10. **Gate:** `M06-FINAL-GATE.md`; issues #59–#68 e #11 fechadas após squash e checks.

## O que NÃO muda

- M07–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum renderer core, GDExtension, LOD de produção, oclusão baked, streaming de cena ou gameplay é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/scenes/m06_performance/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-16-m06/`
- `docs/benchmarks/m06/m06-runtime.v1.json`
- `docs/benchmarks/m06/M06-FINAL-GATE.md`
- `tests/ci/test_m06_final.py`

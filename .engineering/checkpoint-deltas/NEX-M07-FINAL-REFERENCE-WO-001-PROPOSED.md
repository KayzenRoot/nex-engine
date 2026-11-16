# Checkpoint Delta · NEX-M07-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `aa6256a82f6cd34e347b05ac43375ac4042d2ede`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M07 full reference admitido:** `NEX-ADR-0018` / `NEX-D-029`, bounded ao render2d de referência.
2. **CanvasPlanner:** 46 checks headless.
3. **2D lighting:** baseline 0.060 ms → lighting 0.075 ms; 16.218% de pixels.
4. **2D shadows:** 0.100 ms; +33.3% vs lighting; shadows vs lighting 9.028% de pixels.
5. **Normal maps:** 0.082 ms; +9.3% vs lighting; 14.542% de pixels.
6. **GPUParticles2D:** 0.071 ms; 384 partículas; 0.979% de pixels.
7. **Parallax:** 0.070 ms; 3 camadas; 23.006% de pixels.
8. **Quality profiles:** low/medium/high 0.065/0.081/0.153 ms.
9. **Gate:** `M07-FINAL-GATE.md`; issue #12 fechada após squash e checks.

## O que NÃO muda

- M08–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum renderer 2D de produção, atlas packing, y-sort, shader customizado ou gameplay é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M07-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_bench/scenes/m07_2d/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-16-m07/`
- `docs/benchmarks/m07/m07-runtime.v1.json`
- `docs/benchmarks/m07/M07-FINAL-GATE.md`
- `tests/ci/test_m07_final.py`

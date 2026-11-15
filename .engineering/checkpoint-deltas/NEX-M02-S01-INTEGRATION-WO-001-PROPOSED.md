# Checkpoint Delta · NEX-M02-S01-INTEGRATION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `ad41089a3a37407ce8773ea86ac364873971551d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M02-S01 integrado:** modo aditivo `baseline|rig` no harness, rig vendorizado e A/B/A nas três cenas M01.
2. **Visual:** A/A byte-idêntico; A/B mean abs 0.002/0.0003/0.0; changed pixels 0.013%/0.003%/0.0%.
3. **Performance:** GPU p95 delta 0.0%/+0.94%/+1.25%; CPU 0.0%/+13.3%/+12.94%.
4. **QA ledger:** S01 `scene_comparison=PASS`, `performance=MEASURED`; S02–S05 permanecem `INCONCLUSIVE_NOT_RUN`; S06 research-only.
5. **Sem mudança de cena base, preset, contrato, renderer, shader ou ruleset.**
6. **Sem claim de FPS, qualidade, ganho ou generalização.**

## O que NÃO muda

- M01/M02/M03/M04/M05/M06/M09 seguem bounded admitted; M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M02-S01-INTEGRATION-WO-001-EVIDENCE.md`
- `docs/benchmarks/m02/camera-integration.v1.json`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-camera-visual/`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-camera-perf/`
- `tests/ci/test_m02_camera_integration.py` (6 testes)

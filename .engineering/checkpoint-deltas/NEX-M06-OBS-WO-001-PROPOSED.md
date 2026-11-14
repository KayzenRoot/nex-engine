# Checkpoint Delta · NEX-M06-OBS-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `3aa83afaabbe3a0b65afb3d9250158b66da6dde6`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06-OBS integrado:** 12 observações `performance.v1` convertidas de capturas M09 já integradas, com schema e coerência validados.
2. **Semântica:** timings p95, alocação p50, campos não medidos `UNAVAILABLE` com razão; todas as 12 observações classificadas como `pacing` no cap de 240 fps.
3. **Sem nova medição:** conversão determinística de evidência existente; nenhum contrato, engine, cena ou CI alterado.
4. **Parent M06 (#59) permanece NOT_ADMITTED.** Nenhum draw call/VRAM medido ou fabricado.
5. **Sem generalização:** seleção de 12 runs de uma sessão única em uma RTX 5050.

## O que NÃO muda

- M01–M05/M07–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-OBS-WO-001-EVIDENCE.md`
- `docs/benchmarks/m06/observations/m09-observations.v1.json`
- `tests/ci/test_m06_observations.py` (6 testes)

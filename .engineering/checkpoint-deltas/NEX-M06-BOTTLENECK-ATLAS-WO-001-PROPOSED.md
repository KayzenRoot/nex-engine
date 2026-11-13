# Checkpoint Delta · NEX-M06-BOTTLENECK-ATLAS-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `2a93668c1f72f1bb4e66ab5e35e037937c99c81f` · **Code SHA:** `99c9fcb4adc81a161ad5cb11f0010fdef9fe0b98`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06-BOTTLENECK-ATLAS integrado:** 15 runs S05 recomputadas, 32 hashes verificados, validação S05 conferida, classificação `pacing` e deltas baseline reproduzíveis.
2. **Parent M06 (#11) permanece NOT_ADMITTED.** Nenhuma captura nova, engine, CI ou `project.godot`.
3. **Contrato `performance.v1` operacionalizado:** vocabulário de classificação/evidência/confiança usado no atlas; contrato inalterado.
4. **Performance:** dados derivados da sessão S05; nenhum benchmark, FPS ou generalização.
5. **Próximos incrementos:** atlas para workloads GPU-bound, LOD/culling/streaming e M08/M12 exigem WO própria.

## O que NÃO muda

- M01–M05/M07 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-BOTTLENECK-ATLAS-WO-001-EVIDENCE.md`
- `docs/benchmarks/m06/atlas.v1.json`
- `docs/benchmarks/m06/ATLAS.md`
- `tests/ci/test_m06_atlas.py` (12 testes)

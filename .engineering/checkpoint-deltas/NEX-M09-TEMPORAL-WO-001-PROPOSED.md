# Checkpoint Delta · NEX-M09-TEMPORAL-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `cefd2a045a410147b96577a547239f75be5215d5`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-TEMPORAL integrado:** 30 PNGs (5 frames por cena/preset), modo de sequência determinístico no harness e relatório frame-a-frame.
2. **Medição:** todas as frames de cada célula são byte-idênticas; nenhuma variação temporal no workload estático.
3. **Atlas atualizado:** 10 bundles, 66 imagens, 384 arquivos e 10 source SHAs.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** cenas estáticas, sessão única, sem animação ou efeitos dinâmicos.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-TEMPORAL-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-temporal/`
- `docs/benchmarks/m09/temporal-stability.v1.json` e `TEMPORAL-STABILITY-REPORT.md`
- `tests/ci/test_temporal_stability.py` (8 testes)

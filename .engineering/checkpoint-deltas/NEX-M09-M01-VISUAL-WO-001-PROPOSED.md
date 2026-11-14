# Checkpoint Delta · NEX-M09-M01-VISUAL-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `647670eecf051849970e659e5ef5b98da4413367` · **Harness source SHA:** `952b5a63bc1696cadf7436a061a7d996c80fa220`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-M01-VISUAL integrado:** 18 PNGs 1280×720 das três cenas M01 sob `ab-low`/`ab-high`, com A/A byte-idêntico e comparação A/B de pixels.
2. **Medição:** A/A exato em todas as 18 imagens; A/B mean abs 0.5135/0.4898/0.2317 e 4.077%/3.884%/1.745% de pixels alterados (corridor/arena/city).
3. **Ferramentas:** decoder PNG mínimo e builder determinístico; relatório reproduzível `m01-visual.v1.json`.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem claim de qualidade:** frame estático, sessão única, comparação RGB byte a byte.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-M01-VISUAL-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual/`
- `docs/benchmarks/m09/m01-visual.v1.json` e `M01-VISUAL-REPORT.md`
- `tests/ci/test_m01_visual.py` (11 testes)

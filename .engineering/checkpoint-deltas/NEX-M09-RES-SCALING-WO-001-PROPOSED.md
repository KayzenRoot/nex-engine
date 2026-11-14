# Checkpoint Delta · NEX-M09-RES-SCALING-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `f796de1445ff3147b87d8e7a3afe08e83a9284a5` · **Measured source SHA:** `6ebb98e8c7c9c6a9a0aa3faae5af7e8d4290b7f5`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-RES-SCALING integrado:** 18 capturas reais em 960×540/1280×720/1920×1080 na cena `arena_combat`, viewport nativo, 3 runs por preset por resolução.
2. **Medição:** delta GPU p95 high vs low +230.2%/+334.0%/+429.5%; escala 960→1920 +62.5% (low) e +160.6% (high); pacing ~4.2 ms.
3. **Proveniência:** o stretch `canvas_items` foi desabilitado no harness para registrar o viewport real; a primeira tentativa sem o flag foi descartada.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** sessão única, uma cena, máximo 1920×1080.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-RES-SCALING-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling/`
- `docs/benchmarks/m09/res-scaling.v1.json` e `RES-SCALING-REPORT.md`
- `tests/ci/test_res_scaling.py` (10 testes)

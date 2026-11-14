# Checkpoint Delta · NEX-M09-M01-AB-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `51587de8cc8f713d3573a0bb6a52e7f19bb783a6` · **Measured source SHA:** `617db53d6752f30584b296f133e6990ca6602549`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-M01-AB integrado:** harness A/B/A com as três cenas M01, fillers determinísticos até 100 meshes, layout de workload validado e 18 capturas reais (3 por preset por cena).
2. **Medição:** GPU p95 high vs low +380.7% (corridor), +323.9% (arena), +331.0% (city); pacing ~4.2 ms; A/A spread de GPU p95 1.2–7.3%.
3. **Refactor de relatórios:** `preset_report.py` compartilhado pelos builders A/B/A, scaling e M01, sem alterar os relatórios anteriores.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** sessão única, três composições M01, fillers podem sobrepor props, outlier de primeira run documentado.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-M01-AB-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab/`
- `docs/benchmarks/m09/m01-ab.v1.json` e `M01-AB-REPORT.md`
- `tests/ci/test_m01_ab.py` (16 testes)

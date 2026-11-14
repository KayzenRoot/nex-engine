# Checkpoint Delta · NEX-M09-PRESET-SCALING-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `9babd8cb4f88c6cb5ac473c5ff77c82852293eb8` · **Measured source SHA:** `4e4719ac504ddb0ea7961d5c9d557c745f216990`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-PRESET-SCALING integrado:** harness parametrizado por 25/50/100/200 proxies; 18 capturas reais (3 por célula) validadas.
2. **Medição:** GPU p95 high vs low +504.7% (25), +499.3% (100), +478.3% (200); escala 25→200 +18.7% (low) e +13.6% (high); pacing ~4.267 ms.
3. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine/CI/`project.godot`.
4. **Sem generalização:** sessão única, cena sintética, 3 runs/célula, outlier de 1% low documentado.
5. **Próximos incrementos:** cenas M01 e mais repetições exigem WO própria.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-PRESET-SCALING-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling/`
- `docs/benchmarks/m09/scaling.v1.json` e `SCALING-REPORT.md`
- `tests/ci/test_preset_scaling.py` (8 testes)

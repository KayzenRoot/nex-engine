# Checkpoint Delta · NEX-M09-PRESET-AB-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `0cb02ec87fe950bc63f23b707120098993b71007` · **Measured source SHA:** `baf818ef934c418d111091af755e0a19ddd6ac9e`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-PRESET-AB integrado como harness de medição isolado:** cena A/B/A aplica presets `preset_pack.v1`, vsync off, 240 fps e captura com o profiler existente.
2. **Medição real na RTX 5050:** 6 runs COMPLETE/validadas; GPU p95 mediano 0.147 → 0.881 ms (+499.3%) no preset alto; pacing e 1% low estáveis no cap de 240 fps; A/A spread de GPU p95 3.4%.
3. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de `project.godot`, hub, renderer, shaders, engine ou CI.
4. **Sem generalização:** sessão única, cena sintética, 3 runs baixos/3 altos; nenhum claim de FPS de jogo ou ganho universal.
5. **Próximos incrementos:** repetição em cenas M01 e múltiplas amostras exigem WO própria.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-PRESET-AB-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/`
- `docs/benchmarks/m09/ab.v1.json` e `AB-REPORT.md`
- `tests/ci/test_preset_ab_harness.py` (10 testes)

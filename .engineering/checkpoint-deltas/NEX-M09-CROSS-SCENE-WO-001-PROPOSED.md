# Checkpoint Delta · NEX-M09-CROSS-SCENE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce` · **Measured source SHA:** `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-CROSS-SCENE integrado:** 48 capturas reais em `corridor_static` e `dense_city`, 50/100 proxies × 960×540/1920×1080, 3 runs por preset por célula.
2. **Medição:** delta GPU p95 high vs low +294.4%/+464.3–476.5% (corridor) e +245.6–249.3%/+457.3–461.5% (city); resolução 960→1920 +79.4–97.2% (low) e +180.0–191.5% (high); proxies 50→100 0.0–2.9% no GPU.
3. **Leitura:** o padrão pixel-bound de `arena_combat` se repete nas duas cenas; resolução domina o GPU e proxies afetam mais o CPU.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** sessão única, duas cenas, duas contagens e duas resoluções.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-CROSS-SCENE-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-cross-scene/`
- `docs/benchmarks/m09/cross-scene.v1.json` e `CROSS-SCENE-REPORT.md`
- `tests/ci/test_cross_scene.py` (9 testes)

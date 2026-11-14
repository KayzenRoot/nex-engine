# Checkpoint Delta · NEX-M09-INTERACTION-200-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `c1b73743c0c95d9fb8867079cb91fb74cfc03d49` · **Measured source SHA:** `c1b73743c0c95d9fb8867079cb91fb74cfc03d49`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-INTERACTION-200 integrado:** 12 capturas reais em 200 proxies × 960×540/1920×1080 na cena `arena_combat`, 3 runs por preset por resolução.
2. **Medição:** delta GPU p95 high vs low +228.6% (960×540) e +438.2% (1920×1080); resolução 960→1920 +60.2% (low) e +162.4% (high); 100→200 proxies +2.1–9.0% (contexto cross-session).
3. **Leitura:** o padrão pixel-bound se mantém no limite de 200 proxies.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** sessão única, uma cena, uma contagem e duas resoluções.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-INTERACTION-200-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction-200/`
- `docs/benchmarks/m09/interaction-200.v1.json` e `INTERACTION-200-REPORT.md`
- `tests/ci/test_interaction_200.py` (9 testes)

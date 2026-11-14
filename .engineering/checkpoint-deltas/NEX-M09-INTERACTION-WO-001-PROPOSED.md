# Checkpoint Delta · NEX-M09-INTERACTION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `3af467648b0b8b7831fb99003a9a16e583553fe7` · **Measured source SHA:** `2ef072c70189d5d013a62b7efc821f81078ef6d1`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-INTERACTION integrado:** 24 capturas reais em 50/100 proxies × 960×540/1920×1080 na cena `arena_combat`, viewport nativo, 3 runs por preset por célula.
2. **Medição:** delta GPU p95 high vs low +219.8%/+469.4% (50 proxies) e +227.1%/+473.6% (100 proxies); resolução 960→1920 +50.0% (low) e +163.1–167.1% (high); proxies 50→100 0.0–2.3% no GPU e +4.2–7.8% no CPU.
3. **Leitura:** no range de 50–100 meshes, o custo GPU é dominado por resolução; a contagem de proxies afeta principalmente CPU.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** sessão única, uma cena, duas contagens e duas resoluções; 25 proxies exigiria remover geometria.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-INTERACTION-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction/`
- `docs/benchmarks/m09/interaction.v1.json` e `INTERACTION-REPORT.md`
- `tests/ci/test_interaction.py` (10 testes)

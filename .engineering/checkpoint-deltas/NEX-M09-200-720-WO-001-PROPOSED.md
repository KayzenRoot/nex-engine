# Checkpoint Delta · NEX-M09-200-720-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `99eaad041b84c373da33ec1bb8a5922c31f4dad4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-200-720 integrado:** 6 capturas em `arena_combat`, 200 proxies, 1280×720, A/B/A.
2. **Medição:** GPU p95 0.111/0.468 ms; high/low +321.6%; contexto 100→200 +1.8%/+1.3% em GPU e +29.0%/+48.7% em CPU.
3. **Contexto M03:** `ab-high` previsto 0.460 vs medido 0.468 (−1.7%, dentro de 2%); `ab-low` +241.4%.
4. **Atlas:** 11 bundles, 150 capturas de performance, 66 imagens, 399 arquivos, 11 source SHAs.
5. **Enforcement:** `--check` do novo builder; 22 comandos / 19 arquivos.
6. **Sem mudança de harness, cena, preset, contrato, modelo, renderer, shader ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-200-720-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-arena-200-720/`
- `docs/benchmarks/m09/interaction-200-720.v1.json`
- `tests/ci/test_interaction_200_720.py` (6 testes)

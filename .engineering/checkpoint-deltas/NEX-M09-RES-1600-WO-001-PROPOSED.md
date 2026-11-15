# Checkpoint Delta · NEX-M09-RES-1600-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `b9fd2ed1cbde0625200b104fbd2c34796258dad3`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-RES-1600 integrado:** 6 capturas em `arena_combat`, 100 proxies, 1600×900, A/B/A.
2. **Medição:** GPU p95 0.133/0.632 ms; high/low +375.2%; 1280→1600 +25.5%/+37.4%; 1600→1920 +17.3%/+30.7%.
3. **Contexto M03:** `ab-high` −27.2%, entre o match de 1280×720 e o erro de 1920×1080; `ab-low` +185.0%.
4. **M06:** 162 observações / 10 bundles; atlas e advisories regenerados.
5. **Atlas M09:** 15 bundles, 162 capturas, 114 imagens, 483 arquivos, 15 source SHAs.
6. **Enforcement:** 27 comandos / 24 arquivos.
7. **Sem mudança de harness, cena, preset, contrato, modelo, renderer, shader ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M04/M05/M06/M09 seguem bounded admitted; M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-RES-1600-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1600/`
- `docs/benchmarks/m09/res-scaling-1600.v1.json`
- `tests/ci/test_res_scaling_1600.py` (6 testes)

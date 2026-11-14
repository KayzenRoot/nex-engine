# Checkpoint Delta · NEX-M09-RES-1440-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `39633b347784e66526c60be6c655d007d86f16cd`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-RES-1440 integrado:** 6 capturas em `arena_combat`, 100 proxies, 2560×1440, A/B/A.
2. **Medição:** GPU p95 0.206/1.547 ms; high/low +651.0%; 1920→2560 +32.1%/+87.3%; 960→2560 +114.6%/+388.0%.
3. **Contexto M03:** `ab-high` −70.3% (fora de 2%), `ab-low` +84.0% (fora); o acerto de 2% é específico de 1280×720.
4. **Atlas:** 12 bundles, 156 capturas de performance, 66 imagens, 414 arquivos, 12 source SHAs.
5. **Refactor:** núcleo `arena_resolution.py` compartilhado; saída de `build_interaction_200_720.py` byte-idêntica.
6. **Enforcement:** 23 comandos / 20 arquivos.
7. **Sem mudança de harness, cena, preset, contrato, modelo, renderer, shader ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-RES-1440-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling-1440/`
- `docs/benchmarks/m09/res-scaling-1440.v1.json`
- `tests/ci/test_res_scaling_1440.py` (6 testes)

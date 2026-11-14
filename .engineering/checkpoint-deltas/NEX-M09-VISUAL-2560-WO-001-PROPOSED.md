# Checkpoint Delta · NEX-M09-VISUAL-2560-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `4f739cd6808677cd7e3780a8bedb295da55e046d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-VISUAL-2560 integrado:** 18 PNGs em 2560×1440, 3 cenas × 2 presets × 3 repetições.
2. **A/A:** byte-idêntico por SHA em todas as repetições.
3. **A/B:** changed pixels 2.996%/3.074%/1.031%; mean abs 0.3694/0.3863/0.1524.
4. **Comparação com 1920:** Δ mean abs −11.4%/−8.4%/−14.6%.
5. **Atlas:** 13 bundles, 84 imagens, 435 arquivos, 13 source SHAs.
6. **Refactor:** núcleo `visual_truth.py` compartilhado; saída do relatório 1920 byte-idêntica.
7. **Enforcement:** 24 comandos / 21 arquivos.
8. **Sem nova medição de performance, mudança de harness/cena/preset/contrato ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-VISUAL-2560-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-2560/`
- `docs/benchmarks/m09/m01-visual-2560.v1.json`
- `tests/ci/test_m01_visual_2560.py` (5 testes)

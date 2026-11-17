# Checkpoint Delta · NEX-M09-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `371ca4ab4a5f70debc96e84bba55aba3870fc9cf`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09 full reference admitido:** `NEX-ADR-0020` / `NEX-D-031`, bounded às ferramentas de editor.
2. **PresetResolver:** 50 checks headless.
3. **PerfLint:** 42 checks; 13 findings (4 errors, 9 warns).
4. **ImportGuard:** 1 accepted / 3 rejected / 2 noop / 1 conflict; sem escrita.
5. **BenchmarkRecipe:** recipe `m09-corridor_static-ab-high-4101`, driver vulkan, 3 runs.
6. **Fixtures:** 4 arquivos determinísticos; 0 assets de terceiros.
7. **Gate:** `M09-FINAL-GATE.md`; issue #14 fechada após squash e checks.

## O que NÃO muda

- M10–M12 continuam bounded e exigem WO própria.
- M12 continua dependente de aprovação de marca.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhuma importação real, rendering, editor core, gameplay ou asset de terceiros é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `nex_modules/tools/editor_lab/`
- `docs/benchmarks/m09/editor-tools.v1.json`
- `docs/benchmarks/m09/M09-FINAL-GATE.md`
- `tests/ci/test_m09_final.py`

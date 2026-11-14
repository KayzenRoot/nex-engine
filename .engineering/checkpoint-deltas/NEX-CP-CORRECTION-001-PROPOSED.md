# Checkpoint Delta · NEX-CP-CORRECTION-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `599746391bad6d4acf6fc689f01f0d5cc7e309a5`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. `provenanceIndex.entries` 57 → **58**; `maxPr` 241 → **243** (o índice inclui o próprio bloco).
2. `ciBuilderCheckEnforcement.builderCommands` 24 → **25**; `builderFiles` 21 → **22**.
3. Seção do checkpoint atualizada para **58 entradas / PRs 112–243**.
4. Sem alteração do índice, admissão, medição, harness, contrato, modelo ou ruleset.

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.

## Evidência de apoio

- `.engineering/evidence/NEX-CP-CORRECTION-001-EVIDENCE.md`
- `docs/benchmarks/provenance-index.v1.json`

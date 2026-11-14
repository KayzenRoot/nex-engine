# Checkpoint Delta · NEX-M09-ATLAS-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `a33655a1ea55508a2d24d688936348a42c9ef10c`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-ATLAS integrado:** índice verificado dos oito bundles M09, 144 capturas de performance, 18 imagens, 330 arquivos e 8 source SHAs.
2. **Síntese:** resolução domina o custo GPU em 50–200 proxies; o delta do preset cresce com a resolução; proxies afetam mais o CPU; A/A visual é byte-idêntico.
3. **Perguntas abertas:** 2560×1440, outros hardwares, animação/temporal, integração no hub e admissão do parent.
4. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhuma mudança de engine, cenas base, `project.godot` ou CI.
5. **Sem generalização:** síntese de evidência single-session em uma RTX 5050.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-ATLAS-WO-001-EVIDENCE.md`
- `docs/benchmarks/m09/measurement-atlas.v1.json` e `MEASUREMENT-ATLAS.md`
- `tests/ci/test_measurement_atlas.py` (6 testes)

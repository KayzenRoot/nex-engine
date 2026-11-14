# Checkpoint Delta · NEX-M03-BUDGET-VALIDATION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `71375d6621bb179abe88fde398fb62a7fe16da80`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03-BUDGET-VALIDATION integrado:** snapshot do modelo e 6 comparações previsto vs medido nas cenas M01.
2. **Resultado:** 2/6 células dentro de 2% (corridor e arena no `ab-high`); low overestima 247.7–380.4%; city high +33.8%.
3. **Veredito:** `PARTIAL_DOMAIN_MATCH`; o modelo é limitado a luzes/sombras e não representa resolução/MSAA/glow/geometria.
4. **Parent M03 (#43) permanece NOT_ADMITTED.** Nenhuma mudança de modelo, contrato, engine, cenas ou CI.
5. **Sem generalização:** síntese de evidência M09 de uma sessão em uma RTX 5050.

## O que NÃO muda

- M01–M02/M04–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-BUDGET-VALIDATION-WO-001-EVIDENCE.md`
- `docs/benchmarks/m03/light-cost-model.v1.json` e `budget-validation.v1.json`
- `tests/ci/test_m03_budget_validation.py` (5 testes)

# Checkpoint Delta · NEX-ADMISSION-M06-M09-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `8ed41bafaf19cff52da9250784f78c3d608ac504`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06 (#11) e M09 (#14) admitidos** como `BOUNDED_ADMITTED_EVIDENCE_PIPELINE`, cobrindo contratos, protótipos, harnesses, evidência, relatórios, builders e testes.
2. **Excluídos:** runtime, hub, engine, renderer, shaders, cenas, aplicação de presets, generalização e claims de FPS.
3. **Demais parents:** M01–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
4. **Sem relaxamento:** CI, segurança, testes, locks, ruleset e auditoria solo permanecem.
5. **Sem nova medição ou mudança de código.**

## O que NÃO muda

- Nenhum módulo de runtime é admitido; nenhum checkpoint de produto completo é promovido.

## Evidência de apoio

- `.engineering/evidence/NEX-ADMISSION-M06-M09-WO-001-EVIDENCE.md`
- `NEX-ADR-0006-M06-M09-BOUNDED-ADMISSION.md` e `NEX-D-016`
- `tests/ci/test_m06_m09_admission.py` (6 testes)

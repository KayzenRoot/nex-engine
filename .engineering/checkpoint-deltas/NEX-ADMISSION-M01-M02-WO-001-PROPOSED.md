# Checkpoint Delta · NEX-ADMISSION-M01-M02-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `e729774583eb8ce3b75271aea66589bb9e04a587`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M01 (#6) e M02 (#7) admitidos** como `BOUNDED_ADMITTED_REFERENCE_PIPELINE`, cobrindo contratos, cenas base de referência, docs/QA, protótipos render3d e testes.
2. **Excluídos:** runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção, renderização real, render2d/M07, generalização e FPS.
3. **Demais parents:** M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M03/M06/M09 seguem bounded admitted.
4. **Sem relaxamento:** CI, segurança, testes, locks, ruleset e auditoria solo permanecem.
5. **Sem nova medição ou mudança de código.**

## O que NÃO muda

- Nenhum módulo de runtime é admitido; nenhum checkpoint de produto completo é promovido.

## Evidência de apoio

- `.engineering/evidence/NEX-ADMISSION-M01-M02-WO-001-EVIDENCE.md`
- `NEX-ADR-0008-M01-M02-BOUNDED-ADMISSION.md` e `NEX-D-018`
- `tests/ci/test_m01_m02_bounded_admission.py` (7 testes)

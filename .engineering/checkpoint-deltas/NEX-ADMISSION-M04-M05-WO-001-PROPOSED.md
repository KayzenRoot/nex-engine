# Checkpoint Delta · NEX-ADMISSION-M04-M05-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `5f801c09ca4148fb9712f84cfd638bd80f3a4372`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M04 (#9) admitido** como `BOUNDED_ADMITTED_MATERIALS_PIPELINE`, cobrindo contrato `material.v1`, ownership, docs, protótipo `texturebudget`, smoke headless, testes e evidência.
2. **M05 (#10) admitido** como `BOUNDED_ADMITTED_VFX_PIPELINE`, cobrindo contrato `spellfx.v1`, ownership, docs, protótipo `fxbudget`, smoke headless, testes e evidência.
3. **Excluídos:** criação de material/shader/textura/atlas/partícula/emissor/luz/decal, decodificação, atlas packing, integração de renderização, runtime, hub, engine, renderer, shaders, `project.godot`, gameplay, cenas de produção, performance/FPS/qualidade/game feel/licensing.
4. **Demais parents:** M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M01/M02/M03/M06/M09 seguem bounded admitted.
5. **Sem relaxamento:** CI, segurança, testes, locks, ruleset e auditoria solo permanecem.
6. **Sem nova medição ou mudança de código.**

## O que NÃO muda

- Nenhum módulo de runtime é admitido; nenhum checkpoint de produto completo é promovido.

## Evidência de apoio

- `.engineering/evidence/NEX-ADMISSION-M04-M05-WO-001-EVIDENCE.md`
- `NEX-ADR-0009-M04-M05-BOUNDED-ADMISSION.md` e `NEX-D-019`
- `tests/ci/test_m04_m05_bounded_admission.py` (7 testes)

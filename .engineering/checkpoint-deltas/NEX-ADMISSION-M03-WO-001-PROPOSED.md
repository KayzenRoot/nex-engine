# Checkpoint Delta · NEX-ADMISSION-M03-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `51110ff02eb2c542832b6290a98fdc5f979b58a9`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03 (#8) admitido** como `BOUNDED_ADMITTED_ANALYSIS_PIPELINE`, cobrindo contrato, light rig, shadow stability, light budget e validação.
2. **Excluídos:** runtime, renderer, shaders, cenas, hub, `project.godot`, implementação real de luz/sombra/GI, generalização e FPS.
3. **Demais parents:** M01–M02, M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`; M06/M09 seguem bounded admitted.
4. **Sem relaxamento:** CI, segurança, testes, locks, ruleset e auditoria solo permanecem.
5. **Sem nova medição ou mudança de código.**

## O que NÃO muda

- Nenhum módulo de runtime é admitido; nenhum checkpoint de produto completo é promovido.

## Evidência de apoio

- `.engineering/evidence/NEX-ADMISSION-M03-WO-001-EVIDENCE.md`
- `NEX-ADR-0007-M03-BOUNDED-ADMISSION.md` e `NEX-D-017`
- `tests/ci/test_m03_bounded_admission.py` (7 testes)

# NEX-M04-M05-CONTRACTS-WO-001 | Contratos de materiais PBR e SpellFX

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; pacote de interfaces independentes para M04 (#9) e M05 (#10).
**Base:** `main` `11d8e61579680166bb36a645502d97e60b23a832`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M04-M05-CONTRACTS-WO-001-EXECUTION.json` (23 fingerprints).

## Objetivo

Definir contratos versionados para observações de materiais PBR (`material.v1`) e de efeitos de magia (`spellfx.v1`), com ownership prospectivo, documentação e testes estruturais. Nenhuma implementação de material, shader, partícula, luz ou cena.

## Escopo

- `contracts/m04/material.v1.schema.json`, `contracts/m04/ownership.v1.json`.
- `contracts/m05/spellfx.v1.schema.json`, `contracts/m05/ownership.v1.json`.
- `docs/contracts/m04.md`, `docs/contracts/m05.md`.
- `tests/contracts/_contract_support.py`, `tests/contracts/test_m04_material_contract.py`, `tests/contracts/test_m05_spellfx_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Implementar materiais, shaders, texturas, partículas, luzes, cenas ou engine.
- M04/M05 parent admission; M06/M08/M12.
- Claims visuais, de FPS, frame-time ou VRAM.

## DoD

- Dois contratos válidos, versionados e independentes, com ownership prospectivo.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência de contrato, check vermelho ou necessidade de implementação → parar e registrar.

# NEX-M08-CONTRACT-WO-001 | Contrato de composição 2.5D v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; formaliza o rascunho DepthWeave sem implementar 2.5D.
**Base:** `main` `4f692369f7a94378c3bee431fa67fe37fca8c324`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M08-CONTRACT-WO-001-EXECUTION.json` (26 fingerprints).

## Objetivo

Definir `composition.v1` para observações de composição 2.5D: referência ao plano 3D, stack de camadas, política de profundidade, alpha guard, HUD/overlay safety, entidades críticas, performance com disponibilidade e proveniência. Nenhum rendering, shader, viewport ou implementação 2.5D.

## Escopo

- `contracts/m08/composition.v1.schema.json`, `contracts/m08/ownership.v1.json`.
- `docs/contracts/m08.md`.
- `tests/contracts/test_m08_composition_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Implementar 2.5D, camadas, viewport, shader, cena ou engine.
- M08 parent admission; M09–M12.
- Claims visuais, de FPS, frame-time ou VRAM.

## DoD

- Contrato válido com invariantes de camada/HUD/alpha/plano 3D.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência com o rascunho DepthWeave, check vermelho ou necessidade de implementação → parar e registrar.

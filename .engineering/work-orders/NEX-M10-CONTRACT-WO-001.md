# NEX-M10-CONTRACT-WO-001 | Contrato de feedback de combate v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente para o módulo de animação/feedback de combate.
**Base:** `main` `f0f5bec11ca859a74eb3c6964e923728b4c552ed`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M10-CONTRACT-WO-001-EXECUTION.json` (27 fingerprints).

## Objetivo

Definir `feedback.v1` para observações de feedback de combate: fases do ataque, hit events, canais (hit-stop, shake, flash, recoil, damage number), prioridade/intensidade, orçamento de hit-stop/shake/concorrência, performance com disponibilidade e proveniência. Nenhuma animação, shader, câmera ou rendering.

## Escopo

- `contracts/m10/feedback.v1.schema.json`, `contracts/m10/ownership.v1.json`.
- `docs/contracts/m10.md`.
- `tests/contracts/test_m10_feedback_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Implementar animação, hit-stop, shake, flash, recoil, damage numbers ou câmera.
- M10 parent admission; M11/M12.
- Claims visuais, de game feel, FPS ou frame-time.

## DoD

- Contrato válido com invariantes de fase/evento/canal/concorrência/orçamento.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência de contrato, check vermelho ou necessidade de implementação → parar e registrar.

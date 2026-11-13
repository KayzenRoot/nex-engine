# NEX-M10-FEEDBACK-WO-001 | Planejador de feedback de combate

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `feedback.v1`.
**Base:** `main` `9b88b7abc1cc6b5ce13551a915a4cb6311ec65eb`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M10-FEEDBACK-WO-001-EXECUTION.json` (28 fingerprints).

## Objetivo

Implementar um planejador determinístico de feedback de combate: fases do ataque, hit events, canais priorizados, timeline, concorrência, budgets de hit-stop/shake e conflitos. Exporta uma observação `feedback.v1`. Sem animação, câmera ou rendering.

## Escopo

- `nex_modules/animation/combat_feedback/`: projeto Godot autocontido (`feedback_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_feedback_planner.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Implementar animação, hit-stop, shake, flash, recoil, damage numbers ou câmera.
- M10 parent admission; M11/M12.
- Claims de game feel, FPS, frame-time ou VRAM.

## DoD

- Timeline, budgets, concorrência e exportação determinísticos, alinhados a `feedback.v1`.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre planejador e contrato, check vermelho ou necessidade de animação/rendering → parar e registrar.

# NEX-M08-COMPOSITION-WO-001 | Planejador de composição 2.5D

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `composition.v1`.
**Base:** `main` `5159d774436015870ab4fec1fe1416d5a8190cd1`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M08-COMPOSITION-WO-001-EXECUTION.json` (27 fingerprints).

## Objetivo

Implementar um planejador determinístico de composição 2.5D: registrar camadas e entidades críticas, aplicar políticas de profundidade/alpha/HUD, ordenar o draw stack por papel, reportar conflitos (alpha sobre entidade crítica, HUD cobrindo gameplay, override indevido, riscos do plano 3D) e exportar uma observação `composition.v1`. Sem rendering.

## Escopo

- `nex_modules/render2_5d/composition/`: projeto Godot autocontido (`composition_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_composition_planner.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Criar camadas, viewport, shader, cena, engine ou rendering 2.5D.
- M08 parent admission; M09–M12.
- Claims visuais, FPS, frame-time ou VRAM.

## DoD

- Ordenação, conflitos e exportação determinísticos, alinhados a `composition.v1`.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre planejador e contrato, check vermelho ou necessidade de rendering → parar e registrar.

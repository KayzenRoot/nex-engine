# NEX-M05-FXBUDGET-WO-001 | Planejador de orçamento FX

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `spellfx.v1`.
**Base:** `main` `6f93034e7557a6cb0a77aa89d6109ffea9d0c3da`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M05-FXBUDGET-WO-001-EXECUTION.json` (26 fingerprints).

## Objetivo

Implementar um planejador determinístico de orçamento FX: validar magias/emissores no vocabulário `spellfx.v1`, agregar totais de emissores, partículas, emissores GPU, decals e light bridges, detectar violações de contrato e gerar planos de redução de partículas e conversão GPU→CPU quando o orçamento é excedido. Sem criar partículas, luzes, decals ou renderizar.

## Escopo

- `nex_modules/vfx/fxbudget/`: projeto Godot autocontido (`fx_budget_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_fx_budget_planner.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Criar/instanciar partículas, emissores, luzes, decals, shaders ou cenas; alterar `nex_bench`/engine/CI.
- M05 parent admission; M06/M08/M12.
- Claims de qualidade visual, FPS, frame-time ou VRAM.

## DoD

- Agregação, achados e planos de redução determinísticos, alinhados a `spellfx.v1`.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre planejador e `spellfx.v1`, check vermelho ou necessidade de rendering → parar e registrar.

# NEX-M03-SHADOWSTAB-WO-001 | Analisador determinístico de estabilidade de sombras

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome o contrato `lighting.v1` e o plano do light-rig.
**Base:** `main` `346c6dd6bd85c12e3aad1250d8cae95b195bd605`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M03-SHADOWSTAB-WO-001-EXECUTION.json` (22 fingerprints).

## Objetivo

Implementar um analisador determinístico de riscos de estabilidade de sombra a partir de um plano `lighting.plan.v1` ou observação `lighting.v1`: orçamento, bias, softness, pressão de atlas, cascatas e coerência de casters. Sem rendering e sem claim visual.

## Escopo

- `nex_modules/lighting/shadows/`: projeto Godot autocontido (`shadow_stability_analyzer.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_shadow_stability_analyzer.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Criar sombras, shadow maps, filtros, shaders, cenas ou renderer; alterar `nex_bench`/engine/CI.
- M03 parent admission; M04–M12.
- Qualidade visual, acne/peter-panning medidos, FPS, frame-time ou VRAM.

## DoD

- Análise determinística com achados, severidades e veredito explícito.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre analisador e contrato, check vermelho ou necessidade de rendering → parar e registrar.

# NEX-M04-TEXTUREBUDGET-WO-001 | Planejador de orçamento de texturas

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `material.v1`.
**Base:** `main` `65afc09666f8e8f5046e471c8a8e37cf71368279`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M04-TEXTUREBUDGET-WO-001-EXECUTION.json` (25 fingerprints).

## Objetivo

Implementar um planejador determinístico de orçamento de texturas: validar materiais/texturas no vocabulário `material.v1`, deduplicar por SHA-256, estimar bytes decodificados com mips, calcular pressão de atlas e gerar um plano de downscale quando o orçamento é excedido. Sem carregar texturas, criar materiais ou renderizar.

## Escopo

- `nex_modules/materials/texturebudget/`: projeto Godot autocontido (`texture_budget_planner.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_texture_budget_planner.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Carregar/decodificar texturas, compilar shaders, criar materiais, atlas packing real ou rendering.
- Alterar `nex_bench`/engine/CI; M04 parent admission; M05–M12.
- Claims de VRAM real, qualidade visual ou performance.

## DoD

- Deduplicação, bytes/mips, pressão de atlas, achados e plano de downscale determinísticos.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre planejador e `material.v1`, check vermelho ou necessidade de decoding/render → parar e registrar.

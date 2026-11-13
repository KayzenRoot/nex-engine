# NEX-M03-LIGHTBUDGET-WO-001 | Árbitro determinístico de orçamento de iluminação

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente calibrado pelas capturas reais S05 do Lighting Matrix.
**Base:** `main` `7205f6cb2af590877c84a7654a58cad01ec9e5cd`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M03-LIGHTBUDGET-WO-001-EXECUTION.json` (24 fingerprints).

## Objetivo

Implementar um árbitro determinístico que projeta o custo GPU de uma configuração de luzes/sombras/partículas a partir dos coeficientes medidos na sessão S05 e recomenda uma escada de degradação quando o orçamento é excedido. Sem rendering novo e sem generalizar os coeficientes para outras cenas.

## Escopo

- `nex_modules/lighting/budget/`: projeto Godot autocontido (`light_budget_arbiter.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_light_budget_arbiter.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Executar novas capturas GPU, alterar `nex_bench`/engine/CI ou substituir o profiler.
- Claims de FPS, frame-time de cena real ou generalização dos coeficientes.
- M03 parent admission; M04–M12.

## DoD

- Modelo de custo explícito, rastreável à análise S05, com coeficientes sobrescrevíveis.
- Projeção determinística, veredito e escada de degradação ordenada.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre modelo e análise S05, check vermelho ou necessidade de nova captura → parar e registrar.

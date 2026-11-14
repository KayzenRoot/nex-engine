# NEX-M12-VALIDATOR-WO-001 | Validador de identidade visual

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `identity.v1`.
**Base:** `main` `25113e7dfcb12091aeb79b77cb82c9e7aed95549`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M12-VALIDATOR-WO-001-EXECUTION.json` (29 fingerprints).

## Objetivo

Implementar um validador determinístico de identidade visual: paleta/papéis, contraste WCAG calculado dos hex, tipografia, viewBox/digests do logo, escala de spacing, limites de acessibilidade e proveniência. Nenhum logo/tema é gerado ou aprovado.

## Escopo

- `nex_modules/brand/tokens/`: projeto Godot autocontido (`identity_validator.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_identity_validator.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Gerar logos/SVG/temas, editar assets, aprovar marca, alterar engine/CI.
- M12 parent admission.
- Claims de contraste medido em tela, brand approval ou performance.

## DoD

- Validação determinística com achados, métricas de contraste e veredito.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre validador e `identity.v1`, check vermelho ou necessidade de geração de assets → parar e registrar.

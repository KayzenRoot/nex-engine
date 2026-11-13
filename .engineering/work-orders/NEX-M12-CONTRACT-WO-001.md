# NEX-M12-CONTRACT-WO-001 | Contrato de identidade visual v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente para identidade visual, SVG e rebranding.
**Base:** `main` `eca91947ad3785b33bbe7cf1bb1c7c09e6b78500`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M12-CONTRACT-WO-001-EXECUTION.json` (28 fingerprints).

## Objetivo

Definir `identity.v1` para observações de identidade visual: paleta com papéis, tipografia, variantes de logo SVG com digests/viewBox, escala de spacing, requisitos de acessibilidade/contraste e proveniência. Nenhum asset final, logo ou tema é gerado.

## Escopo

- `contracts/m12/identity.v1.schema.json`, `contracts/m12/ownership.v1.json`.
- `docs/contracts/m12.md`.
- `tests/contracts/test_m12_identity_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Gerar logos/SVG/temas, editar assets, alterar engine/CI.
- M12 parent admission.
- Claims de aprovação de marca, contraste medido em tela ou performance.

## DoD

- Contrato válido com invariantes de paleta/contraste/tipografia/logo/spacing.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência de contrato, check vermelho ou necessidade de geração de assets → parar e registrar.

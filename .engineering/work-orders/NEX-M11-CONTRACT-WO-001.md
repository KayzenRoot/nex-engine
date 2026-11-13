# NEX-M11-CONTRACT-WO-001 | Contrato de asset pipeline v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente para asset pipeline, qualidade e licenciamento.
**Base:** `main` `ad18bdd64f7b9745bc606d36f36d2431ac708d10`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M11-CONTRACT-WO-001-EXECUTION.json` (27 fingerprints).

## Objetivo

Definir `asset_pipeline.v1` para observações de pipeline de assets: identidade/digest, estágios raw→imported→cooked→validated, licença SPDX/atribuição/verificação, import settings, dependências, política de licenciamento, orçamentos de assets/bytes/texturas e proveniência. Nenhum import, cook ou carregamento de asset.

## Escopo

- `contracts/m11/asset_pipeline.v1.schema.json`, `contracts/m11/ownership.v1.json`.
- `docs/contracts/m11.md`.
- `tests/contracts/test_m11_asset_pipeline_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Implementar import/cook/validação, carregar assets, alterar engine/CI.
- M11 parent admission; M12.
- Claims de qualidade, licenciamento verificado ou performance.

## DoD

- Contrato válido com invariantes de estágio, licença, dependência e orçamento.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência de contrato, check vermelho ou necessidade de implementação → parar e registrar.

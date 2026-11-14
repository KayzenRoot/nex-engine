# NEX-M11-AUDIT-WO-001 | Auditor de asset pipeline

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; incremento independente que consome `asset_pipeline.v1`.
**Base:** `main` `bc849b42fd8772bcbe35df9cec9d40cd80dffe93`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M11-AUDIT-WO-001-EXECUTION.json` (29 fingerprints).

## Objetivo

Implementar um auditor determinístico de pipeline de assets: validar estágios raw→imported→cooked→validated, licenças SPDX/atribuição/verificação, dependências/ciclos, orçamentos e achados de qualidade; emitir veredito e recomendações. Nenhum asset é importado, cookado ou carregado.

## Escopo

- `nex_modules/assets/license_audit/`: projeto Godot autocontido (`asset_pipeline_auditor.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md`, log headless).
- `tests/ci/test_asset_pipeline_auditor.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Import/cook/validação real de assets, alterar engine/CI.
- M11 parent admission; M12.
- Claims de licenciamento verificado, qualidade ou performance.

## DoD

- Auditoria determinística com achados, veredito e recomendações, alinhada a `asset_pipeline.v1`.
- Smoke headless verde, testes estruturais verdes, suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência entre auditor e contrato, check vermelho ou necessidade de import/cook → parar e registrar.

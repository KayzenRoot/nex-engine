# NEX-M11-KIT-AUDIT-WO-001 | Auditoria M11 do kit M04

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** M11 `BOUNDED_ADMITTED_ASSET_PIPELINE` (`NEX-ADR-0010` / `NEX-D-020`); instrução contínua do Owner de 2026-11-15.
**Base:** `main` `7e425920cdaf17c158d46979e68df47e66742724`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (auditoria determinística, sem import/cook/rendering).
**Lock:** `.engineering/context-locks/NEX-M11-KIT-AUDIT-WO-001-EXECUTION.json`.

## Objetivo

Alimentar o `AssetPipelineAuditor` integrado com as 12 texturas do kit M04 e produzir uma auditoria determinística de hashes, estágios, orçamento e status de licença. O resultado deve ser honesto: licenças **não verificadas** e texturas sem compressão, sem qualquer claim jurídico ou de qualidade.

## Escopo

- `nex_modules/assets/license_audit/kit_audit.gd`: SceneTree headless que lê o kit e chama o auditor.
- `nex_modules/assets/license_audit/evidence/kit-audit-2026-11-15.json`.
- `docs/benchmarks/m11/tools/build_kit_audit.py`, `docs/benchmarks/m11/kit-audit.v1.json` e `KIT-AUDIT.md`.
- `tests/ci/test_kit_audit.py`; enforcement no workflow e contagem 29 arquivos / 32 checks.
- WO/lock/evidência/delta e checkpoint.

## Fora de escopo

- Importar, cozinhar, comprimir, carregar como textura ou renderizar qualquer asset.
- Verificar juridicamente licenças ou emitir claim de licenciamento.
- Alterar o kit, o auditor, o contrato `asset_pipeline.v1`, cenas, presets, renderer ou shaders.
- Claims de FPS, frame-time, VRAM, qualidade ou ganho.
- Novos parents ou mudança de status.

## DoD

- Auditoria de **12 assets**, 788.844 bytes, 0 estágios falhos/pendentes, 0 findings high.
- 12 findings medium `license_unverified` e 12 low `texture_uncompressed`; veredito `REVIEW_REQUIRED`.
- `kit_sha256` e `source_sha` conferidos; builder `--check` reproduz JSON/Markdown; CI 29/32.
- Suíte CI completa verde; PR protegida e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, kit/auditor alterado, veredito `READY_FOR_INTEGRATION` sem licenças verificadas, builder divergente ou check vermelho → parar e registrar.

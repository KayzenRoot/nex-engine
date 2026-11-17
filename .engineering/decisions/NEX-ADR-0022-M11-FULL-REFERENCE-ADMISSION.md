# NEX-ADR-0022 · Admissão full reference do M11 e pipeline de assets

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-17
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `13554f3e9ee879c48edb32d780c6fa0611d41b19`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base. O M11 já tinha contrato `asset_pipeline.v1`, o `AssetPipelineAuditor` com 43 checks e o kit audit de 12 assets, mas não tinha manifesto de assets, planejador de cook, ledger de licenças nem quality gate determinísticos.

## Decisão

Admitir, de forma **full reference e bounded ao M11**:

- **AssetPipelineAuditor:** manter a auditoria de estágios, licenças, dependências, budgets e qualidade com 43 checks.
- **AssetManifest:** validação determinística de id, kind, path, SHA-256, bytes, dimensões, licença, source, mipmaps, PBR maps e escala; 39 checks no smoke.
- **CookPlanner:** plano de cook por plataforma/formato com accepted/rejected/noop/conflicts; nunca escreve.
- **LicenseLedger:** allowlist SPDX, verificação declarada, atribuição, terceiros e veredito CLEARED/REVIEW_REQUIRED/BLOCKED.
- **AssetQualityGate:** heurísticas estruturais de textura, modelo e animação.
- **Fixtures determinísticas:** 3 arquivos e smoke headless.
- **Evidência:** `m11-asset-smoke-2026-11-17.json`, relatório `asset-tools.v1.json` e gate.
- **R&D/QA:** decisões GO/GO_WITH_LIMITATIONS e fechamento de #16 após squash protegido.

## Escopo de arquivos admitido

- `nex_modules/assets/asset_lab/**` (manifest, cook, license, quality, fixtures e smoke).
- `docs/benchmarks/m11/asset-tools.v1.json`, `ASSET-TOOLS.md` e `tools/build_m11_asset_tools.py`.
- `tests/ci/test_m11_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhuma importação, cook, escrita, overwrite ou pipeline real de assets.
- Nenhuma verificação jurídica de licença, clearance ou atribuição publicada.
- Nenhum rendering, shader, cena de produção, editor core ou `project.godot` principal.
- Nenhum asset de terceiros real; fixtures são metadados sintéticos.
- Nenhum M12, gameplay, rede, cloud, FPS, VRAM, qualidade ou paridade com PoE2.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_m11_asset_tools.py --check` reproduz o relatório; smoke `39 checks` PASS.
3. AssetPipelineAuditor smoke `43 checks` PASS; kit audit 12 assets, 0 failed stages.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M12 continua bounded e exige WO própria e aprovação de marca.
6. O fechamento de issue só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M11 passa a ser o décimo primeiro módulo base concluído como **pipeline de assets de referência**, não como jogo.
- M12 pode consumir o ledger e o quality gate; a verificação legal permanece fora do escopo.
- CookPlanner e AssetManifest permanecem ferramentas determinísticas, não benchmarks de hardware.

# NEX-ADR-0023 · Admissão full reference do M12 e sistema de marca

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-17
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `c2c13c57b4de7a5114db2e2b79d37a7e026bfa62`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base. O M12 já tinha contrato `identity.v1`, o `IdentityValidator` com 36 checks e um brand master provisório com wordmark dependente de fonte, sem ícones raster, containers de app ou documento canônico de identidade. A pendência de decisão de marca do Owner impedia o fechamento de #17.

## Decisão

Admitir, de forma **full reference e bounded ao M12**:

- **Wordmark final:** NEX ENGINE construído em paths geométricos outline, sem `<text>` e sem dependência de fonte, em `wordmark.svg` e `logo-primary.svg`.
- **Paleta canônica:** Graphite, Cobalt, Cyan, Amber e Mist, com papéis declarados e contraste verificado.
- **App icons:** 9 PNGs (16–1024), container ICO e container ICNS gerados deterministicamente do mark original.
- **`identity.v1`:** documento canônico com tokens, tipografia, hashes dos SVGs, espaçamento e thresholds de acessibilidade.
- **Validador final:** smoke headless com 14 checks, veredito `READY_FOR_UI` e zero findings.
- **Builder:** `build_brand_kit.py` reproduz relatório, identidade, ICO/ICNS e `SHA256SUMS.txt`; `--check` é obrigatório no Fast Lane.
- **Evidência e gate:** `brand-kit.v1.json`, `BRAND-KIT.md`, `M12-FINAL-GATE.md` e fechamento de #17 após squash protegido.

## Escopo de arquivos admitido

- `assets/brand/**` (SVGs, paleta, identidade, ícones, app icons, guidelines e sums).
- `nex_modules/brand/tokens/final_smoke.gd`, `render_brand_assets.gd` e `evidence/m12-final-identity-2026-11-17.json`.
- `docs/benchmarks/m12/**` (builder, relatório, markdown e gate).
- `docs/brand/BRAND-MASTER.md`.
- `tests/ci/test_brand_assets.py`, `tests/ci/test_m12_final.py`.
- Enforcement de builders e workflow CI.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #17.

## Exclusões explícitas

- Nenhuma integração com editor UI, launcher, installer, hub, renderer ou binário da engine.
- Nenhuma alteração em `nex_bench/project.godot`, cenas de produção ou ícones do editor.
- Nenhuma aprovação jurídica, licença de distribuição ou clearance de trademark.
- Nenhum asset, fonte, shader ou marca de terceiros; a marca é original e não deriva do logo Godot.
- Nenhum claim de FPS, qualidade visual, paridade com PoE2 ou aprovação independente.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_brand_kit.py --check` reproduz relatório, identidade, ICO/ICNS e sums.
3. Smoke final `14 checks` PASS; `identity.v1` `READY_FOR_UI` sem findings.
4. 9 app icons válidos, ICO com 9 entradas, ICNS íntegro, 10 ícones de UI.
5. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
6. Distribuição e trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING` até decisão específica do Owner.
7. O fechamento de #17 só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- O M12 passa a ser o décimo segundo módulo base concluído como **sistema de marca de referência**, não como rebranding da engine.
- A identidade fica pronta para uma futura UI, mas nenhuma UI é admitida por este ADR.
- O wordmark deixa de depender de fonte e pode ser distribuído com hashes verificáveis após a decisão de licença/trademark.

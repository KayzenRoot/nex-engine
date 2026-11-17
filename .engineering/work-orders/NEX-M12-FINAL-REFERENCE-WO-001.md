# NEX-M12-FINAL-REFERENCE-WO-001 | Fechamento do sistema de marca M12

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0023` / `NEX-D-034`; instrução do Owner de 2026-11-17 para finalizar o M12 com identidade verificável, sem rebranding da engine.
**Base:** `main` `c2c13c57b4de7a5114db2e2b79d37a7e026bfa62`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (assets originais e validação headless).
**Lock:** `.engineering/context-locks/NEX-M12-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M12 como sistema de marca de referência: wordmark outline sem dependência de fonte, paleta canônica, 10 ícones de UI, 9 app icons com ICO/ICNS, `identity.v1` com hashes e thresholds, validador final de 14 checks, relatório/gate e fechamento de #17.

## Escopo

- `assets/brand/logo-primary.svg`, `wordmark.svg`, `palette.v1.json`, `identity.v1.json`, `BRAND-GUIDELINES.md`, `SHA256SUMS.txt` e `app-icons/`.
- `nex_modules/brand/tokens/final_smoke.gd`, `render_brand_assets.gd` e evidence `m12-final-identity-2026-11-17.json`.
- `docs/benchmarks/m12/tools/build_brand_kit.py`, `BRAND-KIT.md`, `brand-kit.v1.json` e `M12-FINAL-GATE.md`.
- `docs/brand/BRAND-MASTER.md`.
- `tests/ci/test_brand_assets.py`, `tests/ci/test_m12_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #17.

## Fora de escopo

- Editor UI, launcher, installer, hub, renderer ou binário da engine.
- `nex_bench/project.godot`, cenas de produção ou ícones do editor.
- Licença de distribuição, clearance de trademark ou revisão jurídica.
- Assets, fontes, shaders ou marcas de terceiros.
- FPS, qualidade visual, paridade com PoE2 ou revisão independente.

## DoD

- Wordmark e logo primário sem `<text>` e sem `font-family`.
- 9 app icons PNG com dimensões corretas; ICO com 9 entradas; ICNS íntegro.
- `identity.v1` com 5 tokens, hashes dos 3 SVGs e thresholds 7.0/3.0.
- Smoke final **14 checks** PASS; `READY_FOR_UI`; zero findings.
- Relatório `BRAND_SYSTEM_READY_FOR_UI`; Mist/Graphite 16.48:1; Cobalt/Graphite 4.27:1.
- Builder `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issue #17 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, ícone/container inválido, builder divergente, check vermelho, integração de engine, claim de trademark/licença ou paridade com PoE2 → parar e registrar.

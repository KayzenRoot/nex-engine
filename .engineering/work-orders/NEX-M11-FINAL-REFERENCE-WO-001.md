# NEX-M11-FINAL-REFERENCE-WO-001 | Fechamento do pipeline de assets M11

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0022` / `NEX-D-033`; instrução do Owner de 2026-11-17 para finalizar o M11 com ferramentas determinísticas, sem paridade com PoE2.
**Base:** `main` `13554f3e9ee879c48edb32d780c6fa0611d41b19`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (ferramentas headless e fixtures).
**Lock:** `.engineering/context-locks/NEX-M11-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M11 como pipeline de assets de referência: AssetPipelineAuditor, AssetManifest, CookPlanner, LicenseLedger e AssetQualityGate, com fixtures determinísticas, smoke headless, relatório/gate e fechamento de #16.

## Escopo

- `nex_modules/assets/asset_lab/asset_manifest.gd`, `cook_planner.gd`, `license_ledger.gd`, `quality_gate.gd`, `smoke.gd`, `project.godot`, `main.tscn` e `fixtures/`.
- Evidence `nex_modules/assets/asset_lab/evidence/m11-asset-smoke-2026-11-17.json`.
- `docs/benchmarks/m11/tools/build_m11_asset_tools.py`, `ASSET-TOOLS.md` e `asset-tools.v1.json`.
- `docs/benchmarks/m11/M11-FINAL-GATE.md`.
- `tests/ci/test_m11_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #16.

## Fora de escopo

- Importação, cook, escrita, overwrite ou pipeline real de assets.
- Verificação jurídica de licença, clearance ou atribuição publicada.
- Rendering, shader, cena de produção, editor core, `project.godot` principal.
- M12, gameplay, rede, cloud, assets de terceiros reais.
- FPS, VRAM, qualidade, paridade com PoE2.

## DoD

- AssetPipelineAuditor **43 checks**; asset smoke **39 checks**; total **82 checks**.
- AssetManifest: 8 assets, 2 errors, 2 warns, 270592 bytes.
- CookPlanner: **5 accepted / 1 rejected / 1 noop / 1 conflict**, sem escrita.
- LicenseLedger: 2 third-party, 1 unverified, 2 rejected, 2 attribution; **BLOCKED**.
- AssetQualityGate: 0 errors, 5 warns, 2 info; **REVIEW_REQUIRED**.
- 3 fixtures determinísticas; 0 assets de terceiros reais.
- Builder `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issue #16 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, fixture ausente, check vermelho, escrita de asset, claim de clearance legal ou paridade com PoE2 → parar e registrar.

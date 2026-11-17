# NEX M11 · Asset tools

**Status:** `M11_ASSET_TOOLS_REFERENCE_DERIVED / HEADLESS_FIXTURES / NO_IMPORT_OR_COOK / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `13554f3e9ee879c48edb32d780c6fa0611d41b19` · **Engine:** Godot 4.7.2-stable

## S01 · AssetPipelineAuditor

- **ASSET_AUDITOR_VERIFIED**: 43 checks; kit 12 assets, 0 failed stages, verdict `REVIEW_REQUIRED`.

## S02 · AssetManifest

- **ASSET_MANIFEST_DERIVED**: 8 assets; 2 errors, 2 warns; 270592 bytes declarados.

## S03 · CookPlanner

- accepted **5**, rejected **1**, noop **1**, conflicts **1**.
- Plano determinístico; nenhum arquivo é escrito ou sobrescrito.

## S04 · LicenseLedger

- 3rd-party **2**, unverified **1**, rejected **2**, attribution **2**; veredito `BLOCKED`.

## S05 · AssetQualityGate

- errors **0**, warns **5**, info **2**; veredito `REVIEW_REQUIRED`.

## S06 · QA

- 82 checks totais; 3 fixtures; 0 assets de terceiros reais.

## Decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| AssetPipelineAuditor | **GO** | 43 checks; 12 kit assets, 0 failed stages |
| AssetManifest | **GO_WITH_LIMITATIONS** | 8 assets; 2 errors and 2 warnings from declared metadata |
| CookPlanner | **GO_WITH_LIMITATIONS** | 5 accepted / 1 rejected / 1 noop / 1 conflict; plan only |
| LicenseLedger | **GO_WITH_LIMITATIONS** | 2 third-party, 1 unverified, 2 rejected, 2 attribution; BLOCKED |
| AssetQualityGate | **GO_WITH_LIMITATIONS** | 0 errors, 5 warnings, 2 info; REVIEW_REQUIRED |

## Observações

- AssetPipelineAuditor still passes 43 headless checks
- the M04 kit audit covers 12 assets with 0 failed and 0 pending stages
- AssetManifest reports 2 errors and 2 warnings across 8 deterministic assets
- CookPlanner plans 5 accepted, 1 rejected, 1 noop and 1 conflict without writing
- LicenseLedger returns BLOCKED with 2 rejected and 1 unverified license
- AssetQualityGate returns REVIEW_REQUIRED with 5 warnings and 2 info findings

## Limitações

- fixtures only; no asset is imported, cooked, loaded or rendered
- license verification is declared data, not legal review
- cook sizes are declared bytes, not filesystem or GPU measurements
- quality findings are structural heuristics, not visual review
- no FPS, VRAM, quality or PoE2 parity claim

Gerado por `docs/benchmarks/m11/tools/build_m11_asset_tools.py`; não é verificação jurídica.

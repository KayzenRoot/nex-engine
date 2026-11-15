# NEX M11 · Kit asset-pipeline audit

**Status:** `AUDIT_DERIVED / NON_RENDERING / LICENSES_UNVERIFIED / ADMIN_SOLO_NOT_INDEPENDENT`

**Kit:** `nex_modules/materials/kit/kit.v1.json` · **SHA-256:** `0e597c6579205f93ebb2afc7c659a58593a759df0bdc4f0bd5574306713a6b08`
**Evidência:** `nex_modules/assets/license_audit/evidence/kit-audit-2026-11-15.json` · **SHA-256:** `ef20fe3a0ed10c5f8723067a4dea109bea9b12c31b108f4d5b4639b05d0783c9`

| Métrica | Valor |
|---|---:|
| Assets | 12 |
| Bytes totais | 788844 |
| Bytes de textura | 788844 |
| Estágios falhos | 0 |
| Estágios pendentes | 0 |
| Licenças não verificadas | 12 |
| Findings high/medium/low | 0/12/12 |
| Veredito | REVIEW_REQUIRED |

## Observações

- 12 kit textures were audited with matching SHA-256 values
- no stage failed and no stage is pending; raw and imported are the only stages
- 0 high-severity findings; 12 medium license_unverified and 12 low texture_uncompressed
- the auditor recommends verifying licenses and enabling texture compression

## Limitações

- analysis only: no asset is imported, cooked, loaded or rendered
- license verification is read from the document, not performed
- byte budgets use cooked_bytes as declared, not filesystem measurements
- dependency cycles are graph arithmetic over declared ids
- quality findings are structural heuristics, not visual review
- no scene, engine or project.godot integration

Gerado por `docs/benchmarks/m11/tools/build_kit_audit.py`; não é verificação jurídica de licença.

# NEX M11-AUDIT · Asset pipeline auditor (prototype)

**Status:** `PROTOTYPE / ANALYSIS_ONLY / NO_IMPORT / NO_COOK / NO_LICENSE_CLEARANCE`
**Work Order:** NEX-M11-AUDIT-WO-001 (Issue #16) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`AssetPipelineAuditor` consumes an `asset_pipeline.v1` contract document and returns a deterministic audit:

- Validates asset ids, kinds, source digests, stages and statuses, license fields, import settings and dependencies.
- Enforces stage order (`raw` → `imported` → `cooked` → `validated`), cooked-artifact policy, license allowlist/verification/attribution, dependency existence/self/cycles and byte/asset budgets.
- Reports quality heuristics: uncompressed texture, oversized texture, model without LODs.
- Emits `READY_FOR_INTEGRATION`, `REVIEW_REQUIRED`, `BLOCKED` or `INVALID_INPUT`, with findings and recommendations.

## Findings

| Group | Examples |
|---|---|
| Stages | `stage_order`, `stage_failed`, `stage_pending`, `cooked_artifact_missing` |
| License | `license_rejected`, `license_unverified`, `verified_license_required`, `spdx_not_allowed`, `attribution_missing` |
| Dependencies | `dangling_dependency`, `self_dependency`, `dependency_cycle` |
| Budget | `over_asset_budget`, `over_total_bytes`, `over_texture_bytes`, `over_unverified_licenses` |
| Quality | `texture_uncompressed`, `texture_oversized`, `model_without_lods` |

## API

| Method | Purpose |
|---|---|
| `load_document(document)` | Validate structure and store an `asset_pipeline.v1` document. |
| `audit()` | Deterministic findings, metrics, verdict and recommendations. |
| `get_last_report()` / `clear()` | Last report / reset. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/assets/license_audit `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M11_AUDIT_SMOKE_PASS: 43 checks`; log committed under `evidence/`.

## Limits (explicit)

- **Analysis only**: no asset is imported, cooked, loaded or rendered.
- License verification is read from the document, not performed.
- Byte budgets use declared `cooked_bytes`, not filesystem measurements.
- Dependency cycles are graph arithmetic over declared ids.
- Quality findings are structural heuristics, not visual review.
- No license clearance, quality or performance claim.
- Real pipeline integration requires a future M11 WO; M11 parent remains `NOT_ADMITTED`.

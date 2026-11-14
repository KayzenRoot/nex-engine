# NEX M12-VALIDATOR · Identity validator (prototype)

**Status:** `PROTOTYPE / ANALYSIS_ONLY / NO_ASSET_GENERATION / NO_BRAND_APPROVAL`
**Work Order:** NEX-M12-VALIDATOR-WO-001 (Issue #17) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`IdentityValidator` consumes an `identity.v1` contract document and returns a deterministic validation report:

- Validates palette tokens/roles/hex, typography, logo URIs/digests/viewBox, spacing scale and accessibility thresholds.
- Computes WCAG contrast from the declared hex values: foreground/background text contrast, primary/error/success/warning large-text contrast, accent ≥3:1.
- Checks display size > body size, unique weights and multiples of 100, positive logo viewBox, ascending spacing above base, threshold order and focus ring.
- Emits `READY_FOR_UI`, `REVIEW_REQUIRED`, `BLOCKED` or `INVALID_INPUT`, with findings and recommendations.

## Findings

| Group | Examples |
|---|---|
| Palette | `duplicate_token`, `missing_required_role`, `text_contrast_low`, `large_contrast_low`, `accent_contrast_low` |
| Typography | `display_not_larger`, `duplicate_weight`, `weight_not_multiple` |
| Logo | `view_box_invalid` |
| Spacing | `spacing_below_base`, `spacing_not_ascending` |
| Accessibility | `contrast_threshold_order`, `focus_ring_too_small` |
| Provenance | `provenance_without_evidence` |

## API

| Method | Purpose |
|---|---|
| `load_document(document)` | Validate structure and store an `identity.v1` document. |
| `audit()` | Deterministic findings, metrics, verdict and recommendations. |
| `get_last_report()` / `clear()` | Last report / reset. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/brand/tokens `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M12_VALIDATOR_SMOKE_PASS: 36 checks`; log committed under `evidence/`.

## Limits (explicit)

- **Analysis only**: no logo, theme, SVG or UI asset is generated or approved.
- Contrast is computed from declared hex values, not measured on screen.
- Typography and spacing are validated structurally, not visually.
- Brand approval and trademark review are out of scope.
- No FPS, rendering or quality claim.
- Real brand integration requires a future M12 WO; M12 parent remains `NOT_ADMITTED`.

# NEX M12-S01 · Brand master (decision record)

**Status:** `BRAND_SYSTEM_REFERENCE_FINAL / DISTRIBUTION_TRADEMARK_PENDING`
**Issue:** #17 (NEX-M12-WO-001) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`

## Decision

Direction **"Isometric N / Hex core"**: an isometric N (two verticals + diagonal) inside a hexagonal frame, with an amber baseline diamond. Palette: Graphite `#0b0f14`, Cobalt `#2f6bff`, Cyan `#35d0ff`, Amber `#ffb020`, Mist `#e8eef7`.

The public wordmark is **NEX ENGINE**, built as an outlined geometric path system in `wordmark.svg` and `logo-primary.svg`. It has no `<text>` element and no font dependency, so it is independent of licensed typefaces. Alternatives rejected: wordmark-only (weak at icon sizes), literal "N" glyph (font dependency and weak in monochrome), abstract cube (reads as a generic engine).

## Deliverables

- `assets/brand/logo-mark.svg`, `logo-primary.svg`, `logo-monochrome.svg`, `wordmark.svg`
- `assets/brand/icons/*.svg` (10 monochrome 24×24 icons)
- `assets/brand/app-icons/nex-engine-{16..1024}.png`, `.ico`, `.icns`
- `assets/brand/palette.v1.json`, `identity.v1.json`, `SHA256SUMS.txt`
- `assets/brand/BRAND-GUIDELINES.md`
- `docs/benchmarks/m12/brand-kit.v1.json`, `BRAND-KIT.md`
- `tests/ci/test_brand_assets.py`, `tests/ci/test_m12_final.py`

## Acceptance

- All SVGs parse as XML; no scripts, external references, embedded data, event handlers or `<style>` blocks.
- Primary logo and wordmark use outlined paths only; no `<text>`.
- Icons: 24×24 viewBox, `currentColor` stroke, no text, accessible label.
- Palette tokens unique and well-formed; Mist/Graphite 16.48:1, Cobalt/Graphite 4.27:1.
- Nine app-icon PNG sizes, ICO and ICNS containers generated deterministically.
- `identity.v1` validates as `READY_FOR_UI` with zero findings (14 final checks).
- Zero engine integration: no change to `project.godot`, hub, launcher, installer or CI.
- Brand assets are **not integrated into the editor, launcher or installer**.

## Pending Owner decisions

1. Distribution license for the brand assets.
2. Trademark clearance for the NEX ENGINE name and mark before public distribution.
3. Whether the editor icon set (S03) adopts this palette before a UI Work Order is admitted.

## Future phases (not admitted)

S02 SVG sources → S03 UI/editor icons → S04 build/platform icons → S05 documentation → S06 freeze. Each needs its own Work Order, file inventory and Steward lock; this record does not admit them.

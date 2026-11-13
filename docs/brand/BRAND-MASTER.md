# NEX M12-S01 · Brand master (decision record)

**Status:** `PROVISIONAL_BRAND_MASTER / NOT_INTEGRATED / NOT_DISTRIBUTION_RELEASE`
**Issue:** #17 (NEX-M12-WO-001) · **Wave:** NEX-WAVE-001 frente 4 · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`

## Decision

Direction **"Isometric N / Hex core"**: an isometric N (two verticals + diagonal) inside a hexagonal frame, with an amber baseline diamond. Palette: Graphite `#0B0F14`, Cobalt `#2F6BFF`, Cyan `#35D0FF`, Amber `#FFB020`, Mist `#E8EEF7`.

Rationale: legible at 16 px, geometry echoes the isometric ARPG camera and the measurement discipline of the project, and it avoids any third-party mark. Alternatives rejected: wordmark-only (weak at icon sizes), literal "N" glyph (font dependency and weak in monochrome), abstract cube (reads as a generic engine).

## Deliverables

- `assets/brand/logo-mark.svg`, `logo-primary.svg`, `logo-monochrome.svg`
- `assets/brand/icons/*.svg` (10 monochrome 24×24 icons)
- `assets/brand/palette.v1.json`
- `assets/brand/BRAND-GUIDELINES.md` (usage rules)
- `tests/ci/test_brand_assets.py` (structural acceptance)

## Acceptance (this increment)

- All SVGs parse as XML; no scripts, external references, embedded data, event handlers or `<style>` blocks.
- Icons: 24×24 viewBox, `currentColor` stroke, no text, accessible label.
- Palette tokens unique and well-formed.
- Guidelines state originality (not derived from the Godot logo) and the provisional wordmark rule.
- Zero engine integration: no change to `project.godot`, hub, launcher, installer or CI.

## Pending Owner decisions

1. Final wordmark: approve the provisional lettering or commission/convert to outlines.
2. Distribution license for brand assets.
3. Whether the editor icon set (S03) should adopt this palette before a UI Work Order is admitted.

## Future phases (not admitted)

S02 SVG sources → S03 UI/editor icons → S04 build/platform icons → S05 documentation → S06 freeze. Each needs its own Work Order, file inventory and Steward lock; this record does not admit them.

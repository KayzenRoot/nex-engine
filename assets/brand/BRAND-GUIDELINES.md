# NEX Engine · Brand guidelines (provisional master)

**Status:** `PROVISIONAL_BRAND_MASTER_NOT_DISTRIBUTION_RELEASE` · NEX-WAVE-001 frente 4 · Issue #17
**Scope:** identity direction, mark construction, palette, icon rules. This is a design master for future integration; it does not modify the engine UI, `project.godot`, launchers or installer.

## 1. Concept

The mark is an **isometric "N"** inside a hexagonal frame: three strokes (two verticals and a diagonal) suggest a 3D grid seen from the ARPG camera, while the hexagon reads as a bounded engine core. A small amber diamond marks the baseline (measurement) without resembling any third-party logo.

The identity is original work for NexLabs. It is **not derived from the Godot logo**, and the Godot trademark policy is respected: the engine's own branding is independent, and Godot credit remains legal text, not brand borrowing.

## 2. Files

| File | Use |
|---|---|
| `assets/brand/logo-mark.svg` | Standalone mark (app icon, splash, favicon source) |
| `assets/brand/logo-primary.svg` | Mark + provisional wordmark (documents, store pages) |
| `assets/brand/logo-monochrome.svg` | One-ink surfaces, embossing, low-color contexts |
| `assets/brand/palette.v1.json` | Machine-readable color tokens |
| `assets/brand/icons/*.svg` | 24×24 monochrome UI icons (`currentColor`) |

## 3. Palette

| Token | Hex | Role |
|---|---|---|
| Graphite | `#0B0F14` | Background |
| Cobalt | `#2F6BFF` | Primary |
| Cyan | `#35D0FF` | Accent |
| Amber | `#FFB020` | Highlight / measurement |
| Mist | `#E8EEF7` | Text |

Contrast: Mist on Graphite exceeds 15:1. Cobalt is for shapes and large text; body copy uses Mist. Amber is reserved for measurement/benchmark semantics, never for errors.

## 4. Clear space and minimum size

- Clear space: 25% of the mark height on all sides.
- Minimum digital sizes: mark 16 px (favicon), 24 px (icon), 48 px (launcher); primary logo 160 px wide.
- Never rotate, skew, outline, recolor outside the palette, or place the mark on busy photography.

## 5. Typography

The wordmark in `logo-primary.svg` uses a generic UI stack (Segoe UI/Arial) and is **provisional**. Before any public distribution it must be converted to outlines or replaced by the final licensed typeface; no font binaries are shipped by this master.

## 6. Icon rules

- 24×24 viewBox, 1.8 px stroke, round caps/joins, no fills except where geometry requires.
- `currentColor` only; icons inherit the text color.
- No text, shadows, gradients or external references inside icons.
- Icons are UI affordances, not decoration; keep one metaphor per icon.

## 7. Integration (future, not admitted)

S02 (SVG sources), S03 (UI/editor), S04 (build/platform) and S05 (documentation) remain future Work Orders under #17. Any integration that touches `nex_bench/project.godot`, editor icons or installers requires its own admission, file inventory and Steward lock. This master deliberately touches none of them.

## 8. Licensing

Original assets created for NexLabs. Until a distribution license is decided, treat them as internal project assets; third-party marks (including Godot) are not incorporated.

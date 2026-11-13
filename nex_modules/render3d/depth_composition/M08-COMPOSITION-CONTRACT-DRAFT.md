# NEX M08 2.5D composition contract — DRAFT (NOT PROMOTED)

**Status:** `DRAFT_NOT_PROMOTED / NOT_AN_ADMITTED_CONTRACT / NO_2.5D_IMPLEMENTATION`
**Origin:** NEX-M02-S03-WO-001 (Issue #30), "rascunhar contrato para integração futura com M08 2.5D sem implementar 2.5D agora".
**Owner decision required before any promotion.** This document is not canonical and does not admit M08.

## Purpose

Define the interface a future 2.5D composition layer would consume from the M02 depth planner, so 2.5D work does not silently replace the 3D depth policy.

## Proposed fields (draft)

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | const `nex_2_5d_composition.v1` | Stable identifier. |
| `base_3d_plan` | object | Reference to the M02 plan (passes, depths, risks, conflicts) with SHA-256. |
| `layer_stack` | array | Ordered 2.5D layers: `id`, `role` (`background`, `gameplay`, `foreground`, `hud`), `parallax`, `blend_mode`. |
| `depth_policy` | enum | `inherit_3d`, `override_per_layer`, `hybrid`. |
| `alpha_policy` | object | `sort` (`back_to_front`), `critical_guard` (`enabled`), `max_alpha_over_gameplay`. |
| `overlay_safety` | object | `hud_layer_id`, `may_cover_gameplay` (must be false for gameplay-critical overlays), `conflict_policy` (`report`, never silent). |
| `critical_entities` | array | IDs/flags for player and threats that must remain identifiable. |
| `provenance` | object | BASE/HEAD SHA, evidence URI, measurement status. |

## Proposed invariants

1. The 3D plan remains authoritative for 3D depth; 2.5D layers may not reorder 3D gameplay primitives.
2. Gameplay-critical entities are never silently hidden; conflicts are reported with an explicit policy.
3. Alpha policy must declare a guard; a layer with alpha above `max_alpha_over_gameplay` over a critical entity is a reported conflict.
4. HUD/overlays never enter the 3D opaque/alpha passes.
5. Any visual or performance claim requires measured evidence; missing data is `INCONCLUSIVE`, never a fabricated PASS.

## Non-goals

- No 2.5D implementation, no shader/material changes, no engine fork.
- No promotion of this draft without an Owner-admitted M08 Work Order, contract review and Context Lock.
- No dependency on unadmitted M02-S04+ behavior.

## Open questions for M08 admission

1. Layer ownership and file paths (`nex_modules/render2_5d/**`?).
2. Whether 2.5D layers share the 3D camera or an orthographic sub-viewport.
3. How HUD/overlay conflicts are surfaced to designers (warning vs hard gate).
4. Measurement protocol for 2.5D composition (same baseline/procedure as M01).

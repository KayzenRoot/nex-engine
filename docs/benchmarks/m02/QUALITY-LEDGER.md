# NEX M02 · Quality ledger (what improved, what cost, what regressed)

**Status:** `M02_RUNTIME_REFERENCE_MEASURED / S01_S02_S03_S05_RENDERED / S04_TAA_NO_GO_CUSTOM / NO_GENERAL_QUALITY_CLAIM`

| Component | What got better (structural) | What it costs | What regressed |
|---|---|---|---|
| S01 camera | Deterministic framing, dead zone, replay, contract state | Low; controller maintenance | None observed; 3D↔screen 3e-6 m; A/B framing reproduced |
| S02 Sightline | Rendered reveal policy, critical alerts, hysteresis | Medium; test wall/occluder data | None observed; GPU delta +6.0–8.6% |
| S03 DepthWeave | Rendered alpha overlay, pass ordering, conflict reporting | Medium; AABB approximations | None observed; 0 conflicts; GPU delta +0.0–3.3% |
| S04 TemporalGuard | Native TAA off/on evidence, ghosting/flicker/shimmer gate | Medium–high; region analysis | Custom compositor NO_GO; no benefit proven |
| S05 RenderPassport | Runtime probe, fallbacks, three reversible profiles | Low | None observed; GPU p95 0.758/0.571/0.182 ms by profile |
| S06 Research | Decision matrix, redundancy rejection | Low | Not applicable |

## Explicit non-claims

- No FPS, frame-time, VRAM, visual-quality or perceptual improvement is claimed.
- Structural PASS ≠ scene PASS; S01/S02/S03/S05 have rendered evidence, S04 is visual/region evidence only.
- The Quality targets in `budget.v1.json` remain aspirational.
- The only GO for a custom compositor is NO_GO; RenderPassport and the rendered S02/S03 policies are GO.

## Next data needed

1. Execute A/B/A in `corridor_static`, `arena_combat`, `dense_city` with the exact SHA/driver/procedure.
2. Capture p95/p99/1% low and GPU/CPU render time; separate screenshots from timing runs.
3. Recompute this ledger; only then may scene/performance move from `INCONCLUSIVE_NOT_RUN` to `PASS`/`FAIL`.

# NEX M02 · Quality ledger (what improved, what cost, what regressed)

**Status:** `PROPOSED / NO_MEASURED_GAIN / SCENE_AND_PERFORMANCE_UNMEASURED`

| Component | What got better (structural) | What it costs | What regressed |
|---|---|---|---|
| S01 camera | Deterministic framing, dead zone, replay, contract state | Low; controller maintenance | None observed structurally; scene unmeasured |
| S02 Sightline | Reveal policy, critical-threat alerts, hysteresis | Medium; per-scene occluder data | None observed structurally; scene unmeasured |
| S03 DepthWeave | Pass ordering, z-fight risk, conflict reporting | Medium; mocked geometry | None observed structurally; real depth unmeasured |
| S04 TemporalGuard | Ghosting/flicker/shimmer metrics and gate | Medium–high; analysis to maintain | None observed structurally; real TAA unmeasured |
| S05 RenderPassport | Capability/probe separation, fallbacks, profiles | Low | None observed structurally; driver probe unmeasured |
| S06 Research | Decision matrix, redundancy rejection | Low | Not applicable |

## Explicit non-claims

- No FPS, frame-time, VRAM, visual-quality or perceptual improvement is claimed.
- Structural PASS ≠ scene PASS; the three M01 scenes were not executed with the improvements.
- The Quality targets in `budget.v1.json` remain aspirational.
- The only GO is the RenderPassport process tool; the four render features remain `RESEARCH_MORE`.

## Next data needed

1. Execute A/B/A in `corridor_static`, `arena_combat`, `dense_city` with the exact SHA/driver/procedure.
2. Capture p95/p99/1% low and GPU/CPU render time; separate screenshots from timing runs.
3. Recompute this ledger; only then may scene/performance move from `INCONCLUSIVE_NOT_RUN` to `PASS`/`FAIL`.

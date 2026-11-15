# NEX M02 · Regression report (M01 baseline vs improvements)

**Status:** `QA_REPORT / S01_MEASURED / S02_S03_S04_ANALYSIS_MEASURED / RENDERING_AND_PERFORMANCE_INCONCLUSIVE / NO_MEASURED_GAIN`
**Baseline:** frozen M01 pack (`docs/benchmarks/m01/manifest.json`) · **Source SHA:** `9b40dac928d568cb7783b9e8ae830f35fa2acc21`
**Mechanical source:** `qa-ledger.v1.json` (`python docs/benchmarks/m02/tools/qa_ledger.py --check`).

## Component comparison

| Component | Structural | Checks | Scene comparison (3 scenes) | Performance | Verdict |
|---|---|---:|---|---|---|
| S01 camera | PASS | 32 | `PASS` | `MEASURED` | A/B/A framing reproduced; GPU delta 0.0–1.25% |
| S02 Sightline | PASS | 49 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Scene analysis PASS; rendering not measured |
| S03 DepthWeave | PASS | 37 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Scene analysis PASS; rendering not measured |
| S04 TemporalGuard | PASS | 51 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Scene analysis PASS; real TAA not measured |
| S05 RenderPassport | PASS | 87 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Structural only |
| S06 Research atlas | PASS | 16 | `NOT_APPLICABLE_RESEARCH` | `NOT_APPLICABLE_RESEARCH` | Research only |

S02/S03/S04 carry a separate `scene_analysis` PASS over real M01 scene AABBs and
static frames (`analysis-integration.v1.json`); this is not a rendering A/B/A
comparison, so the scene comparison and performance columns remain
`INCONCLUSIVE_NOT_RUN`.

## Why scene/performance are not PASS

- S01 was executed A/B/A in `corridor_static`, `arena_combat` and `dense_city` on the RTX 5050. S02–S06 were **not** executed as rendered scene comparisons; S02–S04 ran headless analyses over real M01 scene data. A scene-comparison PASS still requires A/B/A rendering with the frozen procedure.
- Performance targets (1080p60 Quality, 120 Performance) remain `ASPIRATIONAL_NOT_MEASURED`/`EXPERIMENTAL_NOT_MEASURED`. No frame-time number is claimed.
- The M01 baseline is the comparison authority; no cross-session pacing comparison is allowed.
- Missing data is surfaced as `INCONCLUSIVE_NOT_RUN`, never converted to a gain.

## Structural evidence

Each component's evidence log is hashed in `qa-ledger.v1.json`. Structural PASS means the deterministic logic tests passed; it does **not** prove visual or runtime quality.

## Gate state

- HIGH/CRITICAL defects: **0**.
- Integration: `SERIAL_STEWARD`, conflicts **0**, no external pending PR assumed.
- Owner promotion: **not requested**; the checkpoint delta is proposed only.

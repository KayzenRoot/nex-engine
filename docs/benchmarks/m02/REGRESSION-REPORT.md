# NEX M02 · Regression report (M01 baseline vs improvements)

**Status:** `QA_REPORT / SCENE_AND_PERFORMANCE_INCONCLUSIVE / NO_MEASURED_GAIN`
**Baseline:** frozen M01 pack (`docs/benchmarks/m01/manifest.json`) · **Source SHA:** `9b40dac928d568cb7783b9e8ae830f35fa2acc21`
**Mechanical source:** `qa-ledger.v1.json` (`python docs/benchmarks/m02/tools/qa_ledger.py --check`).

## Component comparison

| Component | Structural | Checks | Scene comparison (3 scenes) | Performance | Verdict |
|---|---|---:|---|---|---|
| S01 camera | PASS | 32 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Structural only |
| S02 Sightline | PASS | 49 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Structural only |
| S03 DepthWeave | PASS | 37 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Structural only |
| S04 TemporalGuard | PASS | 51 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Structural only |
| S05 RenderPassport | PASS | 87 | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` | Structural only |
| S06 Research atlas | PASS | 16 | `NOT_APPLICABLE_RESEARCH` | `NOT_APPLICABLE_RESEARCH` | Research only |

## Why scene/performance are not PASS

- `corridor_static`, `arena_combat` and `dense_city` were **not executed** with S01–S06 integrated. A PASS requires A/B/A in those scenes on the RTX 5050 with the frozen procedure.
- Performance targets (1080p60 Quality, 120 Performance) remain `ASPIRATIONAL_NOT_MEASURED`/`EXPERIMENTAL_NOT_MEASURED`. No frame-time number is claimed.
- The M01 baseline is the comparison authority; no cross-session pacing comparison is allowed.
- Missing data is surfaced as `INCONCLUSIVE_NOT_RUN`, never converted to a gain.

## Structural evidence

Each component's evidence log is hashed in `qa-ledger.v1.json`. Structural PASS means the deterministic logic tests passed; it does **not** prove visual or runtime quality.

## Gate state

- HIGH/CRITICAL defects: **0**.
- Integration: `SERIAL_STEWARD`, conflicts **0**, no external pending PR assumed.
- Owner promotion: **not requested**; the checkpoint delta is proposed only.

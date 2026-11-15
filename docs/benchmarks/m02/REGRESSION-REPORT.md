# NEX M02 · Regression report (M01 baseline vs improvements)

**Status:** `QA_REPORT / S01_S02_S03_S05_RENDERED_AND_MEASURED / S04_TAA_NO_GO_CUSTOM / NO_GENERAL_QUALITY_CLAIM`
**Baseline:** frozen M01 pack (`docs/benchmarks/m01/manifest.json`) · **Source SHA:** `9b40dac928d568cb7783b9e8ae830f35fa2acc21`
**Mechanical source:** `qa-ledger.v1.json` (`python docs/benchmarks/m02/tools/qa_ledger.py --check`).

## Component comparison

| Component | Structural | Checks | Scene comparison (3 scenes) | Performance | Verdict |
|---|---|---:|---|---|---|
| S01 camera | PASS | 32 | `PASS` | `MEASURED` | A/B/A framing reproduced; GPU delta 0.0–1.25% |
| S02 Sightline | PASS | 49 | `PASS` | `MEASURED` | Rendered reveal; GPU delta +6.0–8.6% |
| S03 DepthWeave | PASS | 37 | `PASS` | `MEASURED` | Alpha overlay with 0 conflicts; GPU delta +0.0–3.3% |
| S04 TemporalGuard | PASS | 51 | `PASS` | `INCONCLUSIVE_NOT_RUN` | Native TAA off/on; custom compositor NO_GO |
| S05 RenderPassport | PASS | 87 | `PASS` | `MEASURED` | Runtime probe + three profiles; GPU p95 0.758/0.571/0.182 ms |
| S06 Research atlas | PASS | 16 | `NOT_APPLICABLE_RESEARCH` | `NOT_APPLICABLE_RESEARCH` | Research only |

S02/S03/S04/S05 carry a separate `scene_analysis` PASS over real M01 scene AABBs
and the M02 runtime report (`runtime.v1.json`). S04 performance remains
`INCONCLUSIVE_NOT_RUN` because the TAA off/on evidence is visual/region-based,
not a performance A/B.

## Why S04 performance is not PASS

- S01, S02, S03 and S05 were executed as rendered comparisons on the RTX 5050. S04 captured native TAA off/on camera-motion sequences, but the region analyzer produced identical metrics on both modes; no custom compositor is justified and no TAA performance claim is made.
- Performance targets (1080p60 Quality, 120 Performance) remain `ASPIRATIONAL_NOT_MEASURED`/`EXPERIMENTAL_NOT_MEASURED`. No frame-time number is claimed.
- The M01 baseline is the comparison authority; no cross-session pacing comparison is allowed.
- Missing data is surfaced as `INCONCLUSIVE_NOT_RUN`, never converted to a gain.

## Structural evidence

Each component's evidence log is hashed in `qa-ledger.v1.json`. Structural PASS means the deterministic logic tests passed; it does **not** prove visual or runtime quality.

## Gate state

- HIGH/CRITICAL defects: **0**.
- Integration: `SERIAL_STEWARD`, conflicts **0**, no external pending PR assumed.
- Owner promotion: **not requested**; the checkpoint delta is proposed only.

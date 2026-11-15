# NEX M02 · QA and integration pack (S07)

**Status:** `PROPOSED_QA_PACK / S01_SCENE_AND_PERFORMANCE_MEASURED / OTHER_COMPONENTS_INCONCLUSIVE / NO_MEASURED_GAIN`
**Work Order:** NEX-M02-S07-WO-001 (Issue #34) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`.

## Contents

- `qa-contract.v1.json` — versioned QA contract: statuses, rules, three scenes, measurement procedure, interface to M03–M06.
- `qa-ledger.v1.json` — face of the pack: six components (S01–S06) with evidence paths and SHA-256, structural status, scene comparison and performance status.
- `camera-integration.v1.json` / `CAMERA-INTEGRATION.md` — S01 camera A/B/A visual and performance report on the three M01 scenes.
- `REGRESSION-REPORT.md` — M01 baseline vs each improvement; S01 is measured, S02–S05 remain `INCONCLUSIVE_NOT_RUN` and S06 is research-only.
- `QUALITY-LEDGER.md` — what improved, what cost, what regressed; no gain claim.
- `INTERFACE-M03-M06.md` — output interface for future modules.
- `tools/qa_ledger.py` — `--write` builds the ledger; `--check` fails on hash divergence, PASS without evidence, measured claim, HIGH/CRITICAL defect or non-serial integration.

## Verify

```powershell
python docs/benchmarks/m02/tools/qa_ledger.py --check
python docs/benchmarks/m02/tools/build_camera_integration.py --check
python -m unittest tests/ci/test_m02_qa_ledger.py -v
```

Expected: `QA_LEDGER_OK`.

## Current verdict

Structural: PASS for all six components. S01 camera: scene comparison PASS and performance MEASURED on the three M01 scenes; the rig reproduces the baseline framing with negligible pixel difference (0.000–0.013%) and GPU p95 delta 0.0–1.25%. S02–S05 remain `INCONCLUSIVE_NOT_RUN` (analysis-only prototypes); S06 is research-only. HIGH/CRITICAL: 0. Integration: serial Steward, no conflicts. No checkpoint is promoted by this pack.

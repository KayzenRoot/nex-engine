# NEX M02 · QA and integration pack (S07)

**Status:** `PROPOSED_QA_PACK / SCENE_AND_PERFORMANCE_INCONCLUSIVE / NO_MEASURED_GAIN`
**Work Order:** NEX-M02-S07-WO-001 (Issue #34) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`.

## Contents

- `qa-contract.v1.json` — versioned QA contract: statuses, rules, three scenes, measurement procedure, interface to M03–M06.
- `qa-ledger.v1.json` — face of the pack: six components (S01–S06) with evidence paths and SHA-256, structural status, scene comparison and performance status.
- `REGRESSION-REPORT.md` — M01 baseline vs each improvement; all scene/performance comparisons are `INCONCLUSIVE_NOT_RUN`.
- `QUALITY-LEDGER.md` — what improved, what cost, what regressed; no gain claim.
- `INTERFACE-M03-M06.md` — output interface for future modules.
- `tools/qa_ledger.py` — `--write` builds the ledger; `--check` fails on hash divergence, PASS without evidence, measured claim, HIGH/CRITICAL defect or non-serial integration.

## Verify

```powershell
python docs/benchmarks/m02/tools/qa_ledger.py --check
python -m unittest tests/ci/test_m02_qa_ledger.py -v
```

Expected: `QA_LEDGER_OK`.

## Current verdict

Structural: PASS for all six components (deterministic logic tests). Scene and performance: `INCONCLUSIVE_NOT_RUN` — the three M01 scenes were not executed with the improvements. HIGH/CRITICAL: 0. Integration: serial Steward, no conflicts. No checkpoint is promoted by this pack.

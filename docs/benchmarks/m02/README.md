# NEX M02 · QA and integration pack (S07)

**Status:** `M02_RUNTIME_REFERENCE_MEASURED / S01_S05_RENDERED / S04_TAA_NO_GO_CUSTOM / NO_GENERAL_QUALITY_CLAIM`
**Work Order:** NEX-M02-S07-WO-001 (Issue #34) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`.

## Contents

- `qa-contract.v1.json` — versioned QA contract: statuses, rules, three scenes, measurement procedure, interface to M03–M06.
- `qa-ledger.v1.json` — face of the pack: six components (S01–S06) with evidence paths and SHA-256, structural status, scene comparison and performance status.
- `camera-integration.v1.json` / `CAMERA-INTEGRATION.md` — S01 camera A/B/A visual and performance report on the three M01 scenes.
- `analysis-integration.v1.json` / `ANALYSIS-INTEGRATION.md` — S02/S03/S04 headless analyses over real M01 scene AABBs and static frames.
- `runtime.v1.json` / `RUNTIME.md` — S01 camera math/aspects, S02 sightline reveal, S03 depth overlay, S04 native TAA off/on and S05 profiles/capability passport on the native RTX 5050.
- `REGRESSION-REPORT.md` — M01 baseline vs each improvement; S01–S05 are rendered; S04 performance remains `INCONCLUSIVE_NOT_RUN`; S06 is research-only.
- `QUALITY-LEDGER.md` — what improved, what cost, what regressed; no gain claim.
- `INTERFACE-M03-M06.md` — output interface for future modules.
- `tools/qa_ledger.py` — `--write` builds the ledger; `--check` fails on hash divergence, PASS without evidence, measured claim, HIGH/CRITICAL defect or non-serial integration.

## Verify

```powershell
python docs/benchmarks/m02/tools/qa_ledger.py --check
python docs/benchmarks/m02/tools/build_camera_integration.py --check
python docs/benchmarks/m02/tools/build_analysis_integration.py --check
python docs/benchmarks/m02/tools/build_m02_runtime.py --check
python -m unittest tests/ci/test_m02_qa_ledger.py tests/ci/test_m02_analysis_integration.py -v
```

Expected: `QA_LEDGER_OK`.

## Current verdict

Structural: PASS for all six components. S01 camera: scene comparison PASS and performance MEASURED; 3D↔screen round trip 3e-6 m, fast follow ≤ 24.3 px/step and four aspect ratios captured. S02 sightline: rendered reveal in the three scenes with GPU delta +6.0–8.6%. S03 depth: rendered alpha overlay with 0 z-fight/alpha/overlay conflicts and GPU delta +0.0–3.3%. S04 temporal: native TAA off/on captured; the region analyzer is identical and a custom compositor is `NO_GO`; performance remains `INCONCLUSIVE_NOT_RUN`. S05 profiles: runtime probe on Forward+/Vulkan; quality/balanced/performance applied with GPU p95 0.758/0.571/0.182 ms. S06 is research-only. HIGH/CRITICAL: 0. Integration: serial Steward, no conflicts. No general FPS/quality claim. No checkpoint is promoted by this pack alone.

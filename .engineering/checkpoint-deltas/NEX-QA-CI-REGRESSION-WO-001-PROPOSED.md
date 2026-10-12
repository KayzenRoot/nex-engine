# NEX-QA-CI-REGRESSION-WO-001 | Proposed CI regression checkpoint delta

**PROPOSAL ONLY. NOT PROMOTED.** Linked [Issue #20](https://github.com/KayzenRoot/nex-engine/issues/20), planned Stage A Context Lock PR and subsequent separate Stage B implementation PR.

## Requested change
Required existing Fast Lane context `NEX Fast Lane / Batch Policy Tests` should fail on any failure, empty discovery, missing test directory or import error in `tests/ci`, `tests/contracts` and `tests/telemetry`; preserve all triggers, job/check names, repository permissions and the free-runner budget. Implementation is exactly one existing workflow, no test or app source change.

## Evidence prerequisites / promotion conditions
Stage A four-file Context Lock proposal, owner exact-head protected squash and complete postmerge audit -> actual new protected main SHA/pins -> exclusive single CI writer -> Stage B one-file workflow patch -> reproducible test/run evidence incl negative cases and required checks -> separate Owner exact-head protected squash -> postmerge checks + stage-specific verified test counts -> **only then** record CI guarantee as effective. No retrospective changes to completed M00/WO19/S02 status.

No version release, real GPU/FPS, instrumented test coverage or full draft JSON Schema validator claim is implied. M01 parent and S01 remain NOT_ADMITTED.

**STOP:** `PROPOSED_CI_3_SUITE_GUARD_PENDING_EXACT_HEAD_LOCK_REVIEW`.
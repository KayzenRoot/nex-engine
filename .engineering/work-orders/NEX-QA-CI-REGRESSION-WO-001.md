# NEX-QA-CI-REGRESSION-WO-001 | Fail-closed Fast Lane contract/telemetry regression checks

**WORK TYPE: NECESSARY / CI GUARANTEE / STANDARD risk. STATE: OWNER SCOPE ADMITTED, STAGE A PROPOSAL ONLY, STAGE B BLOCKED until protected lock promotion.** This is a narrow follow-on within [Issue #20](https://github.com/KayzenRoot/nex-engine/issues/20#issuecomment-6129959929), not a new engine module or admission of M01. Stage A review actor ChatGPT NOT_INDEPENDENT.

## Verified sources / authority
Current protected main observed: `6d04200bb348a8cfeffd081b9bca6f9b51b5a9d2`, exact tree `326ab7fd8c5531422a0148ec7b9898128d8db3ec`, 21 direct Git blob SHA-1 source pins in accompanying Context Lock. [PR #98 Stage B checkpoint](https://github.com/KayzenRoot/nex-engine/pull/98) protected merged and postmerge [12/12 checks + 6/6 workflows verified](https://github.com/KayzenRoot/nex-engine/issues/96#issuecomment-6129837474). `.engineering/CHECKPOINT.{json,md}` now records bounded v1 contracts + synthetic S02 integrated, while M01 parent/S01 are NOT_ADMITTED.

### Root cause
Required `NEX Fast Lane / Batch Policy Tests` workflow invokes **only** `python3 -m unittest discover -s tests/ci`; it does NOT execute real `tests/contracts` and `tests/telemetry` test trees, so protected PR and push-green statuses cannot guarantee regressions of contract validation and FramePulse. The suites are stdlib Python and present on main. Green static checks and previously executor-reported local tests are not substitutes.

## Stage A: immutable planning/lock PR only
Only these FOUR new governance paths may appear in Stage A Git diff:
- `.engineering/work-orders/NEX-QA-CI-REGRESSION-WO-001.md`
- `.engineering/context-locks/NEX-QA-CI-REGRESSION-WO-001-EXECUTION.json`
- `.engineering/evidence/NEX-QA-CI-REGRESSION-WO-001-ADMISSION-EVIDENCE.md`
- `.engineering/checkpoint-deltas/NEX-QA-CI-REGRESSION-WO-001-PROPOSED.md`

This lock is a **proposal** until Owner separately authorizes its exact HEAD/base/tree protected squash and postmerge CI is audited; creating an issue comment or branch is not promotion.

## Stage B: singular CI workflow implementation, later
**Exactly ONE writable existing file** `.github/workflows/nex-ci-fastlane.yml` with Git blob `0a8b477a0b4c6e4c2f256eff78221b9ba691fcfb`. All 20 remaining pinned files READ-ONLY, along with every unlisted path. After promoted lock + new actual main rebind + exclusive Integration Steward lease and no competing CI writers, implement within one separately reviewed branch/PR only.

Keep workflow name, `policy-tests` job and required context `NEX Fast Lane / Batch Policy Tests`, `pull_request/main` and `push/main`, `contents:read`, pinned checkout, credentials false, default free `ubuntu-latest`, 10m job budget. Must run existing `tests/ci` plus `tests/contracts` and `tests/telemetry` **from repository root, fail-closed**. Recommended Python implementation uses stdlib `unittest.TestLoader.discover(start_dir=...,pattern='test_*.py')`; checks `Path(...).is_dir()`, `suite.countTestCases()>0`, `TextTestRunner(verbosity=2).run(suite).wasSuccessful()` for EACH suite; terminate nonzero on discovery/failed tests. Preserve `tests/contracts/test_ownership_locks.py` local-module import context and `tests/telemetry/test_framepulse.py` root package imports. Do not add a standalone script file unless approved by expanded Owner allowlist.

## Stage B acceptance / test cases
1. Verify real 3-suite test counts and commands from exact-head GitHub required job, record exit codes and logs; no zero-test false green.
2. Negative controls in a disposable, isolated test environment, NOT protected main: missing suite, empty suite, intentionally failing test and import error **all fail gate**; baseline tests/ci still run; controlled changes never enter tracked repository paths.
3. Preserve job identifier and ALL six mandatory free protected contexts (CodeRabbit optional), no new packages, cloud paid runners, altered timeout/permissions, action hash or security settings.
4. PR contains EXACTLY one permitted workflow diff. Review HEAD, base, tree, zero unresolved threads, CI, risks and rollback. **Distinct Owner exact-HEAD protected squash authorization** needed for Stage B; postmerge push re-runs three suites.
5. Existing contract test validator implements LIMITED supported schema keywords, NOT standards-complete Draft 2020-12. S02 test output is SYNTHETIC_NOT_MEASURED, NOT native FPS, GPU or VRAM. Do not claim achieved coverage% solely because tests run.

## Out of scope / residual risk
No M01 parent/S01/M12 admission, no engine or contract changes, no checkpoint edits, no test edits, no native build and no auto-merge. Live `AGENTS.md` still has an earlier historical line saying Stage B checkpoint was proposed: use actual postmerge Git audit and current promoted checkpoint as factual truth; record for a separate future governance status cleanup, do not modify outside allowlist. Stop on actual Source Hierarchy conflict, stale pin or discovered writer conflict.

**STOP Stage A:** `NEX_QA_CI_LOCK_PROPOSAL_READY_OWNER_EXACT_HEAD_DECISION`.
**STOP Stage B:** `NEX_QA_CI_ONE_WORKFLOW_PR_REVIEW_OWNER_MERGE_DECISION`.
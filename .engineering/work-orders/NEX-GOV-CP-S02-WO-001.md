# NEX-GOV-CP-S02-WO-001 | S02 postmerge checkpoint reconciliation

**STATUS: PROPOSED_SCOPE / LOCK_PROMOTION_PENDING / STAGE_B_NOT_ADMITTED.** Issue [#96](https://github.com/KayzenRoot/nex-engine/issues/96). Parent M01 #6 remains NOT_ADMITTED/NOT_STARTED.

## OBJECTIVE / CONTEXT
Correct historical-current status contradictions after completed S02 child PR #95, without altering any existing accepted decisions or admitting gameplay, runtime/GPU, S01 or broader M01. Source: [Issue #22 final audit](https://github.com/KayzenRoot/nex-engine/issues/22#issuecomment-6127892436); protected main baseline `ef20ad4e03e3fd588ec6f6386fd88ce45e1dd6cd`, tree `ee8d5695c1cc94416aa155e19dbfd776b710645c`. Git/code/CI evidence prevails over stale project descriptions.

## TWO GATED INCREMENTS / SCOPE
**Stage A, proposal only:** immutable governance Work Order, proposed Context Lock, admission evidence, proposed Checkpoint Delta; these FOUR files are the only permitted changed paths:
- `.engineering/work-orders/NEX-GOV-CP-S02-WO-001.md`
- `.engineering/context-locks/NEX-GOV-CP-S02-WO-001-EXECUTION.json`
- `.engineering/evidence/NEX-GOV-CP-S02-WO-001-ADMISSION-EVIDENCE.md`
- `.engineering/checkpoint-deltas/NEX-GOV-CP-S02-WO-001-PROPOSED.md`

**Stage B, FUTURE ONLY after protected lock, full postmerge SHA attestation, Owner scope admission and exclusive writer:** update exactly SEVEN already-existing canonical files:
- `.engineering/CHECKPOINT.json`
- `.engineering/CHECKPOINT.md`
- `.engineering/DECISIONS-LEDGER.md`
- `.engineering/BACKLOG.md`
- `.engineering/SCOPE.md`
- `AGENTS.md`
- `.engineering/work-orders/NEX-M01-S02-WO-001.md`

This current PR must never modify the Stage B paths. No other files are allowed without new Owner-reviewed Context Lock.

## SOURCES TO READ
`AGENTS.md`, `.engineering/SOURCE-HIERARCHY.md`, `CHECKPOINT.{json,md}`, `DECISIONS-LEDGER.md`, `SCOPE.md`, `DEFINITION-OF-DONE.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `SECURITY.md`, `TEST-BENCHMARK-PLAN.md`, `BACKLOG.md`, `DEPLOYMENT.md`, `PROJECT-OVERVIEW.md`, S02/WO19 locks and issues, actual main Git tree. This lock pins **37 exact blob hashes**.

## REQUIREMENTS / ARCHITECTURE
Additive reconciliation only. Keep all old ledger entries verbatim; append an evidence-based superseding entry. Preserve historical `mainObservedSha` as pre-lock snapshot, do not fabricate future squash hash. In current checkpoint, distinguish M00 baseline, WO19 contracts integrated and S02 synthetic child verified; parent M01 still NOT_ADMITTED. No full schema validator, 60/120 real-FPS, actual GPU/VRAM profiling, verified coverage, independent Windows local-run or 5/5 native batch claims.

## OUT OF SCOPE / CONSTRAINTS
No code/tests/dependencies/CI, no M01 parent admission, no other WOs, no binary/distribution/benchmark, no history rewrite, no secrets, no auto-merge, no stale Context Lock. Source Pack changes occur ONLY on a distinct Stage B PR after explicit promotion. ChatGPT review = NOT_INDEPENDENT.

## ACCEPTANCE CRITERIA / TESTS / EVIDENCE
Stage A: verify base SHA/tree + 37/37 source pinset; parse JSON; exact four-file diff; no extra changes; all SIX mandatory free protected checks and applicable extras pass at PR HEAD; zero unresolved threads; separately Owner-authorized protected squash, then audit actual new main sole parent/tree/changed paths and postmerge checks before Stage B.
Stage B: validate checkpoint JSON syntax + key preservation, consistency with MD/Backlog/Scope/Ledger/AGENTS/WO, origin SHA + frozen blobs; exact seven-file diff, no unadmitted execution; no test claim without actual evidence. Separate Owner exact-head approval again, postmerge audit and only then canonical checkpoint promotion.

## DELIVERABLES / REVIEW FORMAT
Stage A: work order, lock JSON, evidence, proposed delta and one PR. Stage B after gate: one scoped implementation governance PR, Evidence Bundle and proposed Checkpoint Delta, technical audit in PT-BR `APPROVED / CORRECTION_REQUIRED / BLOCKED`, only then owner/merge/postmerge. Stop on STALE/missing checks/high risk.

**STOP STAGE A:** `NEX_GOV_CP_S02_LOCK_PROPOSAL_REVIEW_OWNER_DECISION`.
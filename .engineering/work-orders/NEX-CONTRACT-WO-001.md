# NEX-CONTRACT-WO-001 | Minimal common contracts and ownership
**Issue:** #19 · **Owner:** KayzenRoot · **Risk:** STANDARD if JSON-only, ELEVATED if native ABI/core proposed · **Approval:** 2026-10-12 Owner scope approval in [Issue #19](https://github.com/KayzenRoot/nex-engine/issues/19#issuecomment-6122906159).
**Status:** OWNER_SCOPE_APPROVED / EXECUTABLE_ONLY_AFTER_PROTECTED_LOCK_PROMOTION_AND_POSTMERGE_SHA_FINGERPRINT_ATTESTATION / NO_EXECUTION UNTIL VERIFIED. **M01 NOT_ADMITTED.**

## Objective
Freeze two tiny versioned JSON contracts for independent future M01 scene fixture and synthetic telemetry collectors, plus ownership constraints. Work is contracts-only: no Godot C++ ABI, rendering engine, editor, game scene, telemetry measurements, or local GPU tests.

## EXACT implementation FILES_ALLOWED (six)
- `contracts/m01/scene_manifest.v1.schema.json`
- `contracts/m01/telemetry_run.v1.schema.json`
- `contracts/m01/ownership.v1.json`
- `contracts/README.md`
- `tests/contracts/test_m01_schema.py`
- `tests/contracts/test_ownership_locks.py`

All other paths READ_ONLY/forbidden, especially Source Pack, workflows, global config, project.godot, toolchain, Godot native sources, consumer implementations, secrets and `main`. Only the Integration Steward owns these shared schema files; one writer, zero overlapping worktrees. Allowlist expansion or schema-wide/API changes require a separate Owner decision.

## Strict preflight
1. Read canonical Source Hierarchy, Checkpoint JSON/MD, Decisions Ledger, SCOPE, DoD, Security, active WO and promoted execution Context Lock on protected main.
2. Verify actual post-promotion main SHA, lock fingerprints, passed checks and external SHA attestation in Issue #19. The lock's authorityBaseSha is historic snapshot and not its own future squash SHA.
3. Verify no branch/worktree lock conflicts, single Steward lease, clean Codex Desktop LOCAL repo. Any mismatch is STALE; stop without edits.
4. No new libraries/APIs/purchases: use stdlib Python unittest/JSON; if JSON Schema library necessary, first report extra dependency and seek Owner scope approval; do not silently add package.
5. Create only separate `feat/nex-contract-wo-001-<slug>` implementation branch/worktree after promotion.

## Required contracts
**scene_manifest.v1.schema.json:** JSON schema dialect explicit, stable scene ID/revision/seed, scene_SHA256, camera preset/renderer/quality/resolution, asset digests/attribution/license; reject invalid/missing data.
**telemetry_run.v1.schema.json:** version/run ID, 40-hex git_sha, scene ID/digest, renderer/toolchain/hardware, warmup/sample counts, monotonic clock/time units, frame time ms, explicit unavailable GPU/VRAM provenance. Never pretend headless CI provides FPS or GPU timings.
**ownership.v1.json:** unique writer per exact allowed implementation path; future consumers may only READ contracts; dependency DAG must have no cycle, stale consumer on breaking schema revision.

## Contract tests / negative cases
Python `unittest` discover targeted tests; validate JSON and logical schema/fixture using Python stdlib or approved dependency; reject NaN/Inf, invalid 40hex sha, bad scene checksum, missing license, invalid units, negative timings/sample mismatch, absent-vs-zero GPU values, duplicate owner, writable glob overlaps and cyclic DAG. Two isolated mock consumers, NOT M01 actual components. Test no unexpected native/CI/file edits; archive real outputs without secrets.

## Review, checks and STOP
Six active free mandatory checks on exact new PR head: NEX Free Review / Static, NEX Fast Lane / Batch Policy Tests, NEX Governance / Source Pack, SonarCloud Code Analysis, Socket PR Alerts & Socket Project Report. Applicable extra checks must pass; no waiting CodeRabbit. Open ONE bounded implementation PR with evidence, do not merge until Owner authorizes that reviewed exact HEAD/base. Steward audits postmerge before future M01 proposal is considered. No M01 auto-admission.
STOP=`CONTRACTS_IMPLEMENTATION_PR_EXACT_HEAD_READY_FOR_REVIEW_WITHOUT_MERGE`; on failure `STALE_OR_BLOCKED`.

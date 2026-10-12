# Work Order NEX-M00-WO-001 | Native Godot baseline
**Owner:** KayzenRoot. **Owner approval:** 2026-10-11 (Issue #5). **Class:** NECESSARY. **Risk:** STANDARD, elevated if license/core/toolchain drift. **Status:** IMPLEMENTATION_VERIFIED_POSTMERGE / CHECKPOINT_PROMOTION_SEPARATE. Review and Owner authorization for PR #78 complete; recorded SHA `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`. No work until the exact new main SHA is attested after the lock's squash merge and the Integration Steward issues a single-writer lease. **Executor:** Codex Desktop LOCAL + Integration Steward; ChatGPT repairs reviewed issues first per ADR-0002.
## Objective
Deliver a reproducible, **unmodified Godot 4.7.2-stable** editor/runtime baseline and provenance evidence for native Windows, with Ubuntu headless smoke. No renderer, gameplay or module feature implementation.
## Preconditions (gates)
1. Completed GEF #1 and checkpoint #75: `main` at current verified SHA, `gefInstalled/gefInitialized/ciExactHead=VERIFIED` and no stale Source Pack.
2. M00 governance PR #76 (ADR-0003, Scope/DoD/Test Plan/Security) squash merged to `10054a2d7038b2677bc00fa9279a754e08adc5fb`, CodeRabbit/Socket/Sonar/CI and 6/6 post-merge checks verified.
3. This M00 execution Context Lock was authored after PR #76 merge using `10054a2d7038b2677bc00fa9279a754e08adc5fb` as Source Pack authority base with exact Git blob fingerprints. It becomes **ADMITTED only after its own protected PR merges**. Git cannot pre-embed its own future squash SHA: the runtime base must be read back and independently attested in Issue #5 before code.
4. Exclusive Steward lease (no overlapping writer, branch, worktree or GPU run); repo & Windows environment inspected before changing files.
## Files and boundaries
**Proposed write scope, to freeze in execution lock:** `tooling/godot/**`, `.nex/toolchain/**`, `tests/m00/**`, `.github/workflows/nex-m00-smoke.yml`, `.engineering/evidence/NEX-M00-WO-001-*.md`, M00 proposed checkpoint delta. `project.godot` or common settings require explicit Steward approval and individual path ownership; avoid entirely for the first smoke if disposable fixture suffices.
**Read-only:** `AGENTS.md`, `.engineering/` canonical sources, `.gef/**`, `package.json`, `package-lock.json`, other WOs/modules/contracts. **Forbidden:** `main`, user secrets, upstream Godot source edits, out-of-scope artifacts, deleting untracked files/unknown state, publishing executables without license review.
## Execution phases
**P0:** read Source Pack+lock, verify observed main/fingerprints, local Git clean and exclusive lease; inspect compiler versions, disk/RAM, no surprise downloads. **P1:** verify official tag SHA, source archive SHA256 and third-party licenses; record toolchain manifest. **P2:** test official editor/runtime and small disposable project on Windows; build unmodified source if toolchain/budget viable with full output logs; avoid benchmarking GPU yet. **P3:** add constrained Ubuntu headless smoke in CI, unit/safety checks for manifests and negative checksum/command errors; attach evidence. **P4:** open single implementation PR; stop for independent CodeRabbit/Socket/Sonar/CI and exact-head review. Do not merge or self-promote.
## Acceptance
- Source tag and archive hash VERIFIED; compiler/build flags, binaries and logs reproducible or explicitly INCONCLUSIVE if native build unavailable.
- Windows editor start, headless minimal scene/project smoke, CLI version, exit codes; CI Ubuntu runs at exact PR HEAD, no out-of-scope patch.
- Third-party notices accounted for; no HIGH/CRITICAL issue; Source Pack and GEF unmodified; Evidence Bundle with links, checksums, CPU/RAM/disk usage if measured; proposed Checkpoint Delta only.
- If source Windows compilation not proved, M00 cannot claim complete; diagnostics alone do not satisfy DoD.
## STOP CONDITION
`NEX_M00_WO_001_READY_FOR_EXACT_HEAD_REVIEW` on implementation PR; `STALE` for SHA/lock drift, `BLOCKED` for unknown licenses, permission, resource or safety failures; never advance M01 automatically.

## Final evidence / closure (2026-10-11)
- Implementation PR #78 reviewed at `8c26ecc019b05edef5839f21c43b4af72bb34d9c`, squash `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`; exact Git tree SHA identical; postmerge 6/6 checks SUCCESS. See `.engineering/evidence/NEX-M00-WO-001-POSTMERGE-EVIDENCE.md`.
- CD-003 10/10 start tests PASS; cause of earlier `0xC0000005` unknown, Owner accepted bounded residual risk. No cloud GPU or paid services, renderer fork, M01, release or FPS claim. Stop condition reached for M00 implementation; promote checkpoint only by separate reviewed governance PR. M01 NOT_ADMITTED.

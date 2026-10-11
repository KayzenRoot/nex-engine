# NEX-M00-WO-001 | Final post-merge evidence for checkpoint promotion

**Verification:** M00 implementation PR #78 merged with exact-tree identity. This file is a checkpoint-promotion proposal and is not itself authority to merge another PR or admit M01.

## Provenance and Git identities
- Official Godot `4.7.2-stable`, source commit `ed1daf0bf001b61586d9930840f2f1394092c079`, archive SHA-256 `a18ce0ccec3ecc40b0dd6c4f5132ca934e9fb7c2979717940ff32aee1eb35481`.
- [PR #78](https://github.com/KayzenRoot/nex-engine/pull/78) reviewed HEAD `8c26ecc019b05edef5839f21c43b4af72bb34d9c`; old `main`/PR base `c4174573086df365aadc72967e4722b2cbe6f3ac`; protected squash merge/new main `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`.
- Reviewed PR HEAD tree AND promoted main tree: `fedcac4bfbc06dce2d21aa3d5d6ce4a19826fdac` (exact match). New main's only parent is the expected former main SHA. Base-to-merge comparison shows only the eight approved M00 files, no extras.
- Ruleset #24864413 active; no bypass, force push or unrelated source/core changes. Owner explicitly accepted the residual historical startup risk and tree-equivalence verification prior to authorizing PR #78 exact-HEAD squash.

## Test and workflow evidence
- Native Windows Godot source build: [M00 exact-head run #38175760924](https://github.com/KayzenRoot/nex-engine/actions/runs/38175760924), SCons exit 0 after ~5,236 seconds. Windows editor/scene and Ubuntu headless smokes SUCCESS. Windows local M00 test suite 17/17 PASS.
- Windows source-build artifact ID `11717936580` API ZIP digest `49321572bd5e097f8762b9675c44562b079e01ad381465b9aea2eb9c90690dea`; internal package `043a25bce0ea433da68a0ef0eeaae60798f6d605cde6fc09f8ae601d987e1a76`; editor `cba2434252fe40dd940e19ffaf8d6ac412937a9577452dd471b781cfb7481372`; console editor `4b3a08478695d0551ce11729159dbdd3daa179c84ef10b12c5d599f15e85cad2`.
- CD-003 [startup matrix](https://github.com/KayzenRoot/nex-engine/pull/78#issuecomment-6115141428): 5/5 isolated fresh-user-data and 5/5 warm-user-data editor smokes exit 0, no observed crash events. Raw logs and 107-file hash index retained on local D: and reported in GitHub, not independently downloaded in full by ChatGPT.
- Exact reviewed PR HEAD: 10/10 GitHub check runs SUCCESS, CodeRabbit SUCCESS, zero unresolved review threads.
- New main SHA: **6/6 SUCCESS**: [GEF Windows+Ubuntu run #38185193893](https://github.com/KayzenRoot/nex-engine/actions/runs/38185193893), [Governance Source Pack+PowerShell run #38185193916](https://github.com/KayzenRoot/nex-engine/actions/runs/38185193916), SonarCloud and Socket Project Report.
- [Issue #5 postmerge audit](https://github.com/KayzenRoot/nex-engine/issues/5#issuecomment-6115221416). The M00 workflow only runs on `pull_request`. No fresh M00 native build on the squash SHA is claimed; the approved Git-tree SHA equivalence reuses exact-head evidence. CodeRabbit and Socket PR alerts are PR-specific.

## Bounded approval, risk and stop
- M00 baseline native Windows source-build/editor/runtime and Ubuntu smoke have been verified. It is **not** a finished NEX Engine product, FPS benchmark, game installer or renderer fork.
- The historical local `0xC0000005` cause remains UNKNOWN; no recurrence in 10 CD-003 tests. Owner explicitly accepted residual risk; no claim of root-cause fix.
- SonarCloud new-code coverage was reported 0.0% and four complexity annotations despite Quality Gate PASS; test executions are recorded but coverage instrumentation remains unproven.
- GEF npm-signature and doctor REVIEW/INCONCLUSIVE caveats are carried forward, not silently converted to PASS.
- ChatGPT audit is NOT_INDEPENDENT. The checkpoint promotion requires a separate governance PR with exact-head external checks/Owner decision and postmerge validation.
- **M01 is NOT_ADMITTED/NOT_STARTED**; a separate Owner-approved work order/lock is required. No automatic next increment.

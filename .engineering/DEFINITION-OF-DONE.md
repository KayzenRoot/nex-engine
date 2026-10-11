# Definition of Done · NEX Bootstrap
Status: CANONICAL_BOOTSTRAP_DOD_VERIFIED_BY_PR74_POSTMERGE_AFTER_CHECKPOINT_PROMOTION; applies only to the GEF bootstrap, NOT to the future Godot engine.
NEX-GEF-WO-001 is done only if:
1. Current governing Source Pack is reviewed, merged and coherent.
2. The GEF CLI package is locked at v1.1.2, available locally and in reproducible CI.
3. GEF init preview is inspected, safe apply succeeds and managed state is valid.
4. CLI version/help/doctor/status results are recorded with exit codes; findings or unknowns are accounted for, not papered over.
5. Exact implementation PR HEAD has required CI passing, code/security/collision tests appropriate to risk and no unresolved known HIGH/CRITICAL.
6. Evidence Bundle, base/head SHAs, owner exact-head audit and Checkpoint Delta review are complete; merge and post-merge checks confirmed before checkpoint promotion.
A drafted plan, issue, open PR or CLI install on an unrelated machine does NOT satisfy DoD.
No scope/percentage claims for the eventual Godot-based engine.

Evidence for the bounded bootstrap DoD: [PR #74](https://github.com/KayzenRoot/nex-engine/pull/74) merged to `570d0671ed57f5cd29932baf0bac26345efca279`, exact-head CodeRabbit, Socket x2, SonarCloud, GEF Windows/Ubuntu and Governance x2 all SUCCESS, post-merge main CI six SUCCESS, owner audit comment and separate checkpoint promotion PR. Security caveats remain documented. No engine-specific DoD/percentage is inferred.

## M00 DoD is distinct from GEF DoD
The Godot M00 baseline is NOT yet admitted by this update alone. After governance promotion and a fresh execution lock, M00 acceptance follows `.engineering/m00/M00-SCOPE-AND-DOD.md` and `.engineering/m00/M00-TEST-PLAN.md`. Passing GEF tests is not a substitute for a native editor/runtime build.

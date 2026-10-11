# Definition of Done · NEX Bootstrap
Status: CANONICAL_AFTER_GOVERNANCE_PR_MERGE (bootstrap policies only, GEF NOT_VERIFIED).; applies to bootstrap phase only, NOT the future graphics engine.
NEX-GEF-WO-001 is done only if:
1. Current governing Source Pack is reviewed, merged and coherent.
2. The GEF CLI package is locked at v1.1.2, available locally and in reproducible CI.
3. GEF init preview is inspected, safe apply succeeds and managed state is valid.
4. CLI version/help/doctor/status results are recorded with exit codes; findings or unknowns are accounted for, not papered over.
5. Exact implementation PR HEAD has required CI passing, code/security/collision tests appropriate to risk and no unresolved known HIGH/CRITICAL.
6. Evidence Bundle, base/head SHAs, owner exact-head audit and Checkpoint Delta review are complete; merge and post-merge checks confirmed before checkpoint promotion.
A drafted plan, issue, open PR or CLI install on an unrelated machine does NOT satisfy DoD.
No scope/percentage claims for the eventual Godot-based engine.

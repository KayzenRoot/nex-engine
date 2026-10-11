# Security · Bootstrap
Status: CANONICAL_AFTER_GOVERNANCE_PR_MERGE (bootstrap policies only, GEF NOT_VERIFIED).
No secrets, API tokens, auth material or private GEF journals in tracked files, issue bodies, evidence or logs.
Use the npm registry package pinned at v1.1.2; upstream release cites source commit af1fe9371a3883cbd8a4aafcbb405ddcd4c2ca82 and verified npm integrity/provenance; verify installed artifact/environment rather than presuming the consumer result.
Installation and GEF init apply run with least privileges after read-only preview and inspection. Never run untrusted hooks or overwrite unknown/owned files to force PASS.
Do not bypass branch protection, reviewers, required CI or code-review gates; no force push or history rewrite.
If SECURITY, RECOVERY_REQUIRED, collision, unexpected permissions, unknown source/HEAD or high-severity defect is observed: STOP=BLOCKED with evidence, retain journals and state.
No paid external service or real authentication in this increment.

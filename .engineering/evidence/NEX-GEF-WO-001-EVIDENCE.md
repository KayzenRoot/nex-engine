# NEX-GEF-WO-001 | Evidence Bundle (DRAFT, not a PASS)
**Repository:** KayzenRoot/nex-engine. **PR:** https://github.com/KayzenRoot/nex-engine/pull/74
**Execution base/main:** `bd2b0073dc8121290c696647e9c631cadc83c881`. **Pre-report HEAD:** `437b1d74199e7b10393ad5cf3d4b3deeace6b10f`.
**Report commit's own HEAD:** must be obtained from GitHub readback after this document is committed; do not treat the pre-report HEAD as final PR HEAD.
**Work Order:** Issue #1. **Risk:** STANDARD, with elevated caution on Git executable trust and external code checks.
**Status:** CORRECTION REQUIRED / NOT MERGEABLE. Checkpoint Delta is a proposal only.

## Source authority and scope
Read `.engineering/CHECKPOINT.{json,md}`, Source Hierarchy, Decisions, Scope, Architecture, Security, DoD and NEX-GEF-WO-001. Only GEF 1.1.2 installation/validation tooling, tests, workflows, lock and managed init state are admitted. No M00/Godot work. Scope-fix commit `55d123c` added the existing collision fixture, init state and receipt to the actual execution lock's enumerated writeScope; final Owner/Steward audit of this reconciliation remains mandatory.

## Evidence from GitHub CI, not from an invented local run
At `437b1d74199e7b10393ad5cf3d4b3deeace6b10f`, independently fetched from GitHub:
- `GEF smoke / ubuntu-latest`: SUCCESS.
- `NEX Governance / Source Pack`: SUCCESS.
- `NEX Governance / PowerShell`: SUCCESS.
- Socket Security Pull Request Alerts and Project Report: SUCCESS.
- `GEF smoke / windows-latest`: FAILURE.
- `SonarCloud Code Analysis`: FAILURE, reported Security Rating C. GitHub surfaces check status, but precise rule IDs/issue lines were not accessible using the connected tools; do not infer them.
- CodeRabbit: PENDING after recent corrections; the original four review threads were resolved. Recheck on final commit.
**Log links:** Ubuntu https://github.com/KayzenRoot/nex-engine/actions/runs/38114298751 and Windows same run, Sonar https://sonarcloud.io/dashboard?id=KayzenRoot_nex-engine&pullRequest=74.

Windows hosted GitHub Actions GEF CLI doctor + init preview report:
```json
{"dirtiness":"UNKNOWN","observationLimits":["WORKING_TREE_NOT_OBSERVED","DIRTINESS_UNKNOWN:GIT_TOOL_UNAVAILABLE"],"gitToolchain":{"presence":"UNAVAILABLE","gaps":["gef.cli.git.physical_path_writable_by_process"]}}
```
This is a **safe refusal** by upstream GEF v1.1.2 Git physical-executable trust policy. A Git install existing on PATH is NOT proof of trusted executability. The hosted Windows runner account can open the machine Git binary for writing; the upstream policy refuses this. Do NOT bypass, monkeypatch, disable checks, mark UNKNOWN=CLEAN or describe Windows as PASS.

Ubuntu test correction: fixture used a pre-existing non-JSON `.gef/init-state.json`; GEF's actual public refusal is `gef.precondition.mutation_refused` with summary `Apply blocked because dry run is STALE`. The new smoke asserts that observed precondition, sentinel unchanged, no private artifacts or Git mutations. It does **not** claim to prove transaction-layer exclusive-create collision. Negative test details must remain clear.

## Corrective commits (same PR/branch, no force-push)
- `e9469f7`: full action SHAs, checkout token persistence disabled.
- `55d123c`: reconcile Context Lock writeScope with already-submitted artifacts.
- `05cf629`, `c15f241`: fail-closed null repository verdict and diagnostic Git-tool trust gaps.
- `835deb7`, `8043345`, `b5f3b9e`, `437b1d7`: refine negative fixture until test matches verified public GEF STALE refusal; all earlier failed tests are preserved in Actions history, not relabeled PASS.
- CodeRabbit initial four finding threads resolved; latest HEAD still requires its own external check.
All patch effects bounded to workflow, tests and admitted lock/records. No system ACL, OS credentials, runtime engine or Git history modified.

## Local executor evidence that still requires independent inspection
Codex Desktop reported Node 22, npm ci, GEF 1.1.2 pinned, tarball SRI/sha and SLSA source match; `gef init --apply` succeeded with plan digest `5140fb6c68fb59d2d31e4c5aed1e2dd99e60608568d6659f1a40c417a472514d`, and its receipt is tracked. These are **executor claims and committed artifacts**, not certification of the final PR HEAD. `npm audit signatures` was INCONCLUSIVE (E404 for bundled `@gef-bootstrap/project-identity@0.0.0`), distinct from `npm audit --audit-level=high` which reportedly found zero vulnerabilities. `gef doctor` security.dependency/security.github REVIEW and unsupported `CHECKPOINT.json` schema remain caveats.

## Residual correction delta / no-go criteria
1. **Windows trust/functional proof**: run the exact pinned smoke under a controlled Windows non-admin user with Git in a genuinely machine-protected installation and gather exit codes + redacted CLI doctor + preview results. If Git is still classified untrusted, fail closed and investigate the underlying installed Git path/ACL with upstream GEF policy; hosted-runner cannot silently stand in for native proof. A Windows-only negative test can document expected refusal but cannot be labeled as functional smoke PASS.
2. **Sonar**: inspect PR #74 Security Rating C issue-level details on authenticated SonarCloud account. Return rule key, file/line, explanation and status for each finding. Repair only verified within-WO findings in the existing PR; do not change Quality Gate or dismiss vulnerabilities to force green.
3. **Review**: final CodeRabbit SUCCESS, 2 Socket checks, required Linux/Windows/Quality checks, no HIGH/CRITICAL, Context Lock owner reconciliation, exact final SHA audit, then Owner approval. No checkpoint promotion before merge and post-merge tests.

## STOP and proposed checkpoint
`BLOCKED_WINDOWS_TRUST_AND_SONAR`; `gefInstalled=NOT_VERIFIED`, `gefInitialized=NOT_VERIFIED`, `ciExactHead=NOT_VERIFIED` in canonical checkpoint; `M00=NOT_ADMITTED`. See sibling `.engineering/checkpoint-deltas/NEX-GEF-WO-001-PROPOSED.md`. No automatic completion or release.

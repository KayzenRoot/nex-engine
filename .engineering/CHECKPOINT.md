# Checkpoint · NEX Engine
Status: M00_ADMITTED_BASELINE_NOT_STARTED, effective only after the M00 execution-lock PR is reviewed, squash merged and verified. M00 code execution still requires current-main SHA attestation, exclusive Steward lease and local preflight.

## Source authority / promotion
- Planning Source Pack PR #2 squash merged as `a238f610f0c1bfc2e45b33b38c45dec2ab39ca3c`.
- Governance PR #72 squash merged as `55f92d1942e810e75aac6faf8231427a6b11c346`, NEX-ADR-0002 ChatGPT-first repair effective.
- Main Ruleset preparation PR #73 squash merged as `bd2b0073dc8121290c696647e9c631cadc83c881`.
- GitHub Ruleset #24864413 ACTIVE, strict PR/squash, no bypass, CodeRabbit and both Socket checks required, conversations resolved, no force-push/deletion.

## NEX-GEF-WO-001 completion proof (bootstrap only)
- GEF implementation PR #74 exact reviewed HEAD `8b1f2318d5b5ebb657d55d04da3eda57153dd0ee`, squash merged to `main` as `570d0671ed57f5cd29932baf0bac26345efca279`.
- Source Lock execution base was `bd2b0073dc8121290c696647e9c631cadc83c881`; independently compared 24/24 canonical Git blob fingerprints before merge; all matched. GitHub readback confirmed new `main` commit.
- Pinned project dependency: `@gef-bootstrap/cli@1.1.2`, Node.js 22, npm lock committed; managed `.gef/init-state.json` and associated confirmed apply receipt committed after safe preview/apply. No secret/private GEF journal was committed.
- PR HEAD: CodeRabbit SUCCESS, zero unresolved review threads; SonarCloud Quality Gate SUCCESS (0 new issues), Socket x2 SUCCESS, NEX Governance Ubuntu/PowerShell x2 SUCCESS, GEF smoke Ubuntu/least-privileged Windows x2 SUCCESS.
- Post-merge `main` run #38135493350: NEX Governance / Source Pack SUCCESS and NEX Governance / PowerShell SUCCESS.
- Post-merge `main` run #38135493357: GEF smoke Ubuntu SUCCESS and GEF smoke Windows SUCCESS.
- Post-merge SonarCloud SUCCESS and Socket Security Project Report SUCCESS. CodeRabbit and Socket Pull Request Alerts are PR-specific, not claimed as post-merge `main` contexts.
- Verified GEF init applies to bootstrap integration only; **not** an installable Godot binary/game/engine release. Runtime performance claims are not measured.

## Limits retained
- `npm audit signatures` on a bundled GEF module earlier returned E404, so signature audit is INCONCLUSIVE. Source/tarball/npm lock provenance recorded in the execution Context Lock; `npm audit --audit-level=high` reported no high advisory in CI.
- GEF doctor security.dependency/security.github REVIEW and GEF checkpoint schema-compatibility caveats remain documented; they do not silently turn into PASS.
- Owner's ChatGPT-first repair policy NEX-ADR-0002 and review independence requirements remain in force.

## Next legal action / STOP
- Work Order #1 GEF is completed in Issues #1 and PR #74/#75. Governance authorization for M00 was promoted in PR #76 to `main` commit `10054a2d7038b2677bc00fa9279a754e08adc5fb` with six post-merge checks SUCCESS.
- **M00 #5 becomes ADMITTED only when its execution lock PR merges after required checks.** Before any code, fetch and attest the real new main SHA and promoted file fingerprints in Issue #5; obtain exclusive Steward lease and pass Codex LOCAL P0 preflight.
- M01/M02–M12 and NexLabs Flow remain PLANNING_ONLY. Do not claim an engine completion percentage or unlock GPU development from this document alone.

## M00 Owner authorization (2026-10-11)
Owner approved M00 in Issue #5, and the scope/version governance PR #76 merged into `main` `10054a2d7038b2677bc00fa9279a754e08adc5fb` after CodeRabbit and CI. This execution-lock promotion candidate records `10054a2d7038b2677bc00fa9279a754e08adc5fb` as the **authority source base**, not the unknown future squash SHA of this lock PR. Once merged, read back the new main SHA, verify all promoted contents and postmerge checks, and record an external Issue #5 attestation before starting Codex Desktop LOCAL. No native Godot build or runtime claim yet.

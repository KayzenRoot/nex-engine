# NEX-ADR-0002 · ChatGPT-first review/repair, Codex-only-when-needed
**Date of Owner directive:** 2026-10-10 America/Sao_Paulo.
**STATE:** OWNER_DIRECTED / ACCEPTED_ONLY_ON_EXACT_HEAD_GOVERNANCE_PROMOTION_MERGE.
**Applies to:** KayzenRoot/nex-engine, **all future reviews after Codex LOCAL implementation**, every admitted module M00–M12 and later WOs, CodeRabbit, GitHub CI and Bug Hunter feedback.

## Owner's decision (normalized)
When reviewing completed Codex work, **ChatGPT must first fix here every actionable, genuine pending task or error that can safely be completed with the accessible tools** (including Github patches/commits, unit test revisions, docs, scripts, lint and CI changes, narrow architectural contract corrections). **Hand off to Codex only what cannot actually be performed, safely authorized or adequately validated here**, with minimal exact task and evidence. Never send work to Codex merely for convenience if a safe and verifiable fix is available through ChatGPT/GitHub.

## Review-repair workflow
1. Read current governing Source Pack, exact PR/base/head SHA, contracts, Work Order scope/FILES_ALLOWED, GitHub review comments/threads, CodeRabbit status, security checks and all CI logs; label evidence from previous SHA as STALE.
2. Classify each finding: CONFIRMED; FALSE_POSITIVE with objective evidence; INCONCLUSIVE; OUT_OF_SCOPE; NEEDS_LOCAL. Prioritize SECURITY/HIGH/CRITICAL. Never infer a defect without checking code and reproducing when feasible.
3. For CONFIRMED issues that are **within available ChatGPT tools**, patch directly, ideally on the same admitted PR branch **only when the Codex executor is stopped, the Integration Steward grants exclusive lease, and the branch is current**. Otherwise create a separate exclusive repair branch/PR linked to same WO, or block until conflict resolved; no simultaneous edits to same path. Do not alter unapproved modules/core/contract files or promote checkpoints.
4. Add or amend regression tests and run whatever tests are actually available. If local build/Godot editor, native Windows/Docker GPU hardware or inaccessible environment is required, record this honestly and dispatch **only the irreducible local action** to Codex; keep independently verifiable GitHub fixes in ChatGPT's scope.
5. After any patch: rebind BASE/HEAD, request CodeRabbit/new GitHub checks, confirm exact final-HEAD check-runs; Bug Hunter and other independent reviewers validate the changes; ChatGPT audit must say `NOT_INDEPENDENT`. If any required check pending, unrun, failing or unknown → BLOCKED, not PASS.
6. For a finding not correctable here: write a **minimal Correction Delta** identifying exact PR, WO, latest HEAD, files allowed, reproduction, expected behavior, precise command/test to run locally, reason ChatGPT couldn't do it, and STOP condition. Do not assign unrelated work, and don't ask Codex to fix already corrected items.
7. Integration Steward serializes merges only after required approvals/gates and promotes checkpoint via separate accepted audit; no automatic rollback of user changes, bypass, force push, destructive cleanup, new paid/cloud services, secret exposure or real authentication without existing gates.

## Examples
- **ChatGPT repairs:** a typo/inconsistent source pack; invalid GitHub Actions YAML; a failing unit test that can be reproduced through available CI; an outdated dependency pin supported by source+package integrity; a CodeRabbit complaint about an exact diff; a broken README or CODEOWNERS policy. Update branch and recheck CI.
- **Codex repairs only when necessary:** reproduce a Vulkan/Direct3D crash on user's Windows GPU; edit/check files unavailable through GitHub; run native Godot 3D performance, Docker-heavy integration, Windows installer signing or local hardware profiling; work requiring an isolated Codex Desktop environment.
- **Owner/reviewer decision required:** changes of approved scope, budget/paid accounts, high-risk security recovery, governance promotion, ambiguous destructive init; neither ChatGPT nor Codex silently bypasses this.

## Relationship to existing decisions
- NEX-ADR-0001 and NEX-D-006 specifically authorize ChatGPT to implement the **first GEF bootstrap** only. This ADR independently governs **post-Codex review/repair for all modules**; it does **not** authorize unadmitted fresh engine feature development.
- Inherited GEF ADR-0008 remains upstream reference; an explicit bounded NEX owner directive controls this repository's review-repair actor.
- Independent Bug Hunter [#20](https://github.com/KayzenRoot/nex-engine/issues/20) remains read-only by default and is not replaced by self-audit.

## Acceptance and STOP conditions
`READY_FOR_FIX` requires permission, exclusive files/branch, current exact HEAD, within accepted WO, and test/evidence path. `CHATGPT_PATCHED_AWAIT_FINAL_HEAD_CHECKS` is not PASS. `NEEDS_CODEX_LOCAL` includes precise narrow task and proof of why execution here is unavailable. `STALE/BLOCKED` on drift, concurrent edits, missing gate, high-risk unresolved bug. `REVIEW_PASS` requires independent review, required CI complete on final HEAD and Steward/owner audit.

**Until this promotion PR is merged**, this text is a proposed accepted-on-merge owner policy, not evidence that any Codex task, GEF CLI, or game engine code has been executed.

# NEX Free Review migration (staging only)

Status: STAGED_NOT_ACTIVE. This branch does not replace live CodeRabbit ruleset until admin applies the matching policy.

## Goal
Zero paid API keys, zero AI-review quotas, low-latency deterministic gate:
- Semgrep Community Edition 1.180.0 with local security rules, no Semgrep login or registry call.
- Python compile checks and all existing 23+ CI policy tests.
- Existing SonarCloud, Socket x2, Governance Source Pack, Fast Lane checks remain required.
- Keep branch ruleset active, strict status checks, no bypass, squash-only, PR mandatory. No forced push.
- CodeRabbit becomes optional advisory, NOT a required gate, only AFTER new gate is exercised on an actual PR HEAD and admin policy is changed.

## Deployment order (Codex Desktop as KayzenRoot admin)
1. Confirm current main SHA, current protected ruleset #24864413, and staging branch only five new/modified files.
2. Create exactly one minimal integration PR from this staging branch (GitHub prohibits direct changes to protected main). DO NOT trigger native Godot source build; none of these file paths is under native-trigger globs.
3. First wait for NEX Free Review / Static to execute successfully. Fix only genuine test/scanner findings in isolated branch.
4. Using GH admin API, update LIVE ruleset required checks from CodeRabbit+Socket x2 to the six contexts in ops/github/nex-main-ruleset.json. Preserve pull_request/squash-only, strict, linear history, thread resolution, non-fast-forward and deletion bans, no bypass actors. Re-fetch and diff every ruleset field.
5. Let this ONE PR protected-squash merge with exact-head checks green; do not depend on CodeRabbit or human review. Re-fetch main and postmerge workflow results.
6. Enable GitHub CodeQL default setup for JavaScript and Python on public repo ONLY if eligible and no billing/secret surprises; validate before treating it as a required gate.
7. The already owner-authorized PR #88 originally required a *substantive CodeRabbit review*. Do not silently merge it under altered checks using that old authorization. Ask for a new explicit gate exception/owner authorization if CodeRabbit has not reviewed it. PR #84 also needs new head/base and owner approval after changed main.
8. Do not start/admit M01 or #19. Never claim Semgrep equals human/LLM semantic review.

## STOP
MIGRATED only once the new status check has executed on a real PR, live ruleset matches the checked-in canonical policy, protected merge succeeds, and exact-main postmerge checks complete SUCCESS. Any failed admin permission: report precise blocker and preserve original ruleset.

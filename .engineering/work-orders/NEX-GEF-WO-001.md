# Work Order NEX-GEF-WO-001 · GEF v1.1.2
**Status:** PLANNED / NOT_ADMITTED. Issue source: https://github.com/KayzenRoot/nex-engine/issues/1. Priority: NECESSARY. Risk: STANDARD.
**OBJECTIVE:** Install, initialize and prove `@gef-bootstrap/cli@1.1.2` in `KayzenRoot/nex-engine`, with reproducible local/CI use; nothing else.
**CONTEXT:** main before planning `181c4491d39531b657e0aee6df7909a3cbadc3bd`. Upstream v1.1.2 release source commit `af1fe9371a3883cbd8a4aafcbb405ddcd4c2ca82`. Following planning PR merge, reacquire exact HEAD and fingerprints; original SHA MUST NOT authorize implementation on stale branch.
**SCOPE:** inspect HEAD/sources/working tree; Node 22; pin CLI v1.1.2; run `gef --version`, `--help`, `init --target . --json` preview, `doctor --target . --json`, `status --target . --json`; review preview then apply `init --target . --apply --json` ONLY when authorized/safe; implement minimal reproducible project/CI pin + tests and evidence; PR.
**OUT OF SCOPE:** Godot fork/rendering/2D/3D/game, auth, paid services, VPS, modifications to GEF itself.
**FILES/SOURCES TO READ:** AGENTS.md; all .engineering canonical docs; upstream GEF `docs/INSTALLATION.md`, `docs/V1.1-OPERATIONS-RUNBOOK.md`, `packages/cli/README.md` from accepted release. Inspect actual future files after GEF init preview.
**REQUIREMENTS:** NEX-R-001..007; exact CLI version, no hidden global CI dependency, read-only preview, non-destructive apply, diagnostic evidence.
**ARCHITECTURE RULES:** tooling boundary only; do not vendor whole GEF; Codex-only source/test/CI implementation; preserve source pack, separate transaction artifacts/private journals.
**CONSTRAINTS:** no force push, bypass, overwrite unknown, secrets, external paid services. Fresh Context Lock on execution base; GEF init must be reviewed and recoverable.
**ACCEPTANCE CRITERIA:** pin/version correct, managed init valid, diagnostic outcomes interpreted, local+CI evidence exact HEAD, no unresolved HIGH/CRITICAL, proposed Checkpoint Delta.
**TESTS:** Node 22/npm, CLI version/help/init preview/doctor/status, negative collision checks, no private artifacts, CI smoke Windows/Linux as applicable.
**DELIVERABLES:** implementation branch+PR by Codex, Evidence Bundle with SHA/tests/CI/risks, proposed Checkpoint Delta, Portuguese review.
**REVIEW FORMAT:** APPROVED / CORRECTION REQUIRED / BLOCKED, state issue/PR/HEAD/checks and residual risks.
**STOP CONDITION:** NEX_GEF_WO_001_READY_FOR_EXACT_HEAD_AUDIT. No Codex self-merge/approval/checkpoint promotion.

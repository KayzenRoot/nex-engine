# Test and Benchmark Plan · Bootstrap
Status: CANONICAL_BOOTSTRAP_POLICY; GEF v1.1.2 verified in PR #74. Bounded M00 Godot native baseline implemented/verified via PR #78 and checkpoint promoted via PR #79 at 2090cb28df2385b995666c8fc4d3015e11f6c407. M01 NOT_ADMITTED.
The admitted executor must record actual Node 22/npm/Git versions, target/base HEAD, package integrity/source pin, `gef --version` (=1.1.2), `gef --help`, `gef init --target . --json` (read-only), `gef doctor --target . --json`, `gef status --target . --json`; `gef init --target . --apply --json` only after safe preview.
Require focused negative checks against overwrite/collision, no secrets/journals tracked, deterministic package pin and repeatability where supported.
CI should smoke-test the EXACT PR HEAD with a fresh checkout; prefer Ubuntu and Windows on Node.js 22 using free GitHub Actions and install without global hidden state.
Evidence: commands, exit codes, interpreted diagnostic findings, test counts, platform/CI job URLs, failure remediation, base/head SHAs and exact diff.
No performance/FPS benchmark is required until native graphics features are admitted.

M00 source-build/startup smokes are NOT M01 GPU/frame-time/FPS benchmarks; such performance work remains NOT_ADMITTED and requires a separate Owner-approved Work Order and Context Lock.

# Test and Benchmark Plan · Bootstrap
Status: CANONICAL_AFTER_GOVERNANCE_PR_MERGE (bootstrap policies only, GEF NOT_VERIFIED).
The admitted executor must record actual Node 22/npm/Git versions, target/base HEAD, package integrity/source pin, `gef --version` (=1.1.2), `gef --help`, `gef init --target . --json` (read-only), `gef doctor --target . --json`, `gef status --target . --json`; `gef init --target . --apply --json` only after safe preview.
Require focused negative checks against overwrite/collision, no secrets/journals tracked, deterministic package pin and repeatability where supported.
CI should smoke-test the EXACT PR HEAD with a fresh checkout; prefer Ubuntu and Windows on Node.js 22 using free GitHub Actions and install without global hidden state.
Evidence: commands, exit codes, interpreted diagnostic findings, test counts, platform/CI job URLs, failure remediation, base/head SHAs and exact diff.
No performance/FPS benchmark is required until native graphics features are admitted.

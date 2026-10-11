# Requirements · Bootstrap Phase
Status: CANONICAL_BOOTSTRAP_POLICY; GEF v1.1.2 post-merge verified in PR #74, effective in the new checkpoint only after promotion. No M00 implementation admitted.
- NEX-R-001: Pin production-accepted `@gef-bootstrap/cli@1.1.2`. Do not silently resolve to `latest`.
- NEX-R-002: Tooling executable in local Windows Node.js 22 development environment; CI must not depend on a developer's globally installed binary.
- NEX-R-003: Observe preview before `gef init --apply`; no collision with user files and no hidden destructive effects.
- NEX-R-004: Capture real `gef --version`, `--help`, `doctor`, `status`, init preview and apply results.
- NEX-R-005: Reproducible automated smoke tests and exact-head evidence in GitHub for changed integration surfaces. Do NOT merge the planning PR or promote Source Pack while any required final-HEAD review/check is pending, failed or unknown; recheck checks after every new commit.
- NEX-R-006: Preserve existing README and Source Pack; exclude secrets, node_modules and private GEF transaction journals from Git. Before planning promotion require completion of all applicable checks and a recorded exact-head Source Pack audit; no bypass, self-approval or implied admission from a green status alone.
- NEX-R-007: Deliver isolated implementation PR, base/head SHAs, tests, risk and proposed Checkpoint Delta for objective audit. Its own promotion/merge requires separate exact-head checks and owner audit; ADR NEX-ADR-0001 and NEX-D-006 must be promoted together before admitting ChatGPT as bootstrap executor, followed by refreshed execution Context Lock.
No visual fidelity, Godot, game, multiplayer or GPU feature is required in this increment.

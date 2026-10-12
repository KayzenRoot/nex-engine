# Requirements · Bootstrap Phase
Status: CANONICAL_BOOTSTRAP_POLICY; GEF v1.1.2 verified in PR #74. Bounded M00 Godot native baseline implemented/verified via PR #78 and checkpoint promoted via PR #79 at 2090cb28df2385b995666c8fc4d3015e11f6c407. M01 NOT_ADMITTED.
- NEX-R-001: Pin production-accepted `@gef-bootstrap/cli@1.1.2`. Do not silently resolve to `latest`.
- NEX-R-002: Tooling executable in local Windows Node.js 22 development environment; CI must not depend on a developer's globally installed binary.
- NEX-R-003: Observe preview before `gef init --apply`; no collision with user files and no hidden destructive effects.
- NEX-R-004: Capture real `gef --version`, `--help`, `doctor`, `status`, init preview and apply results.
- NEX-R-005: Reproducible automated smoke tests and exact-head evidence in GitHub for changed integration surfaces. Do NOT merge the planning PR or promote Source Pack while any required final-HEAD review/check is pending, failed or unknown; recheck checks after every new commit.
- NEX-R-006: Preserve existing README and Source Pack; exclude secrets, node_modules and private GEF transaction journals from Git. Before planning promotion require completion of all applicable checks and a recorded exact-head Source Pack audit; no bypass, self-approval or implied admission from a green status alone.
- NEX-R-007: Deliver isolated implementation PR, base/head SHAs, tests, risk and proposed Checkpoint Delta for objective audit. Its own promotion/merge requires separate exact-head checks and owner audit; ADR NEX-ADR-0001 and NEX-D-006 must be promoted together before admitting ChatGPT as bootstrap executor, followed by refreshed execution Context Lock.
No visual fidelity, Godot, game, multiplayer or GPU feature is required in this increment.

## M00-only requirements (historical approved/verified scope after promoted lock)
- NEX-M00-R-001: verify official Godot release tag, commit SHA, downloaded SHA256, license and notices; no floating latest.
- NEX-M00-R-002: prove editor/runtime startup and minimal project import under native Windows; Linux headless CI proves portability but does not measure GPU.
- NEX-M00-R-003: pin exact toolchain versions, include build time/resource log and license/provenance manifest; implement without engine core modifications.
- NEX-M00-R-004: isolated worktree/branch and single-writer ownership, no overlapping files or GPU benchmarks in parallel.
- NEX-M00-R-005: verifiable PR exact-head CI/CodeRabbit/Socket/Sonar, independent review, evidence and proposed checkpoint only.

The M00 requirements were verified with bounded evidence in `.engineering/evidence/NEX-M00-WO-001-POSTMERGE-EVIDENCE.md`; verification does not admit M01 or engine-core enhancements.

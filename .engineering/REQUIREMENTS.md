# Requirements · Bootstrap Phase
Status: DRAFT; all listed requirements apply ONLY to NEX-GEF-WO-001.
- NEX-R-001: Pin production-accepted `@gef-bootstrap/cli@1.1.2`. Do not silently resolve to `latest`.
- NEX-R-002: Tooling executable in local Windows Node.js 22 development environment; CI must not depend on a developer's globally installed binary.
- NEX-R-003: Observe preview before `gef init --apply`; no collision with user files and no hidden destructive effects.
- NEX-R-004: Capture real `gef --version`, `--help`, `doctor`, `status`, init preview and apply results.
- NEX-R-005: Reproducible automated smoke tests and exact-head evidence in GitHub for changed integration surfaces.
- NEX-R-006: Preserve existing README and source pack; exclude secrets, node_modules and private GEF transaction journals from Git.
- NEX-R-007: Deliver isolated implementation PR, base/head SHAs, tests, risk and proposed checkpoint delta for objective audit.
No visual fidelity, Godot, game, multiplayer or GPU feature is required in this increment.

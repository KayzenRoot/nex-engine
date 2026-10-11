# Architecture · Bootstrap Boundary
Status: CANONICAL_BOOTSTRAP_POLICY; GEF v1.1.2 post-merge verified in PR #74, effective in the new checkpoint only after promotion. No M00 implementation admitted.
Project repository: `KayzenRoot/nex-engine`, native-PC direction.
GEF distribution: published npm package `@gef-bootstrap/cli@1.1.2` (immutable version) executed with Node.js 22. Do not vendor/copy all of `KayzenRoot/gef-bootstrap` into this project and do not treat upstream source workspace as a git submodule unless a future ADR justifies it.
Repository-managed deterministic install and scripts must not assume a global CLI; The admitted executor determines minimal implementation from actual GEF CLI and source state. Project-owned managed GEF files follow observed init preview.
Governance: Source Pack -> admitted Work Order + Context Lock -> admitted executor preflight/implementation -> GitHub PR/CI -> exact-head audit -> checkpoint.
The future Godot fork, rendering backend, API and game runtime are NOT_YET_DESIGNED.

Actor exception: NEX-ADR-0001 permits ChatGPT to implement only the initial GEF bootstrap. From the next engine-feature Work Order onward, the Codex-as-executor default is restored unless the owner explicitly changes it again.

## M00 boundary (owner-approved governance phase)
Godot native desktop baseline uses upstream tagged release in an isolated toolchain area, with official archive/checksum and source SHA. Prefer upstream editor/project smoke and documented SCons toolchain; do not fork or patch engine core unless a later accepted ADR proves it necessary. This Source Pack amendment does not start implementation. See `.engineering/decisions/NEX-ADR-0003-M00-GODOT-BASELINE.md`.

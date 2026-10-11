# Architecture · Bootstrap Boundary
Status: DRAFT. This document intentionally specifies **tooling**, not the future engine renderer.
Project repository: `KayzenRoot/nex-engine`, native-PC direction.
GEF distribution: published npm package `@gef-bootstrap/cli@1.1.2` (immutable version) executed with Node.js 22. Do not vendor/copy all of `KayzenRoot/gef-bootstrap` into this project and do not treat upstream source workspace as a git submodule unless a future ADR justifies it.
Repository-managed deterministic install and scripts must not assume a global CLI; Codex determines minimal implementation from actual GEF CLI and source state. Project-owned managed GEF files follow observed init preview.
Governance: Source Pack -> admitted Work Order + Context Lock -> Codex local preflight/implementation -> GitHub PR/CI -> exact-head audit -> checkpoint.
The future Godot fork, rendering backend, API and game runtime are NOT_YET_DESIGNED.

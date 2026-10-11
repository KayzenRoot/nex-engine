# NEX-ADR-0003 | Godot native baseline for M00
**Status:** PROPOSED; accepted only if this governance PR merges. **Owner approval:** Issue #5, 2026-10-11. **Decision type:** bounded version & native build architecture, not engine-feature coding.
## Decision
Use official `godotengine/godot` tag `4.7.2-stable` for the M00 baseline, pinned to commit `ed1daf0bf001b61586d9930840f2f1394092c079` (verified official tag API). Source archive `godot-4.7.2-stable.tar.xz` published GitHub asset digest: `sha256:a18ce0ccec3ecc40b0dd6c4f5132ca934e9fb7c2979717940ff32aee1eb35481`; downloader must independently verify bytes and never continue on mismatch. The official release was published 2026-08-18 (GitHub release metadata). Verify MIT and bundled third-party notices before redistribution.
## Architecture
M00 = native editor/runtime and build toolchain validation, not a new renderer. Windows is the operator target, Ubuntu CI headless smoke. Prefer unmodified official source and binaries; local patching Godot core/GDExtension or third-party modules is **forbidden** in this WO. godot-cpp ABI is **NOT PINNED / NOT REQUIRED** unless a later separately admitted decision demonstrates need. No wholesale vendoring of upstream Godot source into `nex-engine`; keep archives and generated binaries outside Git, publish small metadata and checksums only.
## Evidence gates
Validate Node22/GEF 1.1.2 bootstrap state, Python/SCons/toolchain availability, storage/memory estimate and offline/permission boundaries. Windows build and editor/version/minimal import smoke with exit codes, Linux headless smoke; no fabricated GPU FPS or quality gains. If Windows native source build exceeds budget or lacks compiler, document limitation and use verified official binary as *interim diagnostic*, not a false source build PASS.
## Alternatives and reversibility
A later patched stable tag needs explicit ADR revision and refreshed Context Lock before execution. Falling back to unpinned `latest`, a 4.8 development pre-release, or changing core to satisfy build is not allowed. Do not activate M01 or other modules through this ADR.
## STOP
Until the governance PR and a separate fresh execution Context Lock are promoted: `M00_OWNER_APPROVED_GOVERNANCE_PENDING`, no Codex implementation. Retain all gates of NEX-ADR-0002 and GitHub Ruleset.

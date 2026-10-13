# NEX-M01-S04-GPU-PROFILE-DELTA-001 | Admission evidence snapshot
The owner approved this single bounded GPU profiling scope in chat on 2026-10-12; it was recorded for audit at https://github.com/KayzenRoot/nex-engine/issues/24#issuecomment-6136220475 . Approval does not authorize a merge or completion of the M01 parent issue.

Protected source base before Stage A: `d4a6db4d9e32cfb89a088675eadbfa9f755a62d0`, Git tree `43c51e175e651cb00f347cf4577b8db64a5f3dea`; no open PRs at the time of this lock preparation. PR #105 is already owner-authorized protected-squash merged; its post-merge exact tree equality, **12/12 main checks and 6/6 workflow SUCCESS**, Godot Windows/Linux native and 115 tests are attested at https://github.com/KayzenRoot/nex-engine/pull/105#issuecomment-6135734376 . The visual GPU evidence captures main-loop F10 samples, **not** independently measured render GPU frametime.

Frozen source provenance: 28 Git SHA-1 blob fingerprints were fetched from the exact base `d4a6db4d9e32cfb89a088675eadbfa9f755a62d0`, including M01 contracts, renderer launcher, Godot smoke, existing F10 validator, accepted source hierarchy/checkpoint and workflow definitions. Every pin is reproduced in `.engineering/context-locks/NEX-M01-S04-GPU-PROFILE-DELTA-001-EXECUTION.json`. Any pin drift before execution = STALE, require new locked authority. Canonical `.engineering/CHECKPOINT.*` not edited by Stage A.

Official Godot RenderingServer docs support per-viewport CPU/GPU rendering time with explicit measurement activation. GPU reports can be unavailable in headless; tests must not fake them. See https://docs.godotengine.org/en/stable/classes/class_renderingserver.html . Separate Device/VRAM telemetry requires correctly labeled source.

Quality note: SonarCloud Quality Gate from #105 was SUCCESS but three new issues remained of unknown severity; issue details were not accessible to the GitHub connector. Do not infer they are low-severity; triage before final high-risk claim.

**Do not execute product code until this lock is protected merged, the actual fresh main SHA recorded in #24 and the exclusive Codex/Steward lease established.**
STOP: `S04_GPU_PROFILE_LOCK_PROPOSED_WAIT_OWNER_MERGE`.

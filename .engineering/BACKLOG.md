# Backlog · NEX Engine

## Current verified implementation queue | Stage B

- **COMPLETED, LIMITED:** contracts #19, PR #93; S02 synthetic FramePulse #22, PR #95. No hardware measurement, engine product completion, new native build or wider M01 admission claimed.
- **NEXT:** Stage B checkpoint promotion after six free gates, substantive exact-HEAD audit and separate Owner squash authorization. Only after this, independently admit next NECESSARY WOs. Multiagent W0 #4 was planning-only, NOT a work-code dispatch.
- **QA finding #20:** required GitHub CI does not explicitly run `tests/contracts`/`tests/telemetry`; a future separate single-writer workflow WO is needed.
- **NOT_ADMITTED:** M01 parent #6, S01 #21, M12 and other modules. Older backlog entries below are historical status text; preserved for traceability.

Status: M00_NATIVE_GODOT_BASELINE_VERIFIED_AFTER_CHECKPOINT_PROMOTION; no engine completion denominator or overall release percentage exists.
- NEX-GEF-WO-001 (#1) · NECESSARY / IMPLEMENTED + EXACT-HEAD/POST-MERGE CI VERIFIED: GEF Bootstrap v1.1.2; checkpoint promotion is separate and effective only after its own PR merges. See PR #74 and main commit `570d0671ed57f5cd29932baf0bac26345efca279`.
- NEX-M00-WO-001 (#5) · VERIFIED_BASELINE / IMPLEMENTATION PR #78 SQUASH MERGED to `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861` with exact Git-tree match, Windows source build, Ubuntu CI and 6/6 main checks verified; checkpoint PR #79 was reviewed and protected-squash promoted as `2090cb28df2385b995666c8fc4d3015e11f6c407`, with 6/6 postmerge checks SUCCESS. No engine release claimed.
- NEX-M01-WO-001 (#6) · NECESSARY AFTER M00 / NOT_ADMITTED: measured reference scenes, frame-time and visual baseline.
- Render3D, lighting/GI, PBR, GPU VFX, LOD/performance, 2D, 2.5D, editor, animation, asset import, branding, flow technologies M02–M12 · IMPORTANT/FUTURE / NOT_ADMITTED, dependent on validated baselines and contracts.
- Game development and networked multiplayer · FUTURE / NOT_ADMITTED.
Release percentage: NOT_BASELINED until a canonical engine-specific DoD denominator is frozen and validated. GEF bootstrap passing does NOT mean the engine is 100% built.

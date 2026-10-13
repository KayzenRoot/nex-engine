# NEX-M01-S04-GPU-PROFILE-DELTA-001 | Owner-approved GPU Render-Time Profiler | Stage A immutable execution gate
Status: **OWNER_SCOPE_APPROVED / CONTEXT_LOCK_PROPOSED / NOT_EXECUTABLE_UNTIL_PROTECTED_PROMOTION**.
Owner approval: https://github.com/KayzenRoot/nex-engine/issues/24#issuecomment-6136220475
Parent scope: https://github.com/KayzenRoot/nex-engine/issues/6#issuecomment-6135856364
Risk: STANDARD. Priority: NECESSARY. Implementation owner: Codex Desktop LOCAL; reviewer/repair: ChatGPT first when safe; integration: single-writer Steward.
Frozen Stage A source: main `d4a6db4d9e32cfb89a088675eadbfa9f755a62d0`, tree `43c51e175e651cb00f347cf4577b8db64a5f3dea`, 28 actual Git blob fingerprints pinned in `.engineering/context-locks/NEX-M01-S04-GPU-PROFILE-DELTA-001-EXECUTION.json`. This is historical source authority, NOT a predicted future post-promotion main SHA.

## Exact Stage A scope (THIS PR ONLY)
Add only these four proposal files:
- `.engineering/work-orders/NEX-M01-S04-GPU-PROFILE-DELTA-001.md`
- `.engineering/context-locks/NEX-M01-S04-GPU-PROFILE-DELTA-001-EXECUTION.json`
- `.engineering/evidence/NEX-M01-S04-GPU-PROFILE-DELTA-001-ADMISSION-EVIDENCE.md`
- `.engineering/checkpoint-deltas/NEX-M01-S04-GPU-PROFILE-DELTA-001-PROPOSED.md`

No product code or CI changes here. Do not merge automatically. A separate explicit Owner exact-HEAD protected squash approval and main post-merge audit are necessary to activate the execution lock. Main baseline and existing checkpoints remain untouched.

## Stage B implementation, ONLY after protected lock promotion and current main rebind
One Codex Desktop LOCAL executor/worktree, GPU serial, owner-approved implementation only. **Write allowlist**: `nex_bench/hub.gd`, `nex_bench/smoke.gd`, `nex_bench/README.md`, `nex_bench/gpu_profile/**`, `tests/ci/test_gpu_profile_*.py`. Other paths read-only. Build a real Godot viewport profiler using `RenderingServer.viewport_set_measure_render_time(rid, true)` + `viewport_get_measured_render_time_gpu(rid)` and `viewport_get_measured_render_time_cpu(rid)` (ms) on the actual game viewport RID; gracefully disable when unsupported/unavailable. Source docs https://docs.godotengine.org/en/stable/classes/class_renderingserver.html .

Maintain `nex_frame_observation.v1` unchanged and all historic raw F10 captures. New profiler schema v1: discrete `GPU_RENDER_MS`, `CPU_RENDER_MS`, `MAIN_LOOP_INTERVAL_MS`, `RENDERER_ALLOCATION_BYTES` and independently sourced `DEVICE_SNAPSHOT` labels, with `MEASURED` / `UNAVAILABLE`; no zero as substitute for unavailable value. Run bounded warmups + per-scenario actual capture, raw series + finite aggregate p50/p95/p99, explicit 1% low FPS (1000 / average of slowest ceil(.01*n) main-loop intervals), no fake frametime or unthrottled FPS conclusions. Freeze unit, renderer, viewport, workload, driver, VSync, timestamp and code HEAD for each run. Measure 25/100/200 geometry + one representative combined case, 3 runs per case at 30 seconds each after 2-second warmup if safely supported. Keep a human stop/cancel control and memory/heat safeguards. No secret, network or dependency.

## Proof and Definition of Done
Real Godot 4.7.2 Windows RTX 5050 GUI run and native Windows/Linux Godot smoke; GPU measurement must be >0 and documented when available, otherwise `BLOCKED/UNAVAILABLE`. Python stdlib independently recalculates exact JSON series, rejects nonfinite/incorrect metrics/duplicates and does not mutate files. Hardware log includes NVIDIA driver, capture mode, VRAM source (Godot allocation != total device VRAM; nvidia-smi may describe whole-device WDDM), resolution, frame pacing and explicitly reports uncertainty. **Repetability**: runs 3x serial, capture variability/quality caveats, no invented 1% lows or benchmark claims. Negative tests for unsupported headless, invalid metrics and cancellation. Existing 72 CI+12 contracts+31 telemetry (115) must remain passing plus new tests and six ruleset-required checks. SonarCloud's three pre-existing unclassified issues require real rule/severity/path triage, not suppression or ungrounded claims.

**Out of scope:** Godot core, GDExtension, GEF, renderer rewrite, gameplay, PR merge or Checkpoint promotion, package/release, paid services, unapproved governance writes, parallel GPU runs, broad M01 completion.

**Stage B STOP:** `GPU_PROFILER_REAL_WINDOWS_EVIDENCE_READY_EXACT_HEAD_REVIEW_NO_MERGE`; Stage A STOP: `GPU_PROFILE_STAGE_A_CONTEXT_LOCK_WAIT_OWNER_SQUASH`.

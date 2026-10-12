# NEX Engine | Density Ladder M01/S04

A **standalone Godot 4.7.2 Forward+ live workload demo**, independent of unmerged S01 scenes or S03 image tooling. Uses only original built-in meshes, Godot OmniLight3D and GPUParticles3D. No dependencies, asset licenses, engine fork, or shared CI changes.

## Run

Open `nex_bench/stress/project.godot` in Godot 4.7.2 stable, then run the project. Use **1/2/3/4** to select 25/50/100/200 geometry proxies. Use **G** for geometry only, **L** for geometry + six local lights, **V** for geometry + four GPU particle emitters, **C** for combined load. HUD reports the selected workload and **observed instantaneous FPS**, not scientifically instrumented frame pacing, GPU load or a performance target. Scene generation and positions are deterministic.

The configuration in `config/ladder.v1.json` fail-closes on unsupported count sets or caps. At sustained FPS under 12 for five seconds, higher load automatically falls back to 25 geometry proxies. This does not prevent all GPU driver failures or OOM. Stop manually on resource pressure or instability.

## Evidence protocol for a real benchmark (future, **not performed**)

Only run controlled native Windows tests with exclusive GPU access after a true S01 scene smoke and stable toolchain verification. Record actual Godot version, renderer/backend/driver, CPU/GPU/VRAM, resolution, VSync, frame cap, cold/warm state and samples. Repeat A/B/A with 25, 50, 100, 200 proxies (as safe), isolate geometry/lights/VFX/combined, and use FramePulse (#22) to compute p50/p95/p99 and 1%-low. Live HUD FPS is **not** a valid baseline measurement or evidence of quality improvement. Synthetic proxy counts do not model real NPC AI/pathfinding, combat or PoE2 assets.

The Python regression test in `tests/ci/test_density_ladder.py` checks configuration, bound/cap logic and scene wiring in the required CI. Those tests are static and do **not** run a native Godot renderer. Real GUI smoke still required before runtime acceptance.

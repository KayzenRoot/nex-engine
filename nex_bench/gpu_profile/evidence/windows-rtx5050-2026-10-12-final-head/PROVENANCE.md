# Evidence provenance

Work Order: `NEX-M01-S04-GPU-PROFILE-DELTA-001` (Issue #24, Stage B)

## Source and governance

- Repository: `KayzenRoot/nex-engine`
- Reserved branch: `feat/nex-m01-s04-gpu-profile-delta-001`
- Verified base: `226b015ed34d8e4452819da45f92d8936796b3b0`
- Implementation source commit: `a1b1e1df89a52d219d7d5f328f011d2c6f3c657a`
- Implementation source tree: `48b9fa55b166d3615da080fa9bb20a726e86247a`
- Measurements were collected from that committed source. Evidence and report files were added afterward and do not change the measured source SHA.
- Promoted Context Lock was validated against its historical base with 28/28 pinned fingerprints; Stage B allowlist was honored. The lock was not recreated and canonical checkpoint/main were not modified.
- Exclusive writer and RTX 5050 leases were recorded in Issue #24 comment `6136594074` and held during implementation and serial measurements.

## Local environment

- OS: Microsoft Windows 11 Pro, build 26300.
- GPU: NVIDIA GeForce RTX 5050; driver `617.14`.
- Renderer: Godot `Forward+` over Vulkan; display: Windows.
- Godot: `4.7.2.stable.official.ed1daf0bf`.
- Godot executable SHA256: `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424`.
- Python test runner: Node-independent standard-library `unittest`; exact commands and outputs are in the adjacent `.log` files.
- `Godot-GUI.log` records the Godot version and Vulkan adapter. The F9 HUD screenshot records the live scene diagnostics and profiler status.

## Measurements

- Twelve required local runs: three each at 25 geometry, 100 geometry, 200 geometry, and 25 combined.
- Every run is `COMPLETE`, uses 2 seconds of warmup and at least 30 seconds of observation, and contains 2,251 valid GPU and CPU render samples.
- Each raw JSON passed `nex_bench/gpu_profile/validate_gpu_profile.py`; its validator output is adjacent as `.validation.json`.
- All runs used VSync mode 1. The observed 75 FPS is VSync-limited and is not an uncapped benchmark or a performance claim.
- F9 screenshot observation: 75 FPS; CPU process display 13.47 ms/frame (explicitly not GPU time); 32 draw calls; 794 3D objects; renderer allocation 88.1 MiB. The renderer allocation is not total VRAM.
- The separate `GPU-DEVICE-SNAPSHOT.txt` is a device-wide NVIDIA/WDDM snapshot taken after the matrix. Its utilization and memory values are not attributed to the Godot process.
- `RUN-SUMMARY.md` includes per-run percentiles and descriptive spread. No comparison against another device/configuration is claimed.

## Validation

- Python CI suite: 89 tests passed.
- Contract suite: 12 tests passed.
- Telemetry suite: 31 tests passed.
- Pinned native Godot smoke: passed, including GPU profiler wiring, cancellation, headless-safe `UNAVAILABLE`, existing F10 behavior, and visual truth/heatmap markers.
- `Start-NEX.cmd` launched the GUI. The Density Ladder and F9 were inspected locally; the final PNG contains the profile HUD and F9 data without an absolute user path.
- A strict secret-pattern scan of changed implementation and test files returned no matches. Evidence files were also checked for the local Windows username and absolute user paths before packaging.
- Three older PR #105 SonarCloud findings were triaged in `SONARCLOUD-LEGACY-TRIAGE.md`. They are open `CODE_SMELL` maintainability findings in files outside the Stage B allowlist; this is not a repository-wide security assessment.

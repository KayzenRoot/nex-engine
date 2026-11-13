# Evidence provenance — NEX-M01-S04-GPU-PROFILE-DELTA-001

## Governed source

- Work Order: Issue #24, execution handoff comment #6136323822.
- Stale-ref correction: Issue #24, Correction Delta comment #6136463418. Local remote-tracking refs were synchronized; current origin/main and feature-branch remote ref both resolve to 226b015ed34d8e4452819da45f92d8936796b3b0. The protected main was not edited.
- Promoted Context Lock: Stage A PR #106 merged at base 226b015ed34d8e4452819da45f92d8936796b3b0; post-merge attestation is Issue #24 comment #6136306783. The historical 28 fingerprint pins were validated against their locked historical base; no replacement lock was created.
- Exclusive writer and RTX 5050 lease: Issue #24 comment #6136594074. The local mutex owner remained PID 25936 through the capture and evidence preparation. Release is recorded separately at closeout.
- Branch: feat/nex-m01-s04-gpu-profile-delta-001.
- Verified PR base: 226b015ed34d8e4452819da45f92d8936796b3b0.
- Source code commit measured by all 12 GPU profiles: 3892fbecdff79a17ecd7b76ada993d9e5e34eba5.
- Source code Git tree: 41f8904277bd653a6538a7f5cb7afd130debb316.
- PR: #107, open and non-draft at the time of capture. The final evidence-only commit advances the PR HEAD; the exact final PR SHA and tree are reported in the PR and Issue #24 closeout.
- No merge, main change, checkpoint promotion, or M01 advancement occurred.

## Local toolchain and host

- Windows Management Instrumentation reports Microsoft Windows 11 Pro, version 10.0.26300, 64-bit. The CurrentVersion registry ProductName string still says Windows 10 Pro, DisplayVersion 26H2, build 26300; this is retained as a host metadata discrepancy rather than silently normalized.
- GPU: NVIDIA GeForce RTX 5050; driver 617.14.
- Godot executable: 4.7.2.stable.official.ed1daf0bf, upstream commit ed1daf0bf001b61586d9930840f2f1394092c079.
- Godot executable SHA-256: AB1824F85BFD8E0E4128182C000C4003A3E042245B2967848D089B2A04B22424.
- Runtime renderer: Windows, Forward+, Vulkan.
- Python: 3.13.15, using the standard library for the test suites and validator. No package was installed.
- Native launch smoke is logged in Start-NEX-GUI-launch.log. It records the exact Godot version and successful F9, camera, F10, GPU profiler, heatmap, visual truth, and import smoke markers, followed by GUI launch.
- The actual GUI profile is logged in Godot-GUI.log. The RTX 5050 adapter and Vulkan/Forward+ were observed by Godot.

## Measurement protocol and outputs

- Twelve serial runs were captured on one GPU: 3 each of 25, 100, and 200 geometry proxies, and 3 of 25 proxies with combined effects.
- Each run used 2 seconds of discarded warmup and at least 30 seconds of observation. Each JSON records source SHA 3892fbecdff79a17ecd7b76ada993d9e5e34eba5, COMPLETE status, UTC timestamp, workload, VSync, renderer, device snapshot, GPU/CPU sample series, aggregates, and limitations.
- All 12 raw JSON profiles independently passed nex_bench/gpu_profile/validate_gpu_profile.py with exit code 0. Adjacent validation JSON files preserve each result.
- MEASUREMENTS.md contains one row per run calculated from the raw profiles.
- GPU-PROFILER-F9.png captures the Density Ladder, completed GPU profiler HUD, and local diagnostics panel. In that saved frame: 75 observed FPS (not a benchmark), 15.73 ms/frame CPU process time (not GPU time), 32 draw calls, 794 3D objects, and 88.1 MiB renderer allocation.
- Device-wide nvidia-smi snapshots before and after are provided. Under WDDM they are not process-attributed. Renderer allocation is not total VRAM.
- The run configuration had max_fps=0 and VSync mode 1. The observed display rate was around 72–75 FPS and is VSync-limited; no maximum-performance claim is made.
- The exported profile's viewport render timing is not an input-to-photon measurement and is not assumed to align one-to-one with the current process frame.

## Checks

- Python standard-library suites on source commit 3892fbecdff79a17ecd7b76ada993d9e5e34eba5: 92 CI tests, 12 contract tests, and 31 telemetry tests passed; each exit code was 0. See LOCAL-VALIDATION.log.
- Pinned Godot Windows headless smoke on source commit 3892fbecdff79a17ecd7b76ada993d9e5e34eba5 passed with exit code 0. See LOCAL-VALIDATION.log.
- PR checks on source commit 3892fbecdff79a17ecd7b76ada993d9e5e34eba5 were green, including SonarCloud Quality Gate (0 new issues and 0 Security Hotspots). A fresh provider check result for the final evidence-only HEAD is required and will be recorded in the GitHub closeout.
- CodeRabbit showed a pass status with the message that automatic reviews are disabled; this is not an independent code review.
- The three pre-existing PR #105 SonarCloud records are separately classified in SONARCLOUD-LEGACY-TRIAGE.md. They are CODE_SMELL findings outside this Work Order's allowlist; no security finding was inferred from them.

## Evidence files

- MEASUREMENTS.md and 12 raw gpu_profile_*.json files plus 12 adjacent *.validation.json results.
- GPU-PROFILER-F9.png, Godot-GUI.log, Start-NEX-GUI-launch.log.
- GPU-DEVICE-SNAPSHOT-PRE.txt and GPU-DEVICE-SNAPSHOT-POST.txt.
- LOCAL-VALIDATION.log and SONARCLOUD-LEGACY-TRIAGE.md.
- A local .gitattributes entry disables line-ending conversion for this evidence directory so recorded SHA-256 values remain stable on Windows checkouts.
- SHA256SUMS.txt hashes every evidence file except itself.

# NEX Visual Lab — Windows 11 local GPU validation (PR #105)

## Exact source tested

- Repository: `KayzenRoot/nex-engine`; PR #105.
- Protected base: `a71df4c141ac52cc59778dc0f08831458d62ef33`.
- Application source HEAD tested: `f5e25180c91893e93c7f466e9f936b70c8e8662d`.
- Source tree tested: `ab61bbb1952ba9b448fe4279de335c213cc2338d`.
- The validation bundle is an evidence-only follow-up on the same PR branch. No application-code defect was found, so no product code was changed.

## Pinned Godot and launcher

- Toolchain lock: `.nex/toolchain/NEX-M00-WO-001-toolchain-lock.json`, Godot `4.7.2-stable`, upstream commit `ed1daf0bf001b61586d9930840f2f1394092c079`.
- Official Windows archive SHA-256 from the lock, verified before extraction: `731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953`.
- Executable reported `4.7.2.stable.official.ed1daf0bf`; executable SHA-256: `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424`.
- Executed `nex_bench\Start-NEX.cmd -GodotPath "%LOCALAPPDATA%\NEX\Godot-4.7.2-pr105-visual-lab\Godot_v4.7.2-stable_win64.exe"`.
- Exit code `0`; native import smoke passed; the script opened the GUI process (PID recorded in `Start-NEX.log`). The window title was `NEX Engine | Unified Visual Lab (DEBUG)`.
- Smoke log: F9 diagnostics, native visual truth, heatmap red-pixel/preview, and four-mode import checks all reported `PASS`. The Godot GUI log reports `Vulkan 1.4.351 - Forward+ - Using Device #0: NVIDIA - NVIDIA GeForce RTX 5050`; no GUI error or warning was logged.

## Observed machine and GPU

- OS: Windows 11 Pro, build `26300`.
- Display adapter: NVIDIA GeForce RTX 5050; Windows driver `32.0.16.1714`; `nvidia-smi` driver `617.14`.
- Post-test `nvidia-smi` sample: 8151 MiB total, 1789 MiB used, 7% GPU utilization, 47 C.
- Godot F9 reported display `Windows`, adapter `NVIDIA GeForce RTX 5050`, rendering method `forward_plus`, driver `vulkan`.
- Full sample is in `GPU-Config.txt`; these are observed local values, not estimates.

## GUI and F9 observations

| Scene/load | FPS observed | CPU process ms/frame | Draw calls | 3D objects | Renderer allocation |
| --- | ---: | ---: | ---: | ---: | ---: |
| F1 Corridor | 75 | 16.20 | 45 | 564 | 87.5 MiB |
| F2 Arena | 75 | 13.37 | 46 | 591 | 87.5 MiB |
| F3 Dense City | 75 | 13.55 | 39 | 552 | 87.5 MiB |
| F4 Density, 25 proxies | 75 | 13.49 | 24 | 698 | 87.4 MiB |
| F4 Density, 50 proxies | 75 | 13.40 | 24 | 723 | 87.4 MiB |
| F4 Density, 100 proxies | 75 | 13.36 | 25 | 774 | 87.4 MiB |
| F4 Density, 200 proxies after 6 seconds | 75 | 13.36 | 26 | 874 | 89.4 MiB |
| F1 comparison preview | 72 | 13.42 | 50 | 598 | 93.2 MiB |

The safety config caps the ladder at 200 proxies, six lights, and four particle emitters, and falls back if observed FPS remains below 12 for five seconds. The 200-proxy geometry load stayed at 75 FPS after six seconds; no fallback was triggered. The point-in-time samples are **not** a benchmark or p95/p99 result. F9 CPU process is not GPU time; renderer allocation is not total VRAM.

## B/N/D visual truth

- Captured baseline `B-Corridor.png` and candidate `N-Corridor.png` at the same F1 scene and window settings. Both PNGs are 1280×720 and have the same SHA-256, so this unchanged-scene comparison is an expected zero-difference case.
- Pressed `D`: the GUI reported `0.000% changed (> 2/255)`, `MAE 0.000000`, `PASS`, and `heatmap saved`; the heatmap preview opened and the exported `D-Heatmap.png` exists.
- The launcher smoke separately exercises a red-pixel difference and preview path (`NEX_NATIVE_VISUAL_HEATMAP_PASS`), so the exported black heatmap here is the correct output for identical captures, not a claim that a changed-pixel case was produced by this GUI run.

## Captures and logs

- [F1 and F9 adapter/renderer panel](F1-F9.jpg)
- [F2 Arena](F2-Arena.jpg)
- [F3 Dense City](F3-Dense-City.jpg)
- [F4 at 25](F4-Density-25.jpg), [50](F4-Density-50.jpg), [100](F4-Density-100.jpg), and [200 after six seconds](F4-200-after-6s.jpg)
- [B baseline](B-Corridor.png), [N candidate](N-Corridor.png), [exported D heatmap](D-Heatmap.png), and [comparison/preview screen](BND-Heatmap-Preview.jpg)
- `Start-NEX.log`, `Godot-Native-Smoke.log`, `Godot-GUI.log`, and `GPU-Config.txt` preserve the run evidence.

## Scope and result

No code correction was needed. No additional issue or PR was created. This evidence is committed to the existing PR #105 branch; protected `main` was not modified or merged, and no ruleset, checkpoint, workflow, or GitHub permission was changed. PR #105 remains open for its existing review flow. Measurements describe this local session only.

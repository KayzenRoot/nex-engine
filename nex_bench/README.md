# NEX Engine | Unified Native Visual Lab

**One Godot desktop project** combining the three existing product implementations, without copying or weakening their original independent demos:

- **F1 Corridor**, **F2 Arena** (25 original proxy capsules), **F3 Dense City**, from M01/S01 #21 and PR #101.
- **F4 Density Ladder** from M01/S04 #24 and PR #103. Within the density view use **1, 2, 3, 4** to select 25/50/100/200 capsules and **G/L/V/C** to isolate geometry/lights/GPU particles/combined work. Config and caps are shared from `stress/config/ladder.v1.json` (relative to the stress script), with safety fallback.
- **B Baseline**, **N Candidate**, **D Compare** on static scenes. The integrated app saves PNG captures **without its HUD** in the local Godot `user://visual_truth/` directory, then compares RGB pixels and displays changed percentage and mean absolute channel error. Threshold defaults to 2/255. Native comparison is a preview; `visual_truth/compare.py` from S03 #23 / PR #102 remains the strict offline PNG comparison with fail-closed CLI and reproducible JSON output.

## First launch

1. Open **`nex_bench/project.godot`** with the pinned Godot 4.7.2 editor on a native desktop and press F5 / Run Project.
2. Use the **clickable toolbar** or F1..F4. Start with Corridor.
3. For repeatable image checks, capture B baseline and N candidate **at the same resolution, renderer, camera and settings**, then press D. The screenshots are created locally, not uploaded. Note the folder in the app status line.
4. For an offline strict PNG report, change to the printed captures folder and execute Python with an absolute script path (example: `python C:/path/to/nex-engine/nex_bench/visual_truth/compare.py corridor_static_baseline.png corridor_static_candidate.png --pixel-tolerance 2`). The Python tool rejects input paths escaping the working directory, by design.

The original standalone Godot projects at `nex_bench/scenes/base/project.godot` and `nex_bench/stress/project.godot` continue to work independently. The unified hub contains no third-party assets, online API calls or new package dependencies. Native screens and project integration are original demonstration assets only.

## Tests and limitations

Existing CI: `python3 -m unittest discover -s tests/ci -p 'test_*.py' -v`; contract and FramePulse suites run in the same protected Fast Lane. The new `tests/ci/test_integrated_hub.py` asserts integrated file wiring, only static screenshot paths, bounded stress config relative to its script, and preservation of all feature test files. CI is **not** native Godot rendering; before claiming native VERIFIED, independently run the pinned Godot import/GUI smoke (F1..F4 plus screenshots), record editor messages and actual GPU backend. No measured FPS/p95/p99, GPU/VRAM, visual equivalence, production-ready engine/editor or runtime benchmark claim follows from these synthetic/static tests.

## Native import smoke (local, optional)

With the **pinned Godot 4.7.2 binary installed**, from repository root:

```bash
godot --headless --path nex_bench --rendering-method gl_compatibility --script res://smoke.gd
```

Expect `NEX_NATIVE_IMPORT_SMOKE_PASS` and exit code 0. This exercises main scene creation and all four world modes, **not** a Forward+ visual/GPU/performance validation. We have not run this Godot binary in the current GitHub-only session; execute locally before claiming native runtime verified.

## Windows: launch the integrated app with one double-click

On Windows 11, **double-click `nex_bench/Start-NEX.cmd`**. The launcher checks the pinned Godot 4.7.2 version, runs all four modules through the existing headless import smoke, then opens the visual lab GUI only if validation passed. Godot must already be installed; no installer, cloud dependency, administrator access or download is required.

If Godot isn't on your PATH, call from PowerShell:

```powershell
.\nex_bench\Start-NEX.ps1 -GodotPath "C:\Tools\Godot_v4.7.2-stable_win64.exe"
.\nex_bench\Start-NEX.ps1 -GodotPath "C:\Tools\Godot_v4.7.2-stable_win64.exe" -SmokeOnly
```

Alternatively set the `NEX_GODOT_BIN` environment variable to the Godot executable before launching. A version mismatch, missing binary or failed headless smoke blocks GUI startup and shows a diagnosis; it does not silently downgrade safety. After launch use F1–F4 and B/N/D controls. **The launcher and its wiring have only source-level CI tests so far; executing it on a native Windows/Godot installation is still required.** Headless compatibility mode is not a measured Forward+ GPU test.

## Native Visual Truth regression smoke

The same native Godot import smoke also compares small **in-memory images** through the app's own pixel-diff function. It checks identical images, one changed pixel out of two, and mismatched dimensions. Look for `NEX_NATIVE_VISUAL_TRUTH_PASS` in the Linux and Windows job logs. This test does not capture the real GPU framebuffer or replace a visible GUI/screenshot acceptance test. It intentionally does not overwrite saved user baselines.

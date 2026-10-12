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

## Visual Truth heatmap (desktop preview)

On a static scene, press **B** then **N** to save two captures and **D** to compare them. The result now opens a **bottom-right native heatmap preview**, with altered pixels highlighted in red against a dim grayscale reference. The app also writes `<scene>_heatmap.png` beside the two screenshots in `user://visual_truth/`. Click **FECHAR MAPA DE DIFERENCAS** or switch scenes to dismiss the preview. A failed image write is reported without masking the in-memory comparison; both original captures remain untouched.

The heatmap uses the native pixel tolerance of 2/255. The synthetic Godot native smoke validates altered-pixel color, panel creation and dismissal. It is **not** a real framebuffer capture or display/GPU test; real Windows screenshots and GPU performance still need observation.

## Renderer diagnostics | F9

Press **F9** or **DIAGNOSTICO [F9]** in the toolbar to toggle a bottom-left local telemetry panel. It reads the actual Godot renderer method/driver and video adapter name where exposed, observed FPS, CPU process duration, draw calls, 3D object count and the renderer-reported graphics allocation. Values update about every 0.75 seconds while the panel is visible. On headless builds, missing GPU details explicitly display **N/A**. A zero/unsupported renderer allocation also displays **N/A**, never invented VRAM. **This is live descriptive diagnostics, not a benchmark:** it does not provide total GPU VRAM, true GPU render latency, p95/p99, or reproducible benchmark results. Use the Windows desktop target for actual GPU qualification. The native headless smoke now verifies the eight controls, F9 toggling, and labels using the Godot engine API, but not representative GPU metrics.

## Camera navigation | real changed-frame visual diff

On **F1/F2/F3** scenes use **Left/Right** to orbit the camera 15 degrees, **Up/Down** to change elevation by 10 degrees, **PageUp/PageDown** to zoom and **Home** to restore the exact original reference camera. Changes are limited to the active scene with bounded elevation (12–76 degrees) and zoom (40–200% of original distance). This **does not edit the .tscn source** and deliberately does not apply to F4 Density Ladder.

For a meaningful comparison of two **actually different rendered screenshots**, on F1 press **B**, press **Right**, press **N**, then **D**. The existing pixel diff and red heatmap should show a nonzero changed-pixel ratio. **Home** restores the original reference view. Moving the camera intentionally changes viewpoint, so this is a functional end-to-end test, not a same-camera visual regression test. Native headless CI exercises actual Godot camera movement/reset, not physical GPU screenshots. A subsequent local Codex Desktop run can validate visible rendered B/N/D on the RTX GPU.

## Density Ladder: F10 frame-interval capture

In **F4**, select count 25/50/100/200 with 1/2/3/4 and effects with G/L/V/C, then press **F10**. The app waits **2 seconds** to warm up, collects **up to 8 seconds** of actual `_process(delta)` intervals (at most **1500 samples**) and saves JSON under Godot's local `user://frame_observations/`. Press F10 again to cancel. Changing scene/count/effects during collection cancels rather than mixing scenarios. Fewer than 60 samples means **no report saved**.

JSON includes renderer, adapter, OS, viewport, FPS cap, VSync mode, proxy count, effect mode, sample count, observed mean FPS, **nearest-rank p50/p95/p99 main-loop frame intervals**, and the **ordered original per-frame interval samples in milliseconds** (`frame_intervals_ms`, max 1500) so aggregates can be independently recalculated. These are **not GPU frametime, total VRAM or unthrottled maximum FPS** and may be VSync/refresh capped. Repeat the same scenario under consistent conditions before comparing runs. Native Windows/Linux CI checks only synthetic percentile math and safe start/cancel without writing fictitious measurements. On the RTX 5050, a genuine 8-second capture requires the local Codex Desktop or manual GUI session.


### Validar o JSON de F10 automaticamente (sem GPU)

Execute no repositório local, após salvar uma captura F10 pelo Godot, com Python 3 e somente a biblioteca padrão:

```powershell
python .\nex_bench\validate_frame_observation.py "C:\CAMINHO\frame_observations\density_200_geometry_1234567890.json"
```

O validador retorna **PASS / exit 0** e recalcula a média, FPS médio, p50/p95/p99 e tempo total a partir de **todas as amostras originais**; falha com **FAIL / exit 1** se o JSON tiver chaves duplicadas, dados ausentes, NaN/Infinity, workload inválido, mais de 1500 amostras, discrepância na contagem ou divergência de cálculos. Ele não modifica o arquivo. Preserve o JSON bruto original, saída do validador, log/screenshot e hashes SHA-256 como evidências no mesmo PR.

Os testes sintéticos locais usam `python -m unittest discover -s tests/ci -p 'test_*.py'`. PASS matemático não comprova qualidade visual, GPU frametime real, VRAM total, VSync desligado, repetibilidade entre máquinas ou desempenho máximo.

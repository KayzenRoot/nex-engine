# NEX Engine | M01 Visual Lab (S01)

Native Godot 4.7.2 reference project with **three original built-in 3D scenes** and a keyboard scene selector. This is an executable visual-lab **prototype**, not the finished editor/engine, not gameplay, and not a GPU benchmark.

## Run on Windows / Linux

1. Use Godot 4.7.2 stable (the version pinned by NEX M00).
2. Open the **project in this directory** (`nex_bench/scenes/base/project.godot`) in Godot and press **F6/F5** (run project); alternatively use `godot --path nex_bench/scenes/base --editor` and run the project.
3. Press **1** for Corridor, **2** for Arena (25 proxies), **3** for Dense City. No network, game assets, API keys or paid services required.

The three scene files are standalone `.tscn` Godot Node3D resources; materials, primitive geometry and lights are self-contained. Camera is perspective, pitched ~35.264 degrees for a true diagonal look-at-origin at yaw 45 degrees. Project configuration is **local to this S01 demo**, not the shared M00 smoke `project.godot`.

Run hash validation from repository root: `python3 nex_bench/scenes/base/verify_fixtures.py`. Each `nex_bench/fixtures/base/*.json` uses the promoted `scene_manifest.v1` contract with true SHA-256 bytes for its matching scene. Its declared renderer is the project **requested** Forward+ backend, not hardware-confirmed; verify actual runtime backend before claiming rendered results. All geometry is generated from Godot built-in primitives; external asset list is correctly empty. The numeric seed is a stable fixture identifier, with no procedural randomness used in these static scenes.

**Limitations**: No independent Godot GUI/headless import has been run for this PR by the GitHub-only author. No frame time, GPU load, VRAM, Windows native screenshot, visual parity, or renderer-performance improvement is asserted. Use the pinned local Godot + RTX test environment to establish those separately; headless import is only a parse smoke. Existing CI still tests its own suites and does not build S01 GPU scenes.

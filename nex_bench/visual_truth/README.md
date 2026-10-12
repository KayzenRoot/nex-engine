# NEX Visual Truth | S03 baseline pixel regression

Deterministic PNG screenshot comparison tool for the existing [M01 S03 issue #23](https://github.com/KayzenRoot/nex-engine/issues/23). No paid dependencies or engine changes. It provides a **numeric visual-regression gate**, not perceptual judgment or GPU performance metrics.

```bash
python3 nex_bench/visual_truth/compare.py before.png after.png --pixel-tolerance 2 --max-changed-ratio 0.005 > visual-truth.json
```

Exit codes: **0** passed, **1** screenshot differs beyond allowed ratio, **2** malformed/unsupported input. Output includes changed-pixel ratio, normalized mean absolute error and worst RGB channel error. Files must be identical dimensions, RGB or RGBA PNG with 8-bit channels, noninterlaced, up to 4096 pixels each side. All PNG row filter methods are decoded and CRCs verified. Transparency is composited onto black. Other PNG color types or interlaced inputs are rejected, not silently treated as valid.

Use captures from the same real Godot scene, graphics backend, camera, resolution and settings. Lighting, display, anti-aliasing, color space and driver differences may affect pixels; thresholds should be calibrated using known-good images, never adjusted solely to hide regressions. This initial implementation uses SYNTHETIC unit inputs in CI. Native S01 camera screenshots and golden image collection are pending real Godot execution; no baseline image was fabricated.

For CLI safety, input PNG paths must be relative and remain inside the current working directory; symlink escapes are rejected. Use normal shell redirection for JSON reports.

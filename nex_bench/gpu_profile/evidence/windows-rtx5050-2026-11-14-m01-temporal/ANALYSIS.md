# NEX M09 · M01 temporal stability — RTX 5050

**Status:** `TEMPORAL_STABILITY_OBSERVED / SINGLE_SESSION / STATIC_WORKLOAD / NO_QUALITY_CLAIM`

## Question

Are repeated frames of the same static M01 scene/preset stable over time, or
does the rendered image vary frame-to-frame? This report covers 5 frames per
scene/preset at 1280×720, spaced 30 frames apart after a 180-frame warmup.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_VISUAL_SEQUENCE=1`, `NEX_PRESET_AB_SCENE`,
  `NEX_PRESET_AB_PRESET`, `NEX_PRESET_AB_WIDTH=1280`,
  `NEX_PRESET_AB_HEIGHT=720` and `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- Each scene is instanced with its base camera and lights plus deterministic
  fillers to 100 `MeshInstance3D` total.
- After 180 warmup frames, the harness captures 5 viewport images, waiting 30
  frames between captures. Each image is flipped Y and saved as 8-bit RGB PNG.
- Comparison uses `docs/benchmarks/m09/tools/png_image.py`: exact RGB byte
  differences, `changed_pixels_pct` counts pixels with any channel difference
  greater than 2.

## Results

| Scene | Preset | Frames | Unique SHA-256 | Frame-to-frame mean abs | Changed pixels | Verdict |
|---|---|---:|---:|---:|---:|---|
| corridor_static | ab-low | 5 | 1 | 0.0000 | 0.000% | stable |
| corridor_static | ab-high | 5 | 1 | 0.0000 | 0.000% | stable |
| arena_combat | ab-low | 5 | 1 | 0.0000 | 0.000% | stable |
| arena_combat | ab-high | 5 | 1 | 0.0000 | 0.000% | stable |
| dense_city | ab-low | 5 | 1 | 0.0000 | 0.000% | stable |
| dense_city | ab-high | 5 | 1 | 0.0000 | 0.000% | stable |

- Every cell has one SHA-256 shared by all five frames.
- All frame-to-frame comparisons are exactly zero.
- No temporal variation was observed in this static workload.

## Observations

- The capture path is temporally deterministic on this machine for the tested
  static scenes and presets.
- The result does not cover animation, camera motion, dynamic lighting,
  particles or any temporal effect; it only covers repeated frames of a static
  composition.
- The result is not a quality ranking or a guarantee for other scenes,
  hardware, drivers or sessions.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- Static scenes only; no animation, temporal effects or camera motion.
- Fillers are deterministic but may overlap base-scene props.
- PNG comparison is exact RGB byte comparison; it does not model human
  perception or color spaces.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS, quality or universal recommendation is claimed.

# NEX M09 · Camera-motion sequence — RTX 5050

**Status:** `CAMERA_MOTION_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the harness support a deterministic camera-motion sequence and produce
distinct frames for each captured step? This fills the "camera motion not
covered" gap without changing scene content or claiming quality.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_VISUAL_SEQUENCE=1` and the additive
  `NEX_PRESET_AB_CAMERA_MOTION=1`.
- The camera orbits the origin by **3° per captured frame**; five frames are
  captured per scene/preset with a 30-frame interval after a 180-frame warmup.
- Three M01 scenes × two presets × five frames = **30 PNGs**, all 1280×720.
- Every PNG is checked against its manifest SHA-256; consecutive frames are
  compared with exact RGB bytes and a changed-pixel threshold of 2.
- The static temporal-stability bundle remains the reference for identical
  static frames; this bundle measures motion, not stability.

## Results

| Scene | Preset | Frames | Mean abs médio | Changed pixels máx | PSNR mín |
|---|---|---:|---:|---:|---:|
| corridor_static | ab-low | 5 | 5.0913 | 19.766% | 21.734 dB |
| corridor_static | ab-high | 5 | 5.1619 | 19.168% | 21.428 dB |
| arena_combat | ab-low | 5 | 2.1781 | 8.534% | 25.912 dB |
| arena_combat | ab-high | 5 | 2.2321 | 8.088% | 25.728 dB |
| dense_city | ab-low | 5 | 1.7989 | 7.051% | 27.127 dB |
| dense_city | ab-high | 5 | 1.8396 | 6.477% | 26.768 dB |

## Observations

- All 30 frames were captured with the deterministic orbit; every consecutive
  frame pair differs in at least one pixel.
- The mean absolute difference grows with frame index as the orbit accumulates
  rotation; corridor has the largest differences and city the smallest.
- The high preset produces slightly larger differences than the low preset in
  every scene, consistent with its higher resolution scale and effects.
- This is a harness capability observation for camera motion, not a quality,
  stability or performance claim.
- Static temporal stability remains covered by the separate
  `temporal-stability.v1.json` bundle.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- Discrete 3-degree camera steps between captured frames; not continuous
  animation.
- Static scene content; animation, VFX, physics and gameplay motion are not
  covered.
- Exact RGB byte comparison does not model human perception or color spaces.
- No FPS, quality or universal recommendation is claimed.

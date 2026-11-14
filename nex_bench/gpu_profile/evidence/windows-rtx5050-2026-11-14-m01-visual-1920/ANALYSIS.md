# NEX M09 · M01 visual truth at 1920×1080 — RTX 5050

**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

How large is the `ab-low` → `ab-high` pixel difference on the three M01 scenes
at 1920×1080, and does it differ from the 1280×720 measurement? The answer is
limited to this session, GPU, driver and scene composition.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_VISUAL=1`, `NEX_PRESET_AB_SCENE`,
  `NEX_PRESET_AB_PRESET`, `NEX_PRESET_AB_WIDTH=1920`,
  `NEX_PRESET_AB_HEIGHT=1080` and `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- Each scene is instanced with its base camera and lights plus deterministic
  fillers to 100 `MeshInstance3D` total.
- After applying the preset, the harness waits 180 frames, reads the viewport
  texture after `RenderingServer.frame_post_draw`, flips Y and saves an 8-bit
  RGB PNG at 1920×1080.
- Sequence per scene: low, high, low, high, low, high (three images per cell).
- Comparison uses `docs/benchmarks/m09/tools/png_image.py`: exact RGB byte
  differences, `changed_pixels_pct` counts pixels with any channel difference
  greater than 2.

## Results at 1920×1080

| Scene | A/A identical | A/A mean abs diff | A/B mean abs diff | A/B max abs diff | A/B changed pixels | A/B PSNR |
|---|---|---|---:|---:|---:|---:|---:|
| Corridor | yes (3+3) | 0.0000 | 0.4168 | 167 | 3.367% | 38.485 dB |
| Arena | yes (3+3) | 0.0000 | 0.4215 | 189 | 3.354% | 36.851 dB |
| City | yes (3+3) | 0.0000 | 0.1785 | 146 | 1.276% | 40.464 dB |

- Every scene/preset group has one SHA-256 shared by all three repetitions.
- All six A/A pairs per scene are exactly zero.
- All three matched A/B pairs per scene produce the same metrics above.

## Comparison with 1280×720

| Scene | 1280 A/B mean abs | 1920 A/B mean abs | 1280 changed pixels | 1920 changed pixels |
|---|---:|---:|---:|---:|
| Corridor | 0.5135 | 0.4168 | 4.077% | 3.367% |
| Arena | 0.4898 | 0.4215 | 3.884% | 3.354% |
| City | 0.2317 | 0.1785 | 1.745% | 1.276% |

- At 1920×1080 the A/B mean absolute difference and changed-pixel fraction are
  slightly lower than at 1280×720 in all three scenes; PSNR is slightly higher.
- The direction is consistent: the high preset changes the image in every
  scene, and the city remains the smallest difference.
- This is a pixel-difference observation, not a quality ranking.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- Static frame only; animation, temporal effects and camera motion are not
  covered.
- Fillers are deterministic but may overlap base-scene props; this is a stress
  composition, not a beauty shot.
- PNG comparison is exact RGB byte comparison; it does not model human
  perception, color spaces or display calibration.
- The harness applies a subset of `preset_pack.v1` settings.
- No FPS, quality or universal recommendation is claimed.

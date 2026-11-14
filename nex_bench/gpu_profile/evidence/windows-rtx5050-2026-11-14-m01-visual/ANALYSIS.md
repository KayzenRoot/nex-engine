# NEX M09 · M01 visual truth — RTX 5050

**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Do `ab-low` and `ab-high` produce measurably different rendered images on the
three M01 base scenes, and are repeated captures deterministic? The answer is
limited to this session, GPU, driver and scene composition.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_VISUAL=1`, `NEX_PRESET_AB_SCENE` and
  `NEX_PRESET_AB_PRESET`.
- Each scene is instanced with its base camera and lights plus deterministic
  fillers to 100 `MeshInstance3D` total, as in the performance A/B/A.
- After applying the preset, the harness waits 180 frames, reads the viewport
  texture after `RenderingServer.frame_post_draw`, flips Y and saves an 8-bit
  RGB PNG at 1280×720.
- Sequence per scene: low, high, low, high, low, high (three images per cell).
- Comparison: `docs/benchmarks/m09/tools/png_image.py` decodes PNG scanlines
  without resampling or color management and computes per-channel absolute
  differences. `changed_pixels_pct` counts pixels with any channel difference
  greater than 2.

## Results

| Scene | A/A identical | A/A mean abs diff | A/B mean abs diff | A/B max abs diff | A/B changed pixels | A/B PSNR |
|---|---|---|---:|---:|---:|---:|---:|
| Corridor | yes (3+3) | 0.0000 | 0.5135 | 170 | 4.077% | 37.406 dB |
| Arena | yes (3+3) | 0.0000 | 0.4898 | 187 | 3.884% | 36.386 dB |
| City | yes (3+3) | 0.0000 | 0.2317 | 133 | 1.745% | 39.763 dB |

- Every scene/preset group has one SHA-256 shared by all three repetitions.
- All six A/A pairs per scene are exactly zero (identical pixel buffers).
- All three matched A/B pairs per scene produce the same metrics above.
- The A/B difference is largest in corridor and smallest in city at this fixed
  camera and 100-mesh composition.
- The difference is concentrated in edges and shading detail affected by
  resolution scale, MSAA, shadows and glow; it is not a quality ranking.

## Observations

- The capture path is deterministic on this machine: repeated runs are
  byte-identical, so the A/A comparison is not a tolerance-based pass.
- The high preset changes the image in all three scenes, which confirms that
  the performance A/B/A measured a real rendering-state change rather than a
  no-op preset.
- City has the smallest changed-pixel fraction (1.745%), consistent with its
  large ground plane and relatively small screen coverage of detailed props.
- No claim is made that one image is better, sharper in a perceptual sense, or
  representative of another GPU, driver or session.

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

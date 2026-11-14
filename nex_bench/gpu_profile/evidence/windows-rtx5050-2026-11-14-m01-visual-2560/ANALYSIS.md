# NEX M09 · M01 visual truth at 2560×1440 — RTX 5050

**Status:** `VISUAL_DIFFERENCE_OBSERVED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the visual-difference pattern measured at 1280×720 and 1920×1080 hold at
2560×1440? This report fills the last documented visual-truth resolution gap.

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_VISUAL=1`, the M01 scene, `NEX_PRESET_AB_WIDTH=2560`,
  `NEX_PRESET_AB_HEIGHT=1440` and `NEX_PRESET_AB_NATIVE_RESOLUTION=1`.
- Visual mode waits 180 frames after applying the preset, reads the 2560×1440
  viewport, corrects orientation and saves a PNG.
- Three repetitions per scene/preset pair; every repetition of a pair shares
  one SHA-256 (A/A exact).
- The 1920×1080 context comes from the already integrated
  `m01-visual-1920.v1.json` report measured earlier on the same day; it is not
  re-measured here.
- The desktop is 2560×1080; the 2560×1440 window is taller than the display
  and the viewport is captured off-screen. One initial corridor/high capture
  was clipped to 2560×1009 and re-captured at 2560×1440.

## Results (median/representative frame per scene)

| Scene | A/A identical | A/A mean abs | A/B mean abs | A/B max abs | A/B changed pixels | A/B PSNR | Δ mean abs vs 1920 |
|---|---|---:|---:|---:|---:|---:|---:|
| corridor_static | sim | 0.0000 | 0.3694 | 168 | 2.996% | 39.085 dB | −11.4% |
| arena_combat | sim | 0.0000 | 0.3863 | 190 | 3.074% | 37.136 dB | −8.4% |
| dense_city | sim | 0.0000 | 0.1524 | 123 | 1.031% | 40.790 dB | −14.6% |

## Observations

- A/A is exact: all three repetitions of each scene/preset pair share one
  SHA-256 at 2560×1440.
- ab-high changes the image in every scene; changed pixels are 2.996%
  (corridor), 3.074% (arena) and 1.031% (city).
- The A/B mean absolute difference is slightly lower at 2560×1440 than at
  1920×1080 in all three scenes (−8.4% to −14.6%), continuing the direction
  observed from 1280×720 to 1920×1080.
- The ordering is consistent across resolutions: arena has the largest A/B
  difference and city the smallest.
- This is a pixel-difference observation, not a quality ranking or a universal
  recommendation.

## Limitations

- Single session on one RTX 5050; no cross-device, cross-driver or
  cross-session generalization.
- Static frame only; animation, temporal effects and camera motion are not
  covered.
- Fillers may overlap base-scene props; this is a stress composition, not a
  beauty shot.
- PNG comparison is exact RGB byte comparison; it does not model human
  perception or color spaces.
- The harness applies a subset of `preset_pack.v1` settings.
- The 2560×1440 window is taller than the 2560×1080 desktop; the viewport is
  captured off-screen.
- One initial corridor/high capture was clipped to 2560×1009 and re-captured;
  the committed image is 2560×1440.
- No FPS gain, quality or universal recommendation is claimed.

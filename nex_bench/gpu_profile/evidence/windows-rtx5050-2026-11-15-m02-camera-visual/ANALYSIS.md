# NEX M02-S01 · Isometric camera A/B/A — RTX 5050

**Status:** `SCENE_COMPARISON_MEASURED / SINGLE_SESSION / NO_QUALITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Does the M02 `IsometricCameraRig` reproduce the frozen M01 scene camera framing,
and what is the pixel difference between the baseline camera and the rig?

## Method

- Harness: `nex_bench/scenes/preset_ab/preset_ab.gd` with
  `NEX_PRESET_AB_CAMERA_MODE=baseline|rig` and the M01 scene.
- The rig is vendored at `nex_bench/scenes/m02_camera/camera_rig.gd` from
  `nex_modules/render3d/camera/camera_rig.gd`; a test asserts the copies match.
- The rig is configured per scene with the baseline camera distance and FOV,
  yaw 45° and pitch −35.264°, focus at the origin.
- Three repetitions per mode per scene; visual mode waits 180 frames before
  the capture. Every repetition of a mode is byte-identical.
- The comparison is exact RGB bytes with changed-pixel threshold 2.

## Results

| Scene | A/A identical | A/B mean abs | A/B changed pixels | A/B PSNR | A/B max abs |
|---|---|---:|---:|---:|---:|
| corridor_static | sim | 0.0020 | 0.013% | 59.66 dB | 141 |
| arena_combat | sim | 0.0003 | 0.003% | 71.95 dB | 34 |
| dense_city | sim | 0.0000 | 0.000% | 106.53 dB | 1 |

## Observations

- The rig reproduces the baseline framing with a negligible pixel difference:
  city is effectively identical (max diff 1), arena differs in 0.003% of pixels,
  and corridor differs in 0.013% of pixels (edge rounding).
- All three repetitions of each mode are byte-identical, so the comparison is
  deterministic.
- This is a scene-comparison observation, not a quality ranking or a claim that
  the rig improves visual fidelity.
- The result supports using the rig as a drop-in camera for future M02 scene
  integration; it does not prove behavior under animation or gameplay.

## Limitations

- Single session on one RTX 5050; no cross-device or cross-session generalization.
- One preset (`ab-low`), static frame and one camera pose per scene.
- Exact RGB comparison does not model human perception or color spaces.
- No animation, camera motion, gameplay or production-scene validation.
- No FPS, quality or universal recommendation is claimed.

# NEX M02-S02/S03/S04 · Scene analysis — RTX 5050

**Status:** `SCENE_ANALYSIS_MEASURED / HEADLESS / NO_RENDERING_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

## Question

Do the sightline, depth-composition and temporal prototypes produce meaningful,
deterministic results when fed real M01 scene geometry and integrated static
frames?

## Method

- Headless `SceneTree` script `nex_bench/scenes/m02_analysis/run_analysis.gd`.
- Loads each M01 base scene, computes world AABBs of `MeshInstance3D` nodes,
  and uses the largest 8 as sightline occluders and the largest 16 as depth
  sphere primitives.
- Sightline: deterministic player/threat/decoration layout around the largest
  AABB; 10 update steps of 50 ms.
- Depth: scene camera looking at the origin; opaque primitives with every fifth
  marked gameplay-critical.
- Temporal: 4×4 luminance regions from the five static `ab-low` frames of the
  integrated temporal-stability bundle; motion 0, alpha 1, edge false.
- No rendering, GPU, TAA or compositor is executed.

## Results

| Scene | Meshes | Occluders | Primitives | Reveals | Danger alerts | Critical unseen | Z-fight risks | Temporal |
|---|---:|---:|---:|---:|---:|---|---:|---|
| corridor_static | 17 | 8 | 16 | 1 | 1 | não | 0 | BASELINE_ACCEPTABLE |
| arena_combat | 34 | 8 | 16 | 1 | 1 | não | 4 | BASELINE_ACCEPTABLE |
| dense_city | 23 | 8 | 16 | 1 | 1 | não | 4 | BASELINE_ACCEPTABLE |

## Observations

- The sightline policy is exercised on real scene AABBs: the player is blocked
  by the largest occluder and becomes visually readable after the reveal delay;
  the threat raises a danger alert; decoration does not trigger a reveal.
- No critical actor is left unseen in any scene.
- The depth planner reports 4 z-fight-risk pairs in arena and city and none in
  corridor; no alpha-over-critical or overlay-gameplay conflicts were found.
- The temporal analyzer returns `BASELINE_ACCEPTABLE` on the five static frames
  of all three scenes with zero ghosting, flicker and shimmer.
- These are deterministic analysis results over real scene data, not rendering,
  visual quality or performance claims.

## Limitations

- Meshes are approximated as AABBs or spheres; real per-pixel depth, edges,
  aliasing and transparent surfaces are not evaluated.
- One deterministic actor layout per scene; no gameplay or animation.
- Temporal analysis uses 4×4 luminance regions from static frames; real TAA,
  upscale and compositor behavior remain `INCONCLUSIVE_NOT_RUN`.
- No rendering, GPU, FPS, quality or cross-device claim.

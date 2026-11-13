# NEX M02-S04 · TemporalGuard prototype (analysis and gate only)

**Status:** `PROTOTYPE / ANALYSIS_AND_GATE_ONLY / NO_RENDERING / NO_COMPOSITOR / NO_SHADER / RISK_ELEVATED_DECISION_RECORDED`
**Work Order:** NEX-M02-S04-WO-001 (Issue #31) · **Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable (pinned by M00). Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## Risk decision (ELEVATED)

- **No render thread, no CompositorEffect, no shader, no renderer core.** This prototype analyzes synthetic region sequences and gates a mocked postprocess state.
- **Irreversible operations:** none. Postprocess is disabled by default; enabling requires a measured defect plus compositor availability; disabling is always allowed; every new analysis resets the toggle.
- **Residual risk:** real-scene ghosting/flicker/shimmer cannot be measured without rendering. The verdict for real scenes is **`INCONCLUSIVE_NOT_RUN`**, never a fabricated pass.
- Any CompositorEffect/render-thread implementation requires a **separate Owner-admitted WO**, pinned ABI review, measured failure evidence and explicit risk acceptance.

## Metrics

| Metric | Definition |
|---|---|
| `ghosting` | Step changes in region luminance followed by a stale value closer to the old value; normalized maximum convergence lag. |
| `flicker` | Sign changes of frame-to-frame luminance deltas above `flicker_min_delta`, normalized per region. |
| `shimmer` | High-frequency edge variation: mean absolute delta excluding the single largest (a clean step is not shimmer), edge regions only. |
| `sharpness_penalty` | `(1 - render_scale) * 0.5`; informational, not a quality claim. |

## Verdict and gate

- **`BASELINE_ACCEPTABLE`** → `KEEP_NATIVE`.
- **`DEFECT_REPRODUCED`** → `EVALUATE_COMPOSITOR`; with `prefer_native=true` → `NO_GO`.
- **`INCONCLUSIVE`** (missing frames/regions, invalid values, invalid render scale) → `NO_GO`.
- `set_postprocess_enabled(true)` is rejected unless the compositor is available **and** the last report is a defect with `EVALUATE_COMPOSITOR`.
- The toggle is a mock state; no shader/compositor is implemented.

## API

| Method | Purpose |
|---|---|
| `configure(dict) -> bool` | Thresholds, step/min-delta, min frames, max regions. |
| `analyze(frames, options) -> dict` | Metrics, verdict, action, gate state; `render_scale`, `prefer_native`. |
| `set_compositor_available(bool)` | Marks compositor availability (mock). |
| `set_postprocess_enabled(bool) -> bool` | Guarded toggle with rollback. |
| `get_report() -> dict` | Last report copy. |
| `reset()` | Clears report/state/error. |

Frame format: array of frames; each frame is a dictionary keyed by region id with `{luminance 0..1, motion [dx,dy], alpha 0..1, edge bool}`.

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/render3d/temporal `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M02_S04_SMOKE_PASS: 51 checks`; log committed under `evidence/`.

## Limits (explicit)

- No rendering, TAA, upscale, MSAA, screenshots or human visual gate; no GPU/VRAM/frame-time.
- Metrics operate on synthetic region luminance, not pixels; they detect injected patterns, not prove real-scene quality.
- Real thin lines, emissive VFX, HUD overlays and fast camera motion must be validated by a future scene-integration WO.
- The analyzer is deterministic and thread-free by design; thread-safety claims are out of scope.
- No M04 PBR, engine, CI or contract changes.

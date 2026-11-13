# NEX M05-FXBUDGET · FX-budget planner (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_PARTICLES / NO_RENDERING / NO_VISUAL_CLAIM`
**Work Order:** NEX-M05-FXBUDGET-WO-001 (Issue #10) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`FXBudgetPlanner` reads spells in the `spellfx.v1` vocabulary and returns a deterministic budget report:

- Validates spell/phase/emitter identity, element and kind vocabulary, impact phase, gameplay authority, light-bridge coherence, durations and decal policy.
- Aggregates spells, emitters, particle amounts, GPU emitters, decals, light bridges and total duration, with per-spell detail.
- Flags budgets at or over their limit (`TIGHT` at 90%).
- Generates a particle reduction plan (halve the largest particle/trail/beam amounts in rounds until the budget is met) and a GPU reduction plan (convert the smallest GPU emitters to CPU until the count fits).
- Emits `FIT`, `TIGHT`, `OVER_BUDGET` or `INVALID_INPUT`.

## Contract vocabulary (spellfx.v1)

| Contract field | Planner use |
|---|---|
| `spell_id` / `element` | Contract id pattern and element enum |
| `phases[].phase` | `cast`, `travel`, `impact`, `linger`; impact required |
| `phases[].duration_ms` | Per-spell total ≤ 60000 ms |
| `emitters[].emitter_id` | Unique per spell |
| `emitters[].kind` | `particles`, `trail`, `beam`, `decal`, `light` |
| `emitters[].amount` / `gpu` | Particle total and GPU count |
| `emitters[].light_bridge` | Must match `kind == light` |
| `gameplay_authority` | Damage and hit detection must remain `gameplay` |
| `decal_policy` | Must not exceed `fx_budget.max_decals` |
| `fx_budget` | `max_emitters`, `max_particles`, `max_gpu_particles`, `max_decals` |

The planner mirrors the contract vocabulary; it does not modify the contract.

## API

| Method | Purpose |
|---|---|
| `configure({max_emitters, max_particles, max_gpu_emitters, max_decals})` | Budgets. |
| `analyze(spells)` | Deterministic report, findings and reduction plans. |
| `get_last_report()` | Last report. |
| `clear()` | Restore defaults. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/vfx/fxbudget `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M05_FXBUDGET_SMOKE_PASS: 57 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No rendering**: no particle system, emitter, light, decal or shader is created.
- Particle totals are arithmetic amounts, not alive particles, overdraw or fill rate.
- GPU→CPU conversion is a planning suggestion, not a measured quality/performance trade-off.
- Emitter merging and decal reduction have no projected scene in this prototype.
- Visual clarity and runtime cost: `INCONCLUSIVE_NOT_RUN`.
- Real FX integration requires a future M05 WO; M05 parent remains `NOT_ADMITTED`.

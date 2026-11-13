# NEX M10-FEEDBACK · Combat-feedback planner (prototype)

**Status:** `PROTOTYPE / PLANNING_ONLY / NO_ANIMATION / NO_RENDERING / NO_GAME_FEEL_CLAIM`
**Work Order:** NEX-M10-FEEDBACK-WO-001 (Issue #15) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`
**Engine:** Godot 4.7.2-stable. Self-contained project for deterministic headless tests; not wired into `nex_bench` or the engine tree.

## What it does

`FeedbackPlanner` consumes the `feedback.v1` vocabulary and returns a deterministic combat-feedback plan:

- Configures budgets for hit-stop, camera shake, concurrency and total channels.
- Registers attack phases (`anticipation`, `active`, `recovery`), hit events (damage, critical, element) and feedback channels (`hit_stop`, `camera_shake`, `flash`, `recoil`, `damage_number`).
- Sorts a timeline by start time, priority and id.
- Computes peak concurrency, total hit-stop, max shake intensity and damage-number count.
- Reports conflicts: event outside attack, critical without damage, channel outside window plus tail, dangling event, damage number without damage, hit-stop/shake/total/concurrency over budget.
- Emits `SAFE_CONFIG_HEURISTIC`, `CONFLICTS_REPORTED` or `INVALID_INPUT`.
- Exports a `feedback.v1` observation only for a safe plan, with performance `UNAVAILABLE` and validated provenance.

## Contract vocabulary (feedback.v1)

| Contract field | Planner value |
|---|---|
| `attack.phases[].phase` | `anticipation`, `active`, `recovery` |
| `hit_events[].element` | `fire`, `ice`, `lightning`, `arcane`, `nature`, `physical` |
| `feedback_channels[].channel` | `hit_stop`, `camera_shake`, `flash`, `recoil`, `damage_number` |
| `budget` | `max_hit_stop_ms`, `max_shake_amplitude`, `max_concurrent_channels`, `max_total_channels` |
| feedback tail | channel may end at most 1000 ms after the attack |

The planner mirrors the contract; it does not modify it.

## API

| Method | Purpose |
|---|---|
| `configure({max_hit_stop_ms, max_shake_amplitude, max_concurrent_channels, max_total_channels})` | Budgets. |
| `set_attack(attack_id, phases)` | Attack phases. |
| `register_hit_event(id, at_ms, target_id, damage, critical, element)` | Register a hit event. |
| `register_channel(id, channel, start_ms, duration_ms, intensity, priority, event_id, target_id)` | Register a feedback channel. |
| `plan()` / `get_last_plan()` | Deterministic timeline, metrics and conflicts. |
| `export_observation(observation_id, captured_at_utc, provenance)` | Build a `feedback.v1` observation for a safe plan. |
| `clear()` | Reset all state. |

## Run

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/animation/combat_feedback `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Expected: `NEX_M10_FEEDBACK_SMOKE_PASS: 66 checks`; log committed under `evidence/`.

## Limits (explicit)

- **No animation**: no `AnimationPlayer`, tween, camera, shader, scene or renderer is created.
- Hit-stop/shake budgets are arithmetic, not measured game feel.
- Concurrency counts channel intervals at start instants, not rendered overlap.
- Priority orders the timeline but does not resolve or suppress conflicts.
- Readability and runtime cost: `INCONCLUSIVE_NOT_RUN`.
- Real combat integration requires a future M10 scene WO; M10 parent remains `NOT_ADMITTED`.

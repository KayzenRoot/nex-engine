# NEX M02 · Decision Atlas (R&D)

**Status:** `RESEARCH_ONLY / OWNER_DECISIONS_PENDING / NO_MEASURED_GAP`
**Source of truth:** `hypotheses.v1.json` + `tools/decision_engine.py` (`--check`).
**Audit:** ADMIN_SOLO `NOT_INDEPENDENT`.

## Hypotheses

| ID | Hypothesis | Kind | Native gap | Evidence | Decision | Reason |
|---|---|---|---|---|---|---|
| NEX-M02-RD-ISO | IsoDirector contextual framing | render_feature | UNKNOWN | NOT_MEASURED | **RESEARCH_MORE** | no measured failure; A/B/A required |
| NEX-M02-RD-SIGHT | Sightline contextual reveal | render_feature | UNKNOWN | NOT_MEASURED | **RESEARCH_MORE** | prototype only; real-scene A/B/A required |
| NEX-M02-RD-DEPTH | DepthWeave priority map | render_feature | UNKNOWN | NOT_MEASURED | **RESEARCH_MORE** | no measured z-fight/conflict failure |
| NEX-M02-RD-TEMP | TemporalGuard localized postprocess | render_feature | UNKNOWN | NOT_MEASURED | **RESEARCH_MORE** | HIGH-risk postprocess requires measured gap first |
| NEX-M02-RD-PASS | RenderPassport process tool | process_tool | NONE | PROTOTYPE_VERIFIED | **GO** | process tool with rollback and no rendering change; Owner decision pending |

**No render feature receives GO without a measured gap.** No claim of visual or performance gain is made.

## Rejected redundancies (NO_GO)

| ID | Idea | Reason |
|---|---|---|
| NEX-M02-RED-LOD | Custom mesh LOD | Native mesh LOD exists; tuning belongs to M06. |
| NEX-M02-RED-OCC | Custom occlusion culling | Native occlusion culling exists; tuning belongs to M06. |
| NEX-M02-RED-TAA | Custom TAA/upscaler | Native TAA/upscale options must be measured first; no measured gap. |
| NEX-M02-RED-ZHACK | Global z-depth hack | Composition passes and conflict reporting are safer; no global depth hack. |
| NEX-M02-RED-CORE | GPU-driven core C++ patch | Core intervention is ELEVATED; requires RFC, measured gap and Steward lock. |

## A/B/A plan (per hypothesis)

Each feature is evaluated A (native) → B (prototype) → A (native again) in 3 serial repetitions on the same hardware/SHA/procedure. A result is `INCONCLUSIVE` if any required metric or scene is missing. Missing data is never converted to a gain.

## Ownership and boundaries

- All five hypotheses are owned by M02 (camera/visibility/composition).
- M03 owns lighting/GI/shadows; M04 PBR materials; M05 VFX; M06 LOD/culling/streaming tuning; M08 2.5D. No hypothesis duplicates those owners.
- No engine, shader, addon, compositor, contract or `project.godot` change is authorized here.

## Owner decision

Every hypothesis carries `owner_decision: PENDING`. The engine recommends only; it never approves, merges or promotes a contract. The next legal action is an explicit Owner decision per hypothesis after the A/B/A evidence exists.

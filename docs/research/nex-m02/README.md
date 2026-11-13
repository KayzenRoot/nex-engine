# NEX M02 · R&D decisions (S06)

**Status:** `RESEARCH_ONLY / NO_IMPLEMENTATION / NO_MEASURED_CLAIM`
**Work Order:** NEX-M02-S06-WO-001 (Issue #33) · **Audit:** ADMIN_SOLO `NOT_INDEPENDENT`.

## Contents

- `hypotheses.v1.json` — five hypotheses (IsoDirector, Sightline, DepthWeave, TemporalGuard, RenderPassport) with refutable question, native gap, simplest alternative, data contract, cost/risk, 2.5D compatibility, rollback, A/B/A plan, metrics, sources and Owner decision `PENDING`.
- `tools/decision_engine.py` — deterministic rules; `--check` verifies the JSON recommendations.
- `DECISION-ATLAS.md` — decision matrix and rejected redundancies.
- `proposed-contracts.md` — draft contracts C1–C4 (`DRAFT_NOT_PROMOTED`).

## Run

```powershell
python docs/research/nex-m02/tools/decision_engine.py --check
python -m unittest tests/ci/test_nex_m02_research.py -v
```

Expected: `HYPOTHESES_OK` and tests green.

## Decision summary

- Four render features: **RESEARCH_MORE** — no measured native gap exists; A/B/A on real scenes is required before any GO.
- RenderPassport process tool: **GO** as a process candidate (no rendering change, rollback defined); Owner decision still pending.
- Five redundant ideas: **NO_GO** (native LOD/occlusion/TAA exist; no global z-hack; core patch requires RFC/benchmark).

No implementation, benchmark, FPS, VRAM or visual claim is made. The engine recommends; it never approves or merges.

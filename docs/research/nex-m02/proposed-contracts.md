# NEX M02 · Proposed contracts (DRAFTS, NOT PROMOTED)

**Status:** `DRAFT_NOT_PROMOTED`. None of these contracts is canonical, admitted or implemented. Promotion requires an Owner-admitted Work Order, contract review and a Context Lock; canonical files under `contracts/**` are untouched.

## C1 · Sightline reveal policy v0

- **Fields:** actor id/priority; occluder id/kind/transparent; enter/exit delays; reveal progress; alpha; silhouette; danger alert; critical unseen.
- **Invariants:** gameplay visibility is computed independently and never modified; critical blocked threats always raise an alert; reveal is reversible and capped.
- **Consumer:** future scene integration WO.

## C2 · Depth priority map v0

- **Fields:** pass order (opaque/alpha/overlay), z-fight risk pairs, alpha-over-critical and overlay-gameplay conflicts, stability flag.
- **Invariants:** no global z-depth hack; ties deterministic; conflicts reported, never hidden.
- **Consumer:** future scene integration WO; M08 2.5D draft (see depth_composition/M08 draft).

## C3 · RenderPassport probe v0

- **Fields:** inventory (Godot/OS/renderer/driver/GPU/VRAM), optional runtime probe per capability, capability state/verification, fallback chain, profile settings.
- **Invariants:** GPU name never implies capability; documented states are `DOCUMENTED_UNVERIFIED` until probed; no project.godot writes; no remote collection.
- **Consumer:** future profiles/scene integration WO.

## C4 · Temporal gate v0

- **Fields:** ghosting/flicker/shimmer metrics, thresholds, verdict, action, postprocess toggle state, probe status.
- **Invariants:** no postprocess enabled without a measured defect; every analysis resets the toggle; CompositorEffect/render-thread requires a separate ELEVATED WO.
- **Consumer:** future temporal WO.

## Promotion path

1. Owner admits a specific WO naming the contract and consumer.
2. Contract is reviewed against the pinned Godot 4.7 ABI and existing contracts.
3. Context Lock pins base SHA and file fingerprints.
4. Protected PR with tests; no contract is promoted by research documentation alone.

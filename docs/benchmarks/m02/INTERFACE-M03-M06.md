# NEX M02 · Output interface for M03–M06

**Status:** `INTERFACE_PROPOSED / NOT_IMPLEMENTED`. M02 exposes states; it does not implement M03–M06.

| Consumer | Inputs from M02 | Contract/reference | Required evidence |
|---|---|---|---|
| M03 Lighting | Camera state, visibility/reveal state, capability passport | `contracts/m02/render_core.v1`, C1/C3 drafts | A/B/A in three scenes; lighting must not alter M02 gameplay visibility |
| M04 Materials | Depth plan, alpha/overlay conflicts, passport | `contracts/m02/render_core.v1`, C2/C3 drafts | Alpha sorting and z-fight regression; no M04 shader change in M02 |
| M05 VFX | Temporal gate metrics/verdict, visibility state, passport | C1/C4 drafts, temporal gate | Ghosting/flicker checks; VFX must not hide critical threats |
| M06 Optimization | Passport, fallback chain, M01 baseline/budget | `docs/benchmarks/m01/budget.v1.json`, C3 | Tuning only after measured gap; no duplicate native LOD/culling |

## Rules

- M02 never assumes another module's merged PR exists; consumers provide their own evidence.
- A consumer that changes M02 state must declare it in its WO and re-run the M02 QA ledger.
- Contracts C1–C4 are drafts; consumption requires promotion by a specific Owner-admitted WO.
- No engine/shader/compositor implementation is authorized by this interface document.

# Preserved runs excluded from the required matrix

- The first 12-run attempt at source `d048f5623b0a9cc9e4ada7fdf00873f05e124fb0` is preserved in the preceding evidence directory. The strict validator rejected its timezone-naive timestamps. The defect was corrected by emitting explicit UTC `Z` timestamps in commit `b56bf39b088e03c854cbea9d3b95b59a77b4b2ff`; those earlier raw files were not represented as accepted final evidence.
- A subsequent 12-run set at source `b56bf39b088e03c854cbea9d3b95b59a77b4b2ff` is preserved separately. It passed validation, but was superseded after the HUD was corrected to display only a filename instead of a local absolute path. The final matrix was regenerated at the source SHA recorded in `PROVENANCE.md`.
- During the final GUI session, one additional 200-entity combined-effects run completed while changing effect mode before resetting the load. It is outside the Work Order matrix and is not included among the 12 packaged runs. Its local raw output was left untouched.

No prior run or artifact was deleted.

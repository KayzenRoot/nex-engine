# Evidence correction · GPU-DEVICE-SNAPSHOT.txt checksum

**Date:** 2026-11-15
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Scope:** `SHA256SUMS.txt` line 30 only.

## Finding

The global evidence validator (`docs/benchmarks/tools/validate_evidence.py`) found that
`SHA256SUMS.txt` recorded `ad93615c062a01dd25ff37678eb1a61b44b44007cbe06653d7d3f8a299a3aadc`
for `GPU-DEVICE-SNAPSHOT.txt`, while the committed file hashes to
`f3488105dacea7dbf29e0e4166521eb1acfd89463517a71a23870696cb5faec6`.

The mismatch is present since the bundle was introduced in `af1fe96` and was not
introduced by a later content change. The original manifest line does not match
the committed file under LF, CRLF, BOM or BOM+CRLF variants.

## Correction

The manifest line was updated to the hash of the committed file:

- old: `ad93615c062a01dd25ff37678eb1a61b44b44007cbe06653d7d3f8a299a3aadc`
- new: `f3488105dacea7dbf29e0e4166521eb1acfd89463517a71a23870696cb5faec6`

## What did not change

- `GPU-DEVICE-SNAPSHOT.txt` bytes were not modified.
- No measurement, report, image or other evidence file was modified.
- No claim or limitation in the bundle was changed.

## Verification

`python docs/benchmarks/tools/validate_evidence.py --check` now passes all
bundles and entries, including this one.

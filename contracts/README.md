# NEX M01 contracts

These files define versioned JSON interfaces and an exclusive ownership map only. They do not implement or admit M01, create a scene, collect telemetry, claim engine performance, or assert GPU measurements.

## Scene manifest v1

Validate scene metadata with `m01/scene_manifest.v1.schema.json`.

- `schema_version` is the stable value `scene_manifest.v1`; `scene_id` uses a stable lowercase identifier and `scene_revision` starts at 1.
- `seed` is an unsigned 32-bit integer. `scene_sha256` is exactly 64 lowercase hexadecimal characters and identifies the exported scene artifact bytes. The schema checks its representation, not the referenced bytes.
- `scene_unit_scale_m` is meters per scene unit and must be greater than 0 and at most 1000.
- Camera position and target vectors are ordered x/y/z in meters. The current camera preset contract is perspective projection, with vertical field of view in degrees from 1 through 179 and clip distances in meters. Consumers must also require `far_clip_m > near_clip_m`.
- Resolution width and height are integer pixels from 1 through 16384. Renderer and quality identifiers use the declared enums.
- Every listed asset requires a 64-hex SHA-256 digest, source URI, creator, license identifier, and license URI. `verification.status` is `UNVERIFIED` unless a verifier has evidence; `VERIFIED` requires an `evidence_uri`. Unknown optional assets must not be promoted to verified by default.

## Telemetry run v1

Validate run metadata with `m01/telemetry_run.v1.schema.json`.

- `git_sha` is a lowercase 40-hex Git object ID (SHA-1). It is not an asset or scene SHA-256.
- The clock domain is `monotonic`; timestamps and frame durations use milliseconds. Timestamps must be finite, nonnegative and strictly increase; frame durations must be finite and positive, and `sample_count` must equal the number of samples.
- Warmup and sample counts are explicit nonnegative/positive integers. A consumer must reject a run whose scene ID or scene digest differs from the referenced scene manifest.
- GPU utilization and VRAM use each have an explicit availability state and a nonempty source. `AVAILABLE` requires its numeric measurement; numeric zero is a real measurement. `UNAVAILABLE` requires a source explaining the gap and forbids the metric value. Missing data is never converted to zero.
- No FPS value is defined. Headless or synthetic context does not establish an FPS or GPU performance claim.

## Ownership

`m01/ownership.v1.json` binds exactly the six paths authorized by NEX-CONTRACT-WO-001 to the single `integration-steward` writer. Its two consumers are read-only MOCKs for scene and telemetry contracts. Breaking contract changes make the corresponding consumer stale.

Before granting a writer, normalize slash direction and case using Windows collision rules. Detect equal paths, ancestor/descendant paths, traversal aliases and overlapping globs. Reject dependency graphs that contain cycles or unknown nodes.

## Validation limits

Run the contract tests from the repository root:

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

The tests use only the Python standard library. Their test-only JSON Schema checker is explicitly LIMITED to the keywords exercised by these fixtures; it is not a complete Draft 2020-12 validator. Passing these tests does not prove full JSON Schema standards conformance. A consumer that needs standards-level validation must use a compatible full validator in its own approved environment. The raw JSON helper also rejects duplicate object keys and Python's non-standard NaN/Infinity constants.

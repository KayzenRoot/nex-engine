# Synthetic FramePulse

FramePulse reads a telemetry_run.v1 object and deterministically summarizes
synthetic frame-time samples. It uses Python's standard library only. The
implementation performs a minimal runtime validation of the pinned v1
contract; it is not a full Draft 2020-12 JSON Schema validator.

Every report is labeled SYNTHETIC_NOT_MEASURED. The S02 fixture uses a mock
Git SHA, a stable synthetic scene ID and digest, a stable generator seed, and
120 synthetic samples with injected slow frames. The all-zero 40-character
Git SHA is a mock identity and does not refer to a commit. The scene digest
is SHA-256 of the UTF-8 text
NEX-M01-S02-WO-001:synthetic-scene:framepulse-seed-20261012:v1. The
renderer_id and toolchain
fields are required contract metadata for the synthetic scenario; the engine
was not run. GPU utilization and VRAM are UNAVAILABLE, and their source
fields state that no hardware query or measurement occurred. No output from
this fixture is evidence of achieved FPS, engine performance, or hardware
utilization.

## Input and provenance

The input must use schema_version: telemetry_run.v1 and
execution_mode: synthetic. The analyzer checks required and extra fields,
identifier/hash formats, toolchain metadata, monotonic millisecond timestamps,
frame-time units, sample counts, positive finite frame times, and explicit
GPU/VRAM availability and source. It rejects duplicate JSON object keys,
NaN, infinities, and numeric exponents that overflow to infinity.

git_sha and scene_sha256 are checked for the pinned contract's lowercase
hexadecimal shape. This bounded analyzer has no scene manifest or Git object
database input, so it cannot independently compare those values to external
objects. It retains the IDs, hashes, toolchain, clock, and execution mode in
the result's provenance object.

When hardware is UNAVAILABLE, the result includes the availability and
source but omits a numeric measurement. An available numeric zero remains a
valid numeric value and is not treated as unavailable.

## Metrics

- p50, p95, and p99 frame times are milliseconds. Sort frame times ascending,
  compute h = p * (N - 1), and linearly interpolate between the values at
  floor(h) and ceil(h). For one sample, each quantile equals that sample.
- Synthetic 1%-low uses K = max(1, ceil(0.01 * N)), selects the K slowest
  positive frame times, computes their arithmetic mean, then returns
  1000 / mean_ms. The result field is named
  synthetic_one_percent_low_fps; it is not a measured baseline and does not
  average individual FPS values.
- A slow frame is one whose duration is greater than or equal to the
  configured slow_frame_threshold_ms (default 33.333). Clusters group
  adjacent slow sample indices only; indices are zero-based. They do not infer
  causes such as GPU load, shader compilation, streaming, or camera movement.

## Reproduce

From the repository root:

    python -B -m unittest discover -s tests/telemetry -p 'test_*.py' -v

Use the public helpers analyze_json(text) for strict JSON text or
analyze_run(mapping) for an already decoded object. Both accept the optional
keyword slow_frame_threshold_ms. Invalid inputs raise FramePulseError.

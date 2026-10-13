"""Executable negative regression coverage for actual F10 JSON audit tool."""
from copy import deepcopy
import importlib.util
import json
import math
from contextlib import redirect_stdout
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "nex_bench" / "validate_frame_observation.py"
SPEC = importlib.util.spec_from_file_location("nex_observation_validator", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    samples = [10.0] * 60 + [20.0] * 40
    return {
        "schema_version": "nex_frame_observation.v1",
        "measurement": "OBSERVED_MAIN_LOOP_DELTA_NOT_GPU_TIME",
        "frame_intervals_units": "ms",
        "frame_intervals_ms": samples,
        "sample_count": len(samples),
        "godot": "4.7.2.stable.official",
        "os": "Windows",
        "renderer": "gl_compatibility",
        "driver": "vulkan",
        "captured_at_utc": "2026-10-12T22:00:00Z",
        "proxy_count": 200,
        "effect_mode": "geometry",
        "warmup_seconds": 2.0,
        "requested_seconds": 8.0,
        "observed_seconds": 1.4,
        "mean_interval_ms": 14.0,
        "p50_interval_ms": 10.0,
        "p95_interval_ms": 20.0,
        "p99_interval_ms": 20.0,
        "observed_mean_fps": 1000.0 / 14.0,
    }


class FrameObservationValidatorTests(unittest.TestCase):
    def test_independently_recalculates_all_aggregates(self):
        result = MODULE.validate_report(fixture())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["sample_count"], 100)
        self.assertEqual(result["recalculated"]["p50_interval_ms"], 10.0)
        self.assertEqual(result["recalculated"]["p95_interval_ms"], 20.0)
        self.assertEqual(result["recalculated"]["observed_seconds"], 1.4)
        self.assertEqual(result["measurement"], MODULE.MEASUREMENT)

    def test_tampered_percentile_mean_fps_and_elapsed_time_fail(self):
        for name, bad in (
            ("p50_interval_ms", 20.0),
            ("p95_interval_ms", 10.0),
            ("p99_interval_ms", 100.0),
            ("mean_interval_ms", 13.0),
            ("observed_mean_fps", 99.0),
            ("observed_seconds", 9.0),
        ):
            with self.subTest(name=name):
                sample = fixture()
                sample[name] = bad
                with self.assertRaisesRegex(MODULE.ObservationError, name):
                    MODULE.validate_report(sample)

    def test_count_bounds_mismatch_and_bad_delta_fail(self):
        changes = (
            ("sample_count", 99),
            ("sample_count", True),
            ("frame_intervals_ms", [10.0] * 59),
            ("frame_intervals_ms", [10.0] * 1501),
            ("frame_intervals_ms", [10.0] * 99 + [-1]),
            ("frame_intervals_ms", [10.0] * 99 + [math.inf]),
            ("frame_intervals_ms", [10.0] * 99 + [math.nan]),
            ("frame_intervals_ms", [10.0] * 99 + [True]),
            ("frame_intervals_ms", [10.0] * 99 + [1000.0]),
        )
        for name, bad in changes:
            with self.subTest(name=name, bad=str(bad)[:36]):
                sample = fixture()
                sample[name] = bad
                with self.assertRaises(MODULE.ObservationError):
                    MODULE.validate_report(sample)

    def test_fake_gpu_provenance_wrong_workload_and_units_fail(self):
        changes = (
            ("measurement", "GPU_TIME_MEASURED"),
            ("frame_intervals_units", "seconds"),
            ("proxy_count", 99999),
            ("proxy_count", True),
            ("proxy_count", []),
            ("proxy_count", {}),
            ("effect_mode", "unsafe"),
            ("effect_mode", []),
            ("effect_mode", {}),
            ("schema_version", "nex_frame_observation.v2"),
            ("godot", ""),
            ("warmup_seconds", 0),
            ("requested_seconds", 50.0),
        )
        for name, bad in changes:
            with self.subTest(name=name):
                sample = fixture()
                sample[name] = bad
                with self.assertRaises(MODULE.ObservationError):
                    MODULE.validate_report(sample)

    def test_duplicate_keys_nonfinite_raw_json_and_bad_encoding_fail(self):
        for content in (
            '{"schema_version": "a", "schema_version": "b"}',
            '{"sample_count": NaN}',
            '{"sample_count": 1e999}',
            "[]",
        ):
            with self.subTest(content=content):
                with self.assertRaises(MODULE.ObservationError):
                    MODULE.validate_payload(content.encode("utf-8"))
        with self.assertRaises(MODULE.ObservationError):
            MODULE.validate_payload(b"\xff")

    def test_input_size_cap_empty_and_no_user_controlled_file_open(self):
        with self.assertRaises(MODULE.ObservationError):
            MODULE.validate_payload(b"x" * (MODULE.MAX_BYTES + 1))
        with self.assertRaises(MODULE.ObservationError):
            MODULE.validate_payload(b"")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("source.read_text(", source)
        self.assertNotIn("source.stat(", source)
        self.assertNotIn('parser.add_argument("file"', source)

    def test_cli_valid_output_and_bad_exit_status(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = MODULE.main(json.dumps(fixture()).encode("utf-8"))
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PASS")
        output = io.StringIO()
        with redirect_stdout(output):
            result = MODULE.main(b'{"broken":true}')
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "FAIL")

    def test_raw_capture_version_requires_original_samples(self):
        sample = fixture()
        del sample["frame_intervals_ms"]
        with self.assertRaises(MODULE.ObservationError):
            MODULE.validate_report(sample)


if __name__ == "__main__":
    unittest.main()

import copy
import json
import unittest
from pathlib import Path

from nex_bench.telemetry.framepulse import FramePulseError, analyze_json, analyze_run


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "nex_bench"
    / "telemetry"
    / "fixtures"
    / "synthetic_run.v1.json"
)


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def make_run(frame_times):
    run = copy.deepcopy(load_fixture())
    run["sample_count"] = len(frame_times)
    run["samples"] = [
        {
            "timestamp_ms": index * 20.0,
            "frame_time_ms": frame_time,
        }
        for index, frame_time in enumerate(frame_times)
    ]
    return run


class FramePulseTests(unittest.TestCase):
    def test_fixture_is_synthetic_and_hardware_is_explicitly_unavailable(self):
        report = analyze_json(FIXTURE_PATH.read_text(encoding="utf-8"))

        self.assertEqual(report["classification"], "SYNTHETIC_NOT_MEASURED")
        self.assertEqual(report["provenance"]["execution_mode"], "synthetic")
        self.assertIn("synthetic", report["provenance"]["run_id"].lower())
        self.assertEqual(report["hardware"]["gpu"]["availability"], "UNAVAILABLE")
        self.assertEqual(report["hardware"]["vram"]["availability"], "UNAVAILABLE")
        self.assertNotIn("utilization_percent", report["hardware"]["gpu"])
        self.assertNotIn("used_bytes", report["hardware"]["vram"])
        self.assertGreater(report["sample_count"], 0)
        self.assertEqual(report["slow_frame_count"], 3)
        self.assertEqual(
            report["stutter_clusters"],
            [
                {"start_index": 30, "end_index": 31, "frame_count": 2},
                {"start_index": 80, "end_index": 80, "frame_count": 1},
            ],
        )

    def test_60_fps_and_120_fps_signals_remain_synthetic_targets(self):
        for target_fps in (60, 120):
            with self.subTest(target_fps=target_fps):
                frame_time = 1000.0 / target_fps
                report = analyze_run(make_run([frame_time] * target_fps))
                self.assertEqual(report["classification"], "SYNTHETIC_NOT_MEASURED")
                self.assertAlmostEqual(
                    report["quantiles_ms"]["p50"], frame_time, places=10
                )
                self.assertAlmostEqual(
                    report["synthetic_one_percent_low_fps"], target_fps, places=10
                )
                self.assertEqual(report["stutter_clusters"], [])

    def test_60_and_120_fps_signals_keep_injected_hitches_visible(self):
        for target_fps in (60, 120):
            with self.subTest(target_fps=target_fps):
                frame_time = 1000.0 / target_fps
                values = [frame_time] * 120
                values[40:42] = [45.0, 60.0]
                report = analyze_run(make_run(values))
                self.assertAlmostEqual(
                    report["quantiles_ms"]["p50"], frame_time, places=10
                )
                self.assertEqual(
                    report["stutter_clusters"],
                    [{"start_index": 40, "end_index": 41, "frame_count": 2}],
                )

    def test_quantiles_use_linear_interpolation_for_p50_p95_and_p99(self):
        report = analyze_run(make_run([1.0, 2.0, 3.0, 4.0]))

        self.assertEqual(
            report["quantiles_ms"],
            {"p50": 2.5, "p95": 3.8499999999999996, "p99": 3.9699999999999998},
        )

    def test_quantile_single_sample_boundary(self):
        report = analyze_run(make_run([8.0]))

        self.assertEqual(report["quantiles_ms"], {"p50": 8.0, "p95": 8.0, "p99": 8.0})
        self.assertEqual(report["synthetic_one_percent_sample_count"], 1)
        self.assertEqual(report["synthetic_one_percent_low_fps"], 125.0)

    def test_one_percent_low_uses_mean_of_slowest_ceil_percent(self):
        values = [float(value) for value in range(1, 101)]
        report = analyze_run(make_run(values))

        self.assertEqual(report["synthetic_one_percent_sample_count"], 1)
        self.assertAlmostEqual(report["synthetic_one_percent_low_fps"], 10.0)

        values = [float(value) for value in range(1, 102)]
        report = analyze_run(make_run(values))
        self.assertEqual(report["synthetic_one_percent_sample_count"], 2)
        self.assertAlmostEqual(report["synthetic_one_percent_low_fps"], 1000.0 / 100.5)

    def test_slow_frames_are_grouped_by_contiguous_indices_only(self):
        report = analyze_run(
            make_run([10.0, 35.0, 40.0, 11.0, 35.0, 35.0, 10.0]),
            slow_frame_threshold_ms=35.0,
        )

        self.assertEqual(report["slow_frame_count"], 4)
        self.assertEqual(
            report["stutter_clusters"],
            [
                {"start_index": 1, "end_index": 2, "frame_count": 2},
                {"start_index": 4, "end_index": 5, "frame_count": 2},
            ],
        )

    def test_slow_frame_threshold_must_be_positive_and_finite(self):
        for threshold in (0, -1, float("nan"), float("inf"), True, "20"):
            with self.subTest(threshold=threshold):
                with self.assertRaises(FramePulseError):
                    analyze_run(make_run([10.0]), slow_frame_threshold_ms=threshold)

    def test_parser_rejects_non_object_json(self):
        for text in ("", "[]", "null", '"not a run"'):
            with self.subTest(text=text):
                with self.assertRaises(FramePulseError):
                    analyze_json(text)

    def test_parser_rejects_duplicate_json_object_keys(self):
        text = FIXTURE_PATH.read_text(encoding="utf-8")
        duplicate = text.replace(
            '"schema_version": "telemetry_run.v1",',
            '"schema_version": "wrong",\n  "schema_version": "telemetry_run.v1",',
            1,
        )
        self.assertNotEqual(text, duplicate)
        with self.assertRaises(FramePulseError):
            analyze_json(duplicate)

    def test_parser_rejects_nan_infinity_and_exponent_overflow(self):
        run = make_run([10.0])
        valid = json.dumps(run)
        needle = '"frame_time_ms": 10.0'
        self.assertIn(needle, valid)
        for token in ("NaN", "Infinity", "-Infinity", "1e9999", "-1e9999"):
            with self.subTest(token=token):
                payload = valid.replace(needle, '"frame_time_ms": ' + token, 1)
                with self.assertRaises(FramePulseError):
                    analyze_json(payload)

    def test_runtime_validator_rejects_non_finite_python_numbers(self):
        for invalid in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(invalid=invalid):
                with self.assertRaises(FramePulseError):
                    analyze_run(make_run([invalid]))

    def test_missing_required_metadata_is_rejected(self):
        for field in ("run_id", "git_sha", "scene_id", "scene_sha256", "toolchain"):
            with self.subTest(field=field):
                run = load_fixture()
                del run[field]
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_extra_fields_are_rejected_by_minimal_contract_validation(self):
        run = load_fixture()
        run["unreviewed_field"] = "not part of telemetry_run.v1"
        with self.assertRaises(FramePulseError):
            analyze_run(run)

    def test_wrong_schema_and_execution_versions_are_rejected(self):
        for field, value in (
            ("schema_version", "telemetry_run.v2"),
            ("execution_mode", "editor"),
        ):
            with self.subTest(field=field):
                run = load_fixture()
                run[field] = value
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_wrong_hash_formats_are_rejected(self):
        for field, value in (
            ("git_sha", "not-a-commit"),
            ("git_sha", "A" * 40),
            ("git_sha", "a" * 39),
            ("scene_sha256", "0" * 63),
            ("scene_sha256", "g" * 64),
        ):
            with self.subTest(field=field, value=value):
                run = load_fixture()
                run[field] = value
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_wrong_ids_and_renderer_are_rejected(self):
        for field, value in (
            ("run_id", ""),
            ("run_id", "contains spaces"),
            ("scene_id", "Uppercase.Scene"),
            ("renderer_id", "unknown.renderer"),
            ("renderer_id", []),
        ):
            with self.subTest(field=field, value=value):
                run = load_fixture()
                run[field] = value
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_wrong_clock_or_frame_time_units_are_rejected(self):
        run = load_fixture()
        run["clock"]["domain"] = "wall"
        with self.assertRaises(FramePulseError):
            analyze_run(run)

        run = load_fixture()
        run["clock"]["timestamp_unit"] = "seconds"
        with self.assertRaises(FramePulseError):
            analyze_run(run)

        run = load_fixture()
        run["frame_time_unit"] = "seconds"
        with self.assertRaises(FramePulseError):
            analyze_run(run)

    def test_bad_sample_count_and_warmup_count_are_rejected(self):
        for field, value in (
            ("sample_count", 0),
            ("sample_count", 99),
            ("sample_count", True),
            ("warmup_count", -1),
            ("warmup_count", 1.5),
            ("warmup_count", True),
        ):
            with self.subTest(field=field, value=value):
                run = load_fixture()
                run[field] = value
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_empty_samples_and_malformed_sample_objects_are_rejected(self):
        for samples in ([], [None], ["10ms"], [{"timestamp_ms": 1.0}]):
            with self.subTest(samples=samples):
                run = load_fixture()
                run["samples"] = samples
                run["sample_count"] = len(samples)
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_tied_and_reversed_timestamps_are_rejected(self):
        for timestamps in ((0.0, 0.0), (10.0, 9.0)):
            with self.subTest(timestamps=timestamps):
                run = make_run([10.0, 11.0])
                run["samples"][0]["timestamp_ms"] = timestamps[0]
                run["samples"][1]["timestamp_ms"] = timestamps[1]
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_zero_negative_and_over_limit_frame_times_are_rejected(self):
        for value in (0, -0.1, 60000.1, True, "16.67"):
            with self.subTest(value=value):
                with self.assertRaises(FramePulseError):
                    analyze_run(make_run([value]))

    def test_unbounded_integer_samples_raise_validation_errors(self):
        run = make_run([10.0])
        run["samples"][0]["timestamp_ms"] = 10**1000
        with self.assertRaises(FramePulseError):
            analyze_run(run)

        with self.assertRaises(FramePulseError):
            analyze_run(make_run([10.0]), slow_frame_threshold_ms=10**1000)

    def test_invalid_timestamps_are_rejected(self):
        for value in (-1, 1e15 + 1, False, "12"):
            with self.subTest(value=value):
                run = make_run([10.0])
                run["samples"][0]["timestamp_ms"] = value
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_unavailable_hardware_cannot_carry_numeric_measurements(self):
        for field, measurement in (
            ("gpu", "utilization_percent"),
            ("vram", "used_bytes"),
        ):
            with self.subTest(field=field):
                run = load_fixture()
                run[field][measurement] = 0
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_available_numeric_zero_is_distinct_from_unavailable(self):
        run = load_fixture()
        run["gpu"] = {
            "availability": "AVAILABLE",
            "source": "synthetic test sentinel; not a hardware sample",
            "utilization_percent": 0,
        }
        run["vram"] = {
            "availability": "AVAILABLE",
            "source": "synthetic test sentinel; not a hardware sample",
            "used_bytes": 0,
        }
        report = analyze_run(run)

        self.assertEqual(report["hardware"]["gpu"]["availability"], "AVAILABLE")
        self.assertEqual(report["hardware"]["gpu"]["utilization_percent"], 0)
        self.assertEqual(report["hardware"]["vram"]["availability"], "AVAILABLE")
        self.assertEqual(report["hardware"]["vram"]["used_bytes"], 0)

    def test_invalid_hardware_availability_and_missing_sources_are_rejected(self):
        for field in ("gpu", "vram"):
            with self.subTest(field=field):
                run = load_fixture()
                run[field]["availability"] = "UNKNOWN"
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

                run = load_fixture()
                del run[field]["source"]
                with self.assertRaises(FramePulseError):
                    analyze_run(run)

    def test_invalid_available_hardware_values_are_rejected(self):
        run = load_fixture()
        run["gpu"] = {
            "availability": "AVAILABLE",
            "source": "test sentinel",
            "utilization_percent": 100.1,
        }
        with self.assertRaises(FramePulseError):
            analyze_run(run)

        run = load_fixture()
        run["vram"] = {
            "availability": "AVAILABLE",
            "source": "test sentinel",
            "used_bytes": -1,
        }
        with self.assertRaises(FramePulseError):
            analyze_run(run)


if __name__ == "__main__":
    unittest.main()

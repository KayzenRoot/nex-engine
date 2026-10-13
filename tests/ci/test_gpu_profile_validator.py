"""Negative and arithmetic tests for the offline GPU profile validator.

Fixtures here are deliberately synthetic validation inputs. They are never
stored as local GPU performance evidence or described as hardware results.
"""
from __future__ import annotations

import importlib.util
import io
import json
import math
from pathlib import Path
import unittest
from contextlib import redirect_stdout


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "nex_bench" / "gpu_profile" / "validate_gpu_profile.py"
SPEC = importlib.util.spec_from_file_location("nex_gpu_profile_validator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def percentiles(samples):
    ordered = sorted(samples)
    return {
        "mean": math.fsum(ordered) / len(ordered),
        "p50": ordered[math.ceil(0.50 * len(ordered)) - 1],
        "p95": ordered[math.ceil(0.95 * len(ordered)) - 1],
        "p99": ordered[math.ceil(0.99 * len(ordered)) - 1],
    }


def series(unit, provider, samples, status="MEASURED", invalid=0, reason=""):
    aggregates = percentiles(samples) if status == "MEASURED" else None
    return {
        "status": status,
        "unit": unit,
        "provider": provider,
        "samples": samples,
        "valid_sample_count": len(samples),
        "invalid_sample_count": invalid,
        "aggregates": aggregates,
        "unavailable_reason": reason,
    }


def fixture():
    main_loop = [99.0] * 150 + [101.0] * 150
    slowest = sorted(main_loop)[-math.ceil(0.01 * len(main_loop)):]
    device = {
        "status": "UNAVAILABLE",
        "provider": "nvidia-smi --query-gpu (device-wide; never process-attributed under WDDM)",
        "scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
        "samples": [],
        "unavailable_reason": "No device snapshot was requested in this synthetic validator fixture.",
    }

    return {
        "schema_version": "nex_gpu_render_profile.v1",
        "run_id": "1791841414-1791841414000000",
        "run_status": "COMPLETE",
        "run_reason": "requested_observation_window_elapsed",
        "captured_at_utc": "2026-10-13T02:00:00Z",
        "source_sha": "a" * 40,
        "godot_version": "4.7.2.stable.official.ed1daf0bf",
        "os": "Windows",
        "display": "windows",
        "renderer": "forward_plus",
        "driver": "vulkan",
        "adapter": "NVIDIA GeForce RTX 5050",
        "viewport": {"rid": "RID(1234)", "resolution_px": [1920, 1080]},
        "workload": {
            "scene": "Density Ladder",
            "proxy_count": 25,
            "effect_mode": "geometry",
            "layout": "built-in deterministic grid",
        },
        "settings": {"vsync_mode": 1, "max_fps": 0},
        "measurement": {
            "provider": "Godot RenderingServer per-viewport render timing",
            "warmup_seconds": 2.0,
            "requested_seconds": 30.0,
            "observed_seconds": 30.0,
            "warmup_frames_discarded": 120,
            "invalid_main_loop_samples": 0,
            "percentile_method": "nearest_rank",
            "formula_version": "nex-percentile-and-one-percent-low-v1",
            "one_percent_low_fps_formula": "1000 / mean(slowest ceil(0.01*n) positive MAIN_LOOP_INTERVAL_MS samples)",
            "one_percent_low_fps": 1000.0 / (math.fsum(slowest) / len(slowest)),
            "temporal_alignment_note": "Synthetic validator fixture; no actual GPU run is represented.",
        },
        "series": {
            "GPU_RENDER_MS": series(
                "ms", "RenderingServer.viewport_get_measured_render_time_gpu", [2.5] * 300
            ),
            "CPU_RENDER_MS": series(
                "ms", "RenderingServer.viewport_get_measured_render_time_cpu", [1.5] * 300
            ),
            "MAIN_LOOP_INTERVAL_MS": series(
                "ms", "SceneTree._process(delta)", main_loop
            ),
            "RENDERER_ALLOCATION_BYTES": series(
                "bytes", "Performance.RENDER_VIDEO_MEM_USED", [800_000_000.0] * 300
            ),
        },
        "device_snapshot": device,
    }


def fixture_v2():
    document = fixture()
    document["schema_version"] = "nex_gpu_render_profile.v2"
    measurement = document["measurement"]
    measurement.update({
        "formula_version": "nex-percentile-and-one-percent-low-monotonic-v2",
        "one_percent_low_fps_formula": "1000 / mean(slowest ceil(0.01*n) positive FRAME_PACING_INTERVAL_MS samples)",
        "one_percent_low_fps_source": "FRAME_PACING_INTERVAL_MS",
        "frame_pacing_provider": "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback",
        "frame_pacing_status": "MEASURED",
        "frame_pacing_unavailable_reason": "",
        "invalid_frame_pacing_samples": 0,
        "delta_derived_one_percent_low_fps_label": "DELTA_DERIVED_VSYNC_LIMITED",
        "delta_derived_one_percent_low_fps": 1000.0 / 101.0,
        "frame_pacing_limitation": "Callback pacing only; not display presentation or input-to-photon latency.",
    })
    # 299 normal 99 ms intervals and one simulated 399 ms hitch cover exactly
    # 30 seconds. The slowest 1% calculation must include that actual hitch.
    pacing = [99.0] * 299 + [399.0]
    measurement["observed_seconds"] = math.fsum(pacing) / 1000.0
    slowest = sorted(pacing)[-math.ceil(0.01 * len(pacing)):]
    measurement["one_percent_low_fps"] = 1000.0 / (math.fsum(slowest) / len(slowest))
    document["series"]["FRAME_PACING_INTERVAL_MS"] = series(
        "ms",
        "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback",
        pacing,
    )
    return document


class GPUProfileValidatorTests(unittest.TestCase):
    def test_recalculates_nearest_rank_aggregates_and_main_loop_one_percent_low(self):
        report = MODULE.validate_report(fixture())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["observed_seconds"], 30.0)
        self.assertAlmostEqual(report["one_percent_low_fps"], 1000.0 / 101.0)
        self.assertEqual(report["series"]["GPU_RENDER_MS"]["valid_sample_count"], 300)
        self.assertEqual(report["series"]["GPU_RENDER_MS"]["aggregates"]["p99"], 2.5)

    def test_v2_uses_monotonic_callback_intervals_for_1_percent_low(self):
        document = fixture_v2()
        report = MODULE.validate_report(document)
        self.assertEqual(report["schema_version"], "nex_gpu_render_profile.v2")
        self.assertAlmostEqual(report["one_percent_low_fps"], 1000.0 / 199.0)
        self.assertNotAlmostEqual(report["one_percent_low_fps"], document["measurement"]["delta_derived_one_percent_low_fps"])
        self.assertEqual(report["series"]["FRAME_PACING_INTERVAL_MS"]["valid_sample_count"], 300)

    def test_v2_rejects_zero_and_rollback_intervals(self):
        for bad_interval in (0.0, -1.0):
            with self.subTest(bad_interval=bad_interval):
                document = fixture_v2()
                document["series"]["FRAME_PACING_INTERVAL_MS"]["samples"][0] = bad_interval
                document["series"]["FRAME_PACING_INTERVAL_MS"]["aggregates"] = percentiles(
                    document["series"]["FRAME_PACING_INTERVAL_MS"]["samples"]
                )
                with self.assertRaises(MODULE.ProfileError):
                    MODULE.validate_report(document)

    def test_v2_unavailable_monotonic_clock_cannot_claim_1_percent_low_or_complete(self):
        document = fixture_v2()
        document["run_status"] = "INVALID"
        document["run_reason"] = "invalid_monotonic_tick"
        document["measurement"].update({
            "observed_seconds": 0.001,
            "frame_pacing_status": "UNAVAILABLE",
            "frame_pacing_unavailable_reason": "monotonic_clock_tick_zero_or_rollback",
            "invalid_frame_pacing_samples": 1,
            "one_percent_low_fps": None,
        })
        document["series"]["FRAME_PACING_INTERVAL_MS"] = series(
            "ms",
            "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback",
            [1.0],
            status="UNAVAILABLE",
            invalid=1,
            reason="monotonic_clock_tick_zero_or_rollback",
        )
        self.assertEqual(MODULE.validate_report(document)["run_status"], "INVALID")
        document["run_status"] = "COMPLETE"
        document["run_reason"] = "requested_observation_window_elapsed"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_v2_cancellation_cannot_be_serialized_as_complete(self):
        document = fixture_v2()
        document["run_status"] = "COMPLETE"
        document["run_reason"] = "user_cancelled"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)


    def test_v2_invalid_observed_seconds_rejects_invalid_values(self):
        for bad in (-0.1, 30.101, float("nan"), float("inf"), True, "0", 10 ** 1000):
            with self.subTest(value=str(bad)[:36]):
                document = fixture_v2()
                document["run_status"] = "INVALID"
                document["run_reason"] = "insufficient_frame_pacing_samples"
                document["measurement"]["observed_seconds"] = bad
                with self.assertRaisesRegex(MODULE.ProfileError, "measurement.observed_seconds"):
                    MODULE.validate_report(document)

    def test_v2_invalid_run_with_zero_observation_is_preserved(self):
        document = fixture_v2()
        document["run_status"] = "INVALID"
        document["run_reason"] = "insufficient_frame_pacing_samples"
        document["measurement"].update({
            "observed_seconds": 0.0,
            "frame_pacing_status": "UNAVAILABLE",
            "frame_pacing_unavailable_reason": "no_callback_interval_collected",
            "one_percent_low_fps": None,
        })
        document["series"]["FRAME_PACING_INTERVAL_MS"] = series(
            "ms",
            "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback",
            [],
            status="UNAVAILABLE",
            reason="no_callback_interval_collected",
        )
        result = MODULE.validate_report(document)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["run_status"], "INVALID")
        self.assertIsNone(result["one_percent_low_fps"])

    def test_v2_split_guards_reject_pacing_and_duration_spoofing(self):
        corruptions = (
            ("frame_pacing_provider", "forged callback provider"),
            ("one_percent_low_fps_source", "MAIN_LOOP_INTERVAL_MS"),
            ("frame_pacing_status", "UNAVAILABLE"),
            ("invalid_frame_pacing_samples", 1),
            ("delta_derived_one_percent_low_fps_label", "MEASURED"),
            ("delta_derived_one_percent_low_fps", None),
            ("frame_pacing_limitation", ""),
            ("observed_seconds", 29.0),
        )
        for key, value in corruptions:
            with self.subTest(field=key):
                document = fixture_v2()
                document["measurement"][key] = value
                with self.assertRaises(MODULE.ProfileError):
                    MODULE.validate_report(document)

    def test_historical_v1_gpu_profiles_remain_readable(self):
        evidence = ROOT / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-10-13-final-head"
        captures = sorted(path for path in evidence.glob("gpu_profile_*.json") if not path.name.endswith(".validation.json"))
        self.assertEqual(len(captures), 12)
        for capture in captures:
            with self.subTest(capture=capture.name):
                result = MODULE.validate_payload(capture.read_bytes())
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["schema_version"], "nex_gpu_render_profile.v1")

    def test_v2_partial_resize_run_is_invalid_not_a_complete_benchmark(self):
        # Synthetic validator fixture for the R3 fail-closed resize path.
        # Real Windows GUI/RTX5050 evidence remains a separate requirement.
        document = fixture_v2()
        document["run_status"] = "INVALID"
        document["run_reason"] = "viewport_changed_or_unavailable"
        document["measurement"].update({
            "observed_seconds": 9.9,
            "frame_pacing_status": "UNAVAILABLE",
            "frame_pacing_unavailable_reason": "viewport_resized_during_capture",
            "one_percent_low_fps": None,
        })
        document["series"]["FRAME_PACING_INTERVAL_MS"] = series(
            "ms",
            "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback",
            [99.0] * 100,
            status="UNAVAILABLE",
            reason="viewport_resized_during_capture",
        )
        result = MODULE.validate_report(document)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["run_status"], "INVALID")
        self.assertIsNone(result["one_percent_low_fps"])
        document["run_status"] = "COMPLETE"
        document["run_reason"] = "requested_observation_window_elapsed"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_six_real_v2_frame_pacing_captures_remain_valid(self):
        # Archived R1 hardware evidence: guard against future v1/v2
        # validator regressions, not a claim the current R3 code was retested.
        evidence = (
            ROOT / "nex_bench" / "gpu_profile" / "evidence"
            / "windows-rtx5050-2026-10-13-frame-pacing-correction"
        )
        expected_one_percent_low = {
            "1791883867-295809379": (200, "geometry", 2250, 66.866880),
            "1791883979-407576457": (200, "geometry", 2250, 71.246914),
            "1791884017-445689369": (200, "geometry", 2249, 68.236907),
            "1791884095-523815570": (25, "combined", 2250, 68.335438),
            "1791884133-561569147": (25, "combined", 2250, 68.928521),
            "1791884170-598874419": (25, "combined", 2250, 69.359002),
        }
        captures = sorted(
            path for path in evidence.glob("gpu_profile_*.json")
            if not path.name.endswith(".validation.json")
        )
        self.assertEqual({path.stem.removeprefix("gpu_profile_") for path in captures},
                         set(expected_one_percent_low))
        self.assertEqual(len(captures), 6)
        for capture in captures:
            with self.subTest(capture=capture.name):
                result = MODULE.validate_payload(capture.read_bytes())
                run_id = capture.stem.removeprefix("gpu_profile_")
                count, effect, samples, low = expected_one_percent_low[run_id]
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["run_status"], "COMPLETE")
                self.assertEqual(result["schema_version"], MODULE.SCHEMA_VERSION)
                self.assertEqual(
                    result["source_sha"],
                    "179ede475fa8ef13bbaaeb9af3e37caf373e0d51",
                )
                self.assertEqual(result["workload"],
                                 {"proxy_count": count, "effect_mode": effect})
                self.assertEqual(
                    result["series"]["FRAME_PACING_INTERVAL_MS"]["status"],
                    "MEASURED",
                )
                self.assertEqual(
                    result["series"]["FRAME_PACING_INTERVAL_MS"]["valid_sample_count"],
                    samples,
                )
                self.assertAlmostEqual(result["one_percent_low_fps"], low, places=5)
                self.assertGreaterEqual(result["observed_seconds"], 30.0)
                self.assertLessEqual(result["observed_seconds"], 30.1)

    def test_real_v2_pacing_aggregate_tampering_fails_closed(self):
        # Static repository path only; no user-provided path or GPU operation.
        capture = (
            ROOT / "nex_bench" / "gpu_profile" / "evidence"
            / "windows-rtx5050-2026-10-13-frame-pacing-correction"
            / "gpu_profile_1791883867-295809379.json"
        )
        document = json.loads(capture.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.validate_report(document)["status"], "PASS")
        document["measurement"]["one_percent_low_fps"] += 5.0
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_unavailable_gpu_is_explicit_and_keeps_no_synthetic_zero_samples(self):
        document = fixture()
        document["series"]["GPU_RENDER_MS"] = series(
            "ms", "RenderingServer.viewport_get_measured_render_time_gpu", [],
            status="UNAVAILABLE", invalid=300, reason="headless_rendering_has_no_gpu_timing",
        )
        result = MODULE.validate_report(document)
        self.assertEqual(result["series"]["GPU_RENDER_MS"]["status"], "UNAVAILABLE")
        self.assertEqual(result["series"]["GPU_RENDER_MS"]["valid_sample_count"], 0)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_payload(b'{"schema_version":"nex_gpu_render_profile.v1","schema_version":"spoof"}')

    def test_run_id_digits_are_ascii_only(self):
        document = fixture()
        document["run_id"] = "١791841414-1791841414000000"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_nonfinite_constants_and_values_are_rejected(self):
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_payload(b'{"value":NaN}')
        document = fixture()
        document["series"]["GPU_RENDER_MS"]["samples"][0] = float("inf")
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_zero_gpu_timing_cannot_claim_measured(self):
        document = fixture()
        document["series"]["GPU_RENDER_MS"]["samples"] = [0.0] * 300
        document["series"]["GPU_RENDER_MS"]["aggregates"] = {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_unavailable_gpu_cannot_substitute_zero_sample(self):
        document = fixture()
        document["series"]["GPU_RENDER_MS"] = series(
            "ms", "RenderingServer.viewport_get_measured_render_time_gpu", [0.0],
            status="UNAVAILABLE", invalid=299, reason="gpu_timing_unavailable",
        )
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_measured_status_cannot_hide_too_few_samples(self):
        document = fixture()
        document["series"]["CPU_RENDER_MS"] = series(
            "ms", "RenderingServer.viewport_get_measured_render_time_cpu", [1.0] * 299
        )
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_unavailable_status_cannot_hide_enough_valid_samples(self):
        document = fixture()
        document["series"]["GPU_RENDER_MS"] = series(
            "ms", "RenderingServer.viewport_get_measured_render_time_gpu", [2.5] * 300,
            status="UNAVAILABLE", reason="spoofed_unavailable",
        )
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_missing_metadata_and_unknown_fields_fail_closed(self):
        document = fixture()
        del document["source_sha"]
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)
        document = fixture()
        document["unexpected"] = True
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_inconsistent_aggregate_count_and_duration_are_rejected(self):
        document = fixture()
        document["series"]["GPU_RENDER_MS"]["aggregates"]["p95"] += 1.0
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)
        document = fixture()
        document["series"]["MAIN_LOOP_INTERVAL_MS"]["valid_sample_count"] += 1
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)
        document = fixture()
        document["measurement"]["observed_seconds"] = 29.0
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_locked_durations_use_explicit_float_representation_tolerance(self):
        document = fixture()
        document["measurement"]["warmup_seconds"] = 2.0 - 5e-10
        document["measurement"]["requested_seconds"] = 30.0 - 5e-10
        self.assertEqual(MODULE.validate_report(document)["status"], "PASS")
        document["measurement"]["warmup_seconds"] = 1.999
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_main_loop_formula_is_not_conflated_with_gpu_series(self):
        document = fixture()
        document["measurement"]["one_percent_low_fps"] = 1000.0 / 2.5
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_device_snapshot_cannot_claim_process_vram_or_spoof_status(self):
        document = fixture()
        document["device_snapshot"]["scope"] = "GODOT_PROCESS_MEMORY"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)
        document = fixture()
        document["device_snapshot"]["status"] = "PASS"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)
        document = fixture()
        document["device_snapshot"]["samples"] = [
            {
                "status": "MEASURED",
                "provider": "nvidia-smi",
                "scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
                "captured_at_utc": "2026-10-13T02:00:00Z",
                "exit_code": 0.0,
                "raw_csv": "NVIDIA GeForce RTX 5050, 617.14, 8151 MiB, P3, 7 %, 1592 MiB, 1000, 2000",
                "unavailable_reason": "",
            }
        ]
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_renderer_allocation_is_not_device_vram(self):
        document = fixture()
        document["series"]["RENDERER_ALLOCATION_BYTES"]["provider"] = "NVIDIA process VRAM"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_invalid_run_cannot_claim_collection_complete(self):
        document = fixture()
        document["run_status"] = "INVALID"
        document["run_reason"] = "not_an_authorized_stop_reason"
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)

    def test_sample_and_payload_bounds(self):
        document = fixture()
        document["series"]["MAIN_LOOP_INTERVAL_MS"]["samples"] = [10.0] * (MODULE.MAX_SAMPLES + 1)
        document["series"]["MAIN_LOOP_INTERVAL_MS"]["valid_sample_count"] = MODULE.MAX_SAMPLES + 1
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_report(document)
        with self.assertRaises(MODULE.ProfileError):
            MODULE.validate_payload(b" " * (MODULE.MAX_BYTES + 1))

    def test_cli_reports_pass_and_fail_exit_codes(self):
        with redirect_stdout(io.StringIO()):
            output = MODULE.main(json.dumps(fixture(), allow_nan=False).encode("utf-8"))
        self.assertEqual(output, 0)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(MODULE.main(b'{"bad":true}'), 1)

    def test_hub_wiring_is_opt_in_and_preserves_f10_schema(self):
        hub = (ROOT / "nex_bench" / "hub.gd").read_text(encoding="utf-8")
        session = (ROOT / "nex_bench" / "gpu_profile" / "session.gd").read_text(encoding="utf-8")
        smoke = (ROOT / "nex_bench" / "smoke.gd").read_text(encoding="utf-8")
        self.assertIn("KEY_F11", hub)
        self.assertIn("KEY_F12", hub)
        self.assertIn("func _toggle_gpu_profile()", hub)
        self.assertIn("func _capture_gpu_profile_screenshot()", hub)
        self.assertIn("nex_frame_observation.v1", hub)
        self.assertIn("nex_gpu_render_profile.v2", session)
        validator = (ROOT / "nex_bench" / "gpu_profile" / "validate_gpu_profile.py").read_text(encoding="utf-8")
        self.assertIn("nex_gpu_render_profile.v1", validator)
        self.assertIn("FRAME_PACING_INTERVAL_MS", session)
        self.assertIn("Time.get_ticks_usec()", session)
        self.assertIn("RenderingServer.viewport_set_measure_render_time(viewport_rid, true)", session)
        self.assertIn("RenderingServer.viewport_set_measure_render_time(viewport_rid, false)", session)
        self.assertIn('Time.get_datetime_string_from_system(true, false) + "Z"', session)
        self.assertIn("NEX_NATIVE_GPU_PROFILE_PASS", smoke)
        self.assertNotIn("RenderingServer.viewport_set_measure_render_time", hub)

    def test_readme_does_not_conflate_v2_pacing_with_v1_delta(self):
        readme = (ROOT / "nex_bench" / "README.md").read_text(encoding="utf-8")
        self.assertIn("**No schema v2**", readme)
        self.assertIn("**No schema histórico v1**", readme)
        self.assertIn("`FRAME_PACING_INTERVAL_MS`", readme)
        self.assertIn("`MAIN_LOOP_INTERVAL_MS`", readme)
        self.assertIn("`DELTA_DERIVED_VSYNC_LIMITED`", readme)
        self.assertIn("não são intercambiáveis", readme)
        self.assertNotIn("1% low somente da série `MAIN_LOOP_INTERVAL_MS`", readme)
        self.assertIn("INVALID / viewport_changed_or_unavailable", readme)
        self.assertIn("uma captura negativa real", readme)

    def test_profiler_status_never_displays_absolute_output_paths(self):
        hub = (ROOT / "nex_bench" / "hub.gd").read_text(encoding="utf-8")
        self.assertIn("var display_name := output_path.get_file()", hub)
        self.assertIn("int(cpu.get(\"valid_sample_count\", 0)), display_name", hub)
        self.assertIn("str(document.get(\"run_status\", \"INVALID\")), display_name", hub)
        self.assertIn('"GPU profiler HUD screenshot saved: %s" % filename', hub)


if __name__ == "__main__":
    unittest.main()

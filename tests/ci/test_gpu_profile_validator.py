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


class GPUProfileValidatorTests(unittest.TestCase):
    def test_recalculates_nearest_rank_aggregates_and_main_loop_one_percent_low(self):
        report = MODULE.validate_report(fixture())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["observed_seconds"], 30.0)
        self.assertAlmostEqual(report["one_percent_low_fps"], 1000.0 / 101.0)
        self.assertEqual(report["series"]["GPU_RENDER_MS"]["valid_sample_count"], 300)
        self.assertEqual(report["series"]["GPU_RENDER_MS"]["aggregates"]["p99"], 2.5)

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
        self.assertIn("nex_gpu_render_profile.v1", session)
        self.assertIn("RenderingServer.viewport_set_measure_render_time(viewport_rid, true)", session)
        self.assertIn("RenderingServer.viewport_set_measure_render_time(viewport_rid, false)", session)
        self.assertIn('Time.get_datetime_string_from_system(true, false) + "Z"', session)
        self.assertIn("NEX_NATIVE_GPU_PROFILE_PASS", smoke)
        self.assertNotIn("RenderingServer.viewport_set_measure_render_time", hub)

    def test_profiler_status_never_displays_absolute_output_paths(self):
        hub = (ROOT / "nex_bench" / "hub.gd").read_text(encoding="utf-8")
        self.assertIn("var display_name := output_path.get_file()", hub)
        self.assertIn("int(cpu.get(\"valid_sample_count\", 0)), display_name", hub)
        self.assertIn("str(document.get(\"run_status\", \"INVALID\")), display_name", hub)
        self.assertIn('"GPU profiler HUD screenshot saved: %s" % filename', hub)


if __name__ == "__main__":
    unittest.main()

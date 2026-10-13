"""Regression tests for the stdin-only, read-only v2 repeatability helper.

All sample values in this file are SYNTHETIC. They are not new GPU runs.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
import io
import json
import unittest

from nex_bench.gpu_profile import summarize_profiles as SUMMARY
from test_gpu_profile_validator import fixture_v2, series


def repeated_batch(count: int = 3) -> dict:
    captures = []
    for i in range(count):
        capture = fixture_v2()
        capture["run_id"] = f"1791841414-{1791841414000000 + i}"
        captures.append(capture)
    return {"captures": captures}


def encoded(batch: dict) -> bytes:
    return json.dumps(batch, allow_nan=False).encode("utf-8")


class GPUProfileRepeatabilityTests(unittest.TestCase):
    def test_three_consistent_v2_captures_produce_read_only_summary(self):
        result = SUMMARY.validate_batch_payload(encoded(repeated_batch()))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["schema_version"], "nex_gpu_repeatability.v1")
        self.assertEqual(result["repeat_count"], 3)
        self.assertEqual(result["environment_status"], "NVIDIA_DRIVER_VERSION_UNVERIFIED")
        self.assertAlmostEqual(result["cpu_callback_one_percent_low_fps"]["mean_of_run_metrics"], 1000 / 199)
        self.assertEqual(result["gpu_render_p95_ms"]["mean_of_run_metrics"], 2.5)
        self.assertEqual(result["cpu_render_p95_ms"]["mean_of_run_metrics"], 1.5)
        self.assertEqual(result["renderer_allocation_p95_bytes"]["mean_of_run_metrics"], 800000000)
        self.assertIn("No cross-workload", " ".join(result["limitations"]))

    def test_mixed_environment_source_workload_resolution_and_driver_fail(self):
        mutations = (
            ("source_sha", lambda d: d.update({"source_sha": "b" * 40})),
            ("resolution", lambda d: d["viewport"].update({"resolution_px": [1280, 720]})),
            ("workload", lambda d: d["workload"].update({"effect_mode": "combined"})),
            ("vsync", lambda d: d["settings"].update({"vsync_mode": 0})),
            ("driver", lambda d: d.update({"driver": "other_backend"})),
            ("adapter", lambda d: d.update({"adapter": "another_device"})),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                batch = repeated_batch()
                mutate(batch["captures"][2])
                with self.assertRaisesRegex(SUMMARY.ProfileError, "mixed capture context"):
                    SUMMARY.summarize(batch)

    def test_distinct_driver_version_from_nvidia_snapshot_is_rejected(self):
        batch = repeated_batch()
        for i, document in enumerate(batch["captures"]):
            snapshot = {
                "status": "MEASURED",
                "provider": "nvidia-smi",
                "scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
                "captured_at_utc": "2026-10-13T02:00:00Z",
                "exit_code": 0,
                "raw_csv": f"NVIDIA RTX, {'617.14' if i < 2 else '618.00'}, 8151 MiB, 1300 MiB, 5 %, 1900 MHz, 42 C, 60 W",
                "unavailable_reason": "",
            }
            document["device_snapshot"].update({
                "status": "MEASURED",
                "samples": [snapshot],
                "unavailable_reason": "",
            })
        with self.assertRaisesRegex(SUMMARY.ProfileError, "mixed capture context"):
            SUMMARY.summarize(batch)

    def test_duplicate_run_id_incomplete_run_and_legacy_schema_fail(self):
        batch = repeated_batch()
        batch["captures"][2]["run_id"] = batch["captures"][0]["run_id"]
        with self.assertRaisesRegex(SUMMARY.ProfileError, "duplicate run_id"):
            SUMMARY.summarize(batch)
        batch = repeated_batch()
        batch["captures"][2]["run_status"] = "INVALID"
        batch["captures"][2]["run_reason"] = "viewport_changed_or_unavailable"
        with self.assertRaisesRegex(SUMMARY.ProfileError, "COMPLETE v2"):
            SUMMARY.summarize(batch)
        batch = repeated_batch()
        batch["captures"][2]["schema_version"] = "nex_gpu_render_profile.v1"
        with self.assertRaises(SUMMARY.ProfileError):
            SUMMARY.summarize(batch)

    def test_missing_gpu_series_never_averaged_as_measured_zero(self):
        batch = repeated_batch()
        batch["captures"][2]["series"]["GPU_RENDER_MS"] = series(
            "ms", "RenderingServer.viewport_get_measured_render_time_gpu",
            [], status="UNAVAILABLE", reason="headless_no_gpu",
        )
        result = SUMMARY.summarize(batch)
        self.assertEqual(result["gpu_render_p95_ms"]["status"], "INCONCLUSIVE")
        self.assertEqual(result["gpu_render_p95_ms"]["per_run"][-1], None)
        self.assertEqual(result["cpu_render_p95_ms"]["status"], "MEASURED")

    def test_bad_aggregate_and_nonfinite_inputs_fail_closed(self):
        batch = repeated_batch()
        batch["captures"][0]["series"]["CPU_RENDER_MS"]["aggregates"]["p95"] = 999
        with self.assertRaises(SUMMARY.ProfileError):
            SUMMARY.summarize(batch)
        with self.assertRaisesRegex(SUMMARY.ProfileError, "non-JSON number"):
            SUMMARY.validate_batch_payload(b'{"captures":[NaN]}')
        with self.assertRaisesRegex(SUMMARY.ProfileError, "duplicate JSON key"):
            SUMMARY.validate_batch_payload(b'{"captures":[],"captures":[]}')
        with self.assertRaisesRegex(SUMMARY.ProfileError, "48 MB"):
            SUMMARY.validate_batch_payload(b" " * (SUMMARY.MAX_BATCH_BYTES + 1))

    def test_batch_bounds_and_no_mixed_context_silent_grouping(self):
        with self.assertRaisesRegex(SUMMARY.ProfileError, "3 to 12"):
            SUMMARY.summarize(repeated_batch(2))
        with self.assertRaisesRegex(SUMMARY.ProfileError, "3 to 12"):
            SUMMARY.summarize(repeated_batch(13))
        batch = repeated_batch(6)
        for capture in batch["captures"][3:]:
            capture["workload"]["effect_mode"] = "combined"
        with self.assertRaisesRegex(SUMMARY.ProfileError, "mixed capture context"):
            SUMMARY.summarize(batch)

    def test_cli_outputs_json_without_side_effects(self):
        payload = encoded(repeated_batch())
        with redirect_stdout(io.StringIO()) as output:
            code = SUMMARY.main(payload)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PASS")
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(SUMMARY.main(b"{invalid"), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "FAIL")

    def test_unchanged_raw_documents_are_not_modified(self):
        batch = repeated_batch()
        prior = copy.deepcopy(batch)
        SUMMARY.summarize(batch)
        self.assertEqual(batch, prior)


if __name__ == "__main__":
    unittest.main()

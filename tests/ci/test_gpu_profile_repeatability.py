"""Synthetic fail-closed tests for the read-only v2 GPU repeatability tool."""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from nex_bench.gpu_profile import summarize_profiles as summary
from test_gpu_profile_validator import fixture_v2, series


class GPUProfileRepeatabilityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write_capture(self, index, *, source=None, resolution=None, schema=None, mutate=None):
        document = copy.deepcopy(fixture_v2())
        document["run_id"] = f"1791841414-{1791841414000000 + index}"
        if source is not None:
            document["source_sha"] = source
        if resolution is not None:
            document["viewport"]["resolution_px"] = list(resolution)
        if schema is not None:
            document["schema_version"] = schema
        if mutate is not None:
            mutate(document)
        path = self.root / f"capture_{index}.json"
        path.write_text(json.dumps(document, allow_nan=False), encoding="utf-8")
        return path

    def captures(self, count=3):
        return [self.write_capture(index) for index in range(count)]

    def test_three_v2_repeats_generate_per_run_distribution(self):
        report = summary.summarize(self.captures())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["captures_validated"], 3)
        self.assertEqual(len(report["groups"]), 1)
        group = report["groups"][0]
        self.assertEqual(group["repeat_count"], 3)
        self.assertEqual(group["context"]["source_sha"], "a" * 40)
        self.assertEqual(group["environment_status"], "DRIVER_VERSION_UNVERIFIED")
        self.assertEqual(group["cpu_callback_one_percent_low_fps"]["status"], "MEASURED_CALLBACK_ONLY")
        self.assertAlmostEqual(
            group["cpu_callback_one_percent_low_fps"]["mean_of_run_values"], 1000 / 199.0, places=5
        )
        self.assertEqual(group["gpu_render_p95_ms_per_run"]["mean_of_run_values"], 2.5)
        self.assertEqual(group["cpu_render_p95_ms_per_run"]["mean_of_run_values"], 1.5)
        self.assertEqual(group["renderer_allocation_p95_bytes_per_run"]["mean_of_run_values"], 800000000.0)
        self.assertIn("No cross-group ranking", " ".join(report["limitations"]))

    def test_mixed_source_revision_is_not_averaged(self):
        captures = self.captures(2)
        captures.append(self.write_capture(2, source="b" * 40))
        with self.assertRaisesRegex(summary.ProfileError, "each identical"):
            summary.summarize(captures)

    def test_mixed_viewport_and_effect_configuration_are_not_averaged(self):
        scenarios = (
            {"resolution": (1280, 720)},
            {"mutate": lambda doc: doc["workload"].update({"effect_mode": "combined"})},
            {"mutate": lambda doc: doc["settings"].update({"vsync_mode": 0})},
            {"mutate": lambda doc: doc.update({"driver": "another_render_driver"})},
        )
        for kwargs in scenarios:
            with self.subTest(change=list(kwargs)):
                captures = self.captures(2)
                captures.append(self.write_capture(2, **kwargs))
                with self.assertRaisesRegex(summary.ProfileError, "each identical"):
                    summary.summarize(captures)

    def test_duplicate_run_id_and_undersized_groups_fail_closed(self):
        captures = self.captures(3)
        with self.assertRaisesRegex(summary.ProfileError, "duplicate run_id"):
            summary.summarize([captures[0], captures[0], captures[2]])
        with self.assertRaisesRegex(summary.ProfileError, "3 to 24"):
            summary.summarize(captures[:2])

    def test_historic_v1_and_invalid_v2_are_rejected(self):
        captures = self.captures(2)
        original = fixture_v2()
        legacy = copy.deepcopy(original)
        legacy["schema_version"] = "nex_gpu_render_profile.v1"
        # The strict validator rejects a schema-v1 document containing v2-only fields
        # even before the summary's explicit no-v1 check.
        captures.append(self.write_capture(2, mutate=lambda doc: doc.update(legacy)))
        with self.assertRaises(summary.ProfileError):
            summary.summarize(captures)
        captures = self.captures(2)
        captures.append(self.write_capture(2, mutate=lambda doc: doc.update({
            "run_status": "INVALID", "run_reason": "viewport_changed_or_unavailable"
        })))
        with self.assertRaisesRegex(summary.ProfileError, "incomplete or INVALID"):
            summary.summarize(captures)

    def test_unavailable_gpu_remains_inconclusive_not_zero(self):
        def unavailable(doc):
            doc["series"]["GPU_RENDER_MS"] = series(
                "ms", "RenderingServer.viewport_get_measured_render_time_gpu",
                [], status="UNAVAILABLE", reason="no_gpu_timing_available",
            )
        captures = self.captures(2)
        captures.append(self.write_capture(2, mutate=unavailable))
        report = summary.summarize(captures)
        gpu = report["groups"][0]["gpu_render_p95_ms_per_run"]
        self.assertEqual(gpu["status"], "INCONCLUSIVE")
        self.assertIn(None, gpu["per_run_values"])
        self.assertNotEqual(gpu["per_run_values"][-1], 0)

    def test_rejects_corrupt_json_and_symlink_inputs(self):
        captures = self.captures(3)
        captures[2].write_text('{"broken":}', encoding="utf-8")
        with self.assertRaises(summary.ProfileError):
            summary.summarize(captures)
        # Never follow a user-supplied symlink in the offline summary.
        target = self.write_capture(3)
        link = self.root / "link.json"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            return
        with self.assertRaisesRegex(summary.ProfileError, "non-symlink"):
            summary.summarize([self.write_capture(0), self.write_capture(1), link])

    def test_cli_emits_json_and_does_not_write_reports(self):
        captures = self.captures(3)
        with redirect_stdout(StringIO()) as output:
            code = summary.main([str(path) for path in captures])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PASS")
        self.assertEqual(sorted(path.name for path in self.root.iterdir()),
                         [f"capture_{index}.json" for index in range(3)])
        with redirect_stdout(StringIO()) as output:
            self.assertEqual(summary.main([str(captures[0])]), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()

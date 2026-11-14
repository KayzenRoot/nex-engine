"""Schema, coherence and reproducibility tests for the M09 performance.v1 observations."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tests" / "contracts"))

from _contract_support import read_schema  # noqa: E402 - contract test helper
from _preset_ab_support import load_builder  # noqa: E402 - local CI helper
from test_m01_schema import limited_schema_errors  # noqa: E402 - limited checker
from test_m06_performance_contract import mock_performance_consumer  # noqa: E402 - coherence consumer

TOOL = REPO / "docs" / "benchmarks" / "m06" / "tools" / "convert_m09_observations.py"
BUNDLE = REPO / "docs" / "benchmarks" / "m06" / "observations" / "m09-observations.v1.json"
EXPECTED_IDS = {
    "m09-preset-ab-low", "m09-preset-ab-high",
    "m09-m01-corridor-low", "m09-m01-corridor-high",
    "m09-res-960-low", "m09-res-960-high",
    "m09-res-1920-low", "m09-res-1920-high",
    "m09-i200-960-low", "m09-i200-960-high",
    "m09-i200-1920-low", "m09-i200-1920-high",
}


class M06ObservationBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m06_convert_observations", TOOL)
        cls.bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        cls.schema = read_schema("m06", "performance.v1.schema.json")
        cls.observations = {entry["observation_id"]: entry for entry in cls.bundle["observations"]}

    def test_bundle_has_twelve_unique_observations(self) -> None:
        self.assertEqual("m06_observation_bundle.v1", self.bundle["schema_version"])
        self.assertEqual(12, len(self.bundle["observations"]))
        self.assertEqual(EXPECTED_IDS, set(self.observations))

    def test_every_observation_passes_schema_and_coherence(self) -> None:
        for observation_id, observation in self.observations.items():
            with self.subTest(observation=observation_id):
                self.assertEqual([], limited_schema_errors(observation, self.schema))
                self.assertEqual([], mock_performance_consumer(observation))

    def test_measured_and_unavailable_fields_are_explicit(self) -> None:
        observation = self.observations["m09-i200-1920-high"]
        self.assertEqual("MEASURED", observation["timings"]["gpu_render_ms"]["status"])
        self.assertEqual("MEASURED", observation["timings"]["cpu_render_ms"]["status"])
        self.assertEqual("MEASURED", observation["timings"]["frame_pacing_ms"]["status"])
        self.assertEqual("UNAVAILABLE", observation["frame_interval"]["status"])
        self.assertEqual("UNAVAILABLE", observation["resources"]["draw_calls"]["status"])
        self.assertEqual("UNAVAILABLE", observation["resources"]["vram_used_bytes"]["status"])
        self.assertEqual("UNAVAILABLE", observation["resources"]["objects_rendered"]["status"])
        self.assertEqual("pacing", observation["bottleneck"]["classification"])

    def test_selected_measured_values_match_source_captures(self) -> None:
        expected = {
            "m09-preset-ab-low": 0.147,
            "m09-preset-ab-high": 0.746,
            "m09-m01-corridor-low": 0.086,
            "m09-m01-corridor-high": 0.542,
            "m09-res-960-low": 0.096,
            "m09-res-960-high": 0.317,
            "m09-res-1920-low": 0.156,
            "m09-res-1920-high": 0.826,
            "m09-i200-960-low": 0.099,
            "m09-i200-960-high": 0.322,
            "m09-i200-1920-low": 0.157,
            "m09-i200-1920-high": 0.846,
        }
        for observation_id, value in expected.items():
            with self.subTest(observation=observation_id):
                self.assertEqual(value, self.observations[observation_id]["timings"]["gpu_render_ms"]["value"])

    def test_every_evidence_uri_exists(self) -> None:
        for observation_id, observation in self.observations.items():
            with self.subTest(observation=observation_id):
                uri = observation["provenance"]["evidence_uri"]
                self.assertTrue((REPO / uri).is_file(), uri)
                self.assertEqual("617.14", observation["provenance"]["hardware"]["driver_version"])

    def test_converter_reproduces_committed_bundle(self) -> None:
        rebuilt = self.tool.build_bundle()
        self.assertEqual(self.bundle, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), BUNDLE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

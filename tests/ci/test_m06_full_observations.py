"""Schema, coverage and reproducibility tests for the full M09 performance.v1 bundle."""
from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tests" / "contracts"))

from _contract_support import read_schema  # noqa: E402 - contract test helper
from _preset_ab_support import load_builder  # noqa: E402 - local CI helper
from test_m01_schema import limited_schema_errors  # noqa: E402 - limited checker
from test_m06_performance_contract import mock_performance_consumer  # noqa: E402 - coherence consumer

TOOL = REPO / "docs" / "benchmarks" / "m06" / "tools" / "convert_m09_observations.py"
BUNDLE = REPO / "docs" / "benchmarks" / "m06" / "observations" / "m09-observations-full.v1.json"
EXPECTED_COUNTS = {
    "windows-rtx5050-2026-11-14-preset-ab": 6,
    "windows-rtx5050-2026-11-14-preset-scaling": 18,
    "windows-rtx5050-2026-11-14-m01-ab": 18,
    "windows-rtx5050-2026-11-14-res-scaling": 18,
    "windows-rtx5050-2026-11-14-interaction": 24,
    "windows-rtx5050-2026-11-14-cross-scene": 48,
    "windows-rtx5050-2026-11-14-interaction-200": 12,
    "windows-rtx5050-2026-11-14-arena-200-720": 6,
    "windows-rtx5050-2026-11-14-res-scaling-1440": 6,
}


class M06FullObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_builder("nex_m06_convert_full", TOOL)
        cls.bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        cls.schema = read_schema("m06", "performance.v1.schema.json")
        cls.observations = {entry["observation_id"]: entry for entry in cls.bundle["observations"]}
        cls.sources = {entry["observation_id"]: entry for entry in cls.bundle["sources"]}

    def test_bundle_has_156_unique_observations_and_sources(self) -> None:
        self.assertEqual("m06_observation_bundle.v1", self.bundle["schema_version"])
        self.assertEqual("full", self.bundle["mode"])
        self.assertEqual(156, len(self.bundle["observations"]))
        self.assertEqual(156, len(self.bundle["sources"]))
        self.assertEqual(156, len(self.observations))
        self.assertEqual(set(self.observations), set(self.sources))

    def test_bundle_coverage_matches_the_nine_performance_bundles(self) -> None:
        counts = Counter(source["bundle"] for source in self.bundle["sources"])
        self.assertEqual(EXPECTED_COUNTS, dict(counts))

    def test_every_observation_passes_schema_and_coherence(self) -> None:
        for observation_id, observation in self.observations.items():
            with self.subTest(observation=observation_id):
                self.assertEqual([], limited_schema_errors(observation, self.schema))
                self.assertEqual([], mock_performance_consumer(observation))

    def test_every_observation_is_pacing_and_has_evidence(self) -> None:
        for observation_id, observation in self.observations.items():
            with self.subTest(observation=observation_id):
                self.assertEqual("pacing", observation["bottleneck"]["classification"])
                self.assertTrue((REPO / observation["provenance"]["evidence_uri"]).is_file())
                self.assertEqual("MEASURED", observation["provenance"]["measurement_status"])

    def test_converter_reproduces_the_full_bundle(self) -> None:
        rebuilt = self.tool.build_bundle_full()
        self.assertEqual(self.bundle, rebuilt)
        self.assertEqual(self.tool.render_json(rebuilt), BUNDLE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

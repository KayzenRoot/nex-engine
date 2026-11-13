"""M10 combat feedback contract tests using the repository's limited stdlib checker."""
from __future__ import annotations

import itertools
import unittest
from typing import Any

from _contract_support import (
    global_unavailable_errors,
    provenance_evidence_errors,
    read_manifest,
    read_schema,
    unavailable_performance,
    unavailable_provenance,
)
from test_m01_schema import limited_schema_errors
from test_ownership_locks import normalize_path

FEEDBACK_TAIL_MS = 1000


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "feedback.v1",
        "observation_id": "m10-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "attack": {
            "attack_id": "slash",
            "phases": [
                {"phase": "anticipation", "duration_ms": 120},
                {"phase": "active", "duration_ms": 80},
                {"phase": "recovery", "duration_ms": 200},
            ],
        },
        "hit_events": [
            {"event_id": "hit-01", "at_ms": 150, "target_id": "goblin-01", "damage": 40, "critical": False, "element": "fire"},
            {"event_id": "hit-02", "at_ms": 160, "target_id": "goblin-02", "damage": 120, "critical": True, "element": "fire"},
        ],
        "feedback_channels": [
            {"channel_id": "hit-stop-01", "channel": "hit_stop", "start_ms": 150, "duration_ms": 60,
             "intensity": 1.0, "priority": 10, "event_id": "hit-01"},
            {"channel_id": "shake-01", "channel": "camera_shake", "start_ms": 150, "duration_ms": 120,
             "intensity": 0.4, "priority": 8, "event_id": "hit-02"},
            {"channel_id": "flash-01", "channel": "flash", "start_ms": 150, "duration_ms": 90,
             "intensity": 0.6, "priority": 7, "event_id": "hit-02"},
            {"channel_id": "number-01", "channel": "damage_number", "start_ms": 150, "duration_ms": 600,
             "intensity": 1.0, "priority": 5, "event_id": "hit-02", "target_id": "goblin-02"},
            {"channel_id": "recoil-01", "channel": "recoil", "start_ms": 150, "duration_ms": 100,
             "intensity": 0.5, "priority": 6, "event_id": "hit-01"},
        ],
        "budget": {
            "max_hit_stop_ms": 80,
            "max_shake_amplitude": 0.8,
            "max_concurrent_channels": 5,
            "max_total_channels": 8,
        },
        "performance": unavailable_performance(),
        "provenance": unavailable_provenance(),
    }


def _total_duration(document: dict[str, Any]) -> int:
    return sum(int(phase.get("duration_ms", 0)) for phase in document.get("attack", {}).get("phases", []))


def _events_by_id(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["event_id"]: event for event in document.get("hit_events", []) if isinstance(event, dict)}


def _concurrency_errors(channels: list[dict[str, Any]], limit: int) -> list[str]:
    errors: list[str] = []
    for channel in channels:
        start = int(channel.get("start_ms", 0))
        active = 0
        for other in channels:
            other_start = int(other.get("start_ms", 0))
            other_end = other_start + int(other.get("duration_ms", 0))
            if other_start <= start < other_end:
                active += 1
        if active > limit:
            errors.append(f"$.feedback_channels[{channel.get('channel_id')}]: concurrency {active} exceeds {limit}")
    return errors


def mock_feedback_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus combat-feedback invariants."""
    errors = limited_schema_errors(document, read_schema("m10", "feedback.v1.schema.json"))
    attack = document.get("attack", {})
    phases = attack.get("phases", []) if isinstance(attack, dict) else []
    total = _total_duration(document)
    if isinstance(phases, list) and all(isinstance(phase, dict) for phase in phases):
        names = [phase.get("phase") for phase in phases]
        if len(names) != len(set(names)):
            errors.append("$.attack.phases: duplicate phase")
        if "active" not in names:
            errors.append("$.attack.phases: active phase is required")
        if total > 10000:
            errors.append("$.attack.phases: total duration exceeds 10000 ms")
    events = document.get("hit_events", [])
    event_map = _events_by_id(document)
    if isinstance(events, list) and all(isinstance(event, dict) for event in events):
        ids = [event.get("event_id") for event in events]
        if len(ids) != len(set(ids)):
            errors.append("$.hit_events: duplicate event_id")
        for event in events:
            if int(event.get("at_ms", 0)) > total:
                errors.append(f"$.hit_events[{event.get('event_id')}]: at_ms exceeds attack duration")
            if event.get("critical") and int(event.get("damage", 0)) <= 0:
                errors.append(f"$.hit_events[{event.get('event_id')}]: critical requires damage > 0")
    channels = document.get("feedback_channels", [])
    budget = document.get("budget", {})
    if isinstance(channels, list) and all(isinstance(channel, dict) for channel in channels):
        ids = [channel.get("channel_id") for channel in channels]
        if len(ids) != len(set(ids)):
            errors.append("$.feedback_channels: duplicate channel_id")
        if isinstance(budget, dict) and len(channels) > int(budget.get("max_total_channels", 0)):
            errors.append("$.feedback_channels: total channels exceed max_total_channels")
        for channel in channels:
            start = int(channel.get("start_ms", 0))
            end = start + int(channel.get("duration_ms", 0))
            if start > total or end > total + FEEDBACK_TAIL_MS:
                errors.append(f"$.feedback_channels[{channel.get('channel_id')}]: outside attack window plus tail")
            event_id = channel.get("event_id")
            if event_id is not None and event_id not in event_map:
                errors.append(f"$.feedback_channels[{channel.get('channel_id')}]: dangling event_id")
            if channel.get("channel") == "damage_number":
                event = event_map.get(event_id)
                if event is None or int(event.get("damage", 0)) <= 0:
                    errors.append(f"$.feedback_channels[{channel.get('channel_id')}]: damage_number requires positive damage")
            if channel.get("channel") == "hit_stop" and isinstance(budget, dict):
                if int(channel.get("duration_ms", 0)) > int(budget.get("max_hit_stop_ms", 0)):
                    errors.append(f"$.feedback_channels[{channel.get('channel_id')}]: hit_stop exceeds budget")
            if channel.get("channel") == "camera_shake" and isinstance(budget, dict):
                if float(channel.get("intensity", 0.0)) > float(budget.get("max_shake_amplitude", 0.0)):
                    errors.append(f"$.feedback_channels[{channel.get('channel_id')}]: shake exceeds budget")
        if isinstance(budget, dict):
            errors.extend(_concurrency_errors(channels, int(budget.get("max_concurrent_channels", 1))))
    errors.extend(global_unavailable_errors(document))
    errors.extend(provenance_evidence_errors(document))
    return errors


class FeedbackContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m10", "feedback.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("feedback.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_feedback_consumer(valid_observation()))

    def test_missing_attack_is_rejected(self) -> None:
        document = valid_observation()
        del document["attack"]
        self.assertIn(
            "$: missing required property attack",
            limited_schema_errors(document, read_schema("m10", "feedback.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_feedback_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertEqual([], mock_feedback_consumer(document))

        zero = valid_observation()
        zero["performance"]["measurement_status"] = "MEASURED"
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_feedback_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 0,
        }
        self.assertTrue(mock_feedback_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["draw_calls"] = {"status": "MEASURED", "value": 12}
        self.assertTrue(
            any("global UNAVAILABLE forbids MEASURED metric" in error for error in mock_feedback_consumer(document))
        )

    def test_duplicate_ids_are_rejected(self) -> None:
        duplicate_event = valid_observation()
        duplicate_event["hit_events"][1]["event_id"] = "hit-01"
        self.assertTrue(any("duplicate event_id" in error for error in mock_feedback_consumer(duplicate_event)))

        duplicate_channel = valid_observation()
        duplicate_channel["feedback_channels"][1]["channel_id"] = "hit-stop-01"
        self.assertTrue(any("duplicate channel_id" in error for error in mock_feedback_consumer(duplicate_channel)))

    def test_phase_invariants(self) -> None:
        duplicate = valid_observation()
        duplicate["attack"]["phases"][1]["phase"] = "anticipation"
        self.assertTrue(any("duplicate phase" in error for error in mock_feedback_consumer(duplicate)))

        missing_active = valid_observation()
        missing_active["attack"]["phases"] = [phase for phase in missing_active["attack"]["phases"] if phase["phase"] != "active"]
        self.assertTrue(any("active phase is required" in error for error in mock_feedback_consumer(missing_active)))

        long_attack = valid_observation()
        long_attack["attack"]["phases"][2]["duration_ms"] = 10000
        self.assertTrue(any("total duration exceeds" in error for error in mock_feedback_consumer(long_attack)))

    def test_event_window_and_critical_damage(self) -> None:
        outside = valid_observation()
        outside["hit_events"][0]["at_ms"] = 500
        self.assertTrue(any("at_ms exceeds" in error for error in mock_feedback_consumer(outside)))

        critical_zero = valid_observation()
        critical_zero["hit_events"][1]["damage"] = 0
        self.assertTrue(any("critical requires damage" in error for error in mock_feedback_consumer(critical_zero)))

    def test_channel_window_and_dangling_event(self) -> None:
        outside = valid_observation()
        outside["feedback_channels"][3]["duration_ms"] = 5000
        self.assertTrue(any("outside attack window" in error for error in mock_feedback_consumer(outside)))

        dangling = valid_observation()
        dangling["feedback_channels"][0]["event_id"] = "missing"
        self.assertTrue(any("dangling event_id" in error for error in mock_feedback_consumer(dangling)))

    def test_damage_number_requires_positive_damage(self) -> None:
        document = valid_observation()
        document["hit_events"][1]["damage"] = 0
        document["hit_events"][1]["critical"] = False
        self.assertTrue(
            any("damage_number requires positive damage" in error for error in mock_feedback_consumer(document))
        )

    def test_budgets(self) -> None:
        hit_stop = valid_observation()
        hit_stop["feedback_channels"][0]["duration_ms"] = 120
        self.assertTrue(any("hit_stop exceeds budget" in error for error in mock_feedback_consumer(hit_stop)))

        shake = valid_observation()
        shake["feedback_channels"][1]["intensity"] = 1.0
        self.assertTrue(any("shake exceeds budget" in error for error in mock_feedback_consumer(shake)))

        total = valid_observation()
        total["budget"]["max_total_channels"] = 2
        self.assertTrue(any("total channels exceed" in error for error in mock_feedback_consumer(total)))

    def test_concurrency_budget(self) -> None:
        document = valid_observation()
        document["budget"]["max_concurrent_channels"] = 2
        self.assertTrue(any("concurrency" in error for error in mock_feedback_consumer(document)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_feedback_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m10-fixture"
        self.assertEqual([], mock_feedback_consumer(document))

    def test_invalid_vocabulary_is_rejected(self) -> None:
        document = valid_observation()
        document["attack"]["attack_id"] = "Slash"
        self.assertTrue(mock_feedback_consumer(document))

        document = valid_observation()
        document["feedback_channels"][0]["channel"] = "screen_flash"
        self.assertTrue(mock_feedback_consumer(document))

        document = valid_observation()
        document["hit_events"][0]["element"] = "holy"
        self.assertTrue(mock_feedback_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["attack"]["phases"][0]["duration_ms"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["hit_events"][0]["damage"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["feedback_channels"][0]["intensity"] = 1.5; perturbations.append(doc)
        doc = valid_observation(); doc["feedback_channels"][0]["priority"] = 11; perturbations.append(doc)
        doc = valid_observation(); doc["budget"]["max_hit_stop_ms"] = 501; perturbations.append(doc)
        doc = valid_observation(); doc["budget"]["max_concurrent_channels"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["provenance"]["base_sha"] = "A" * 40; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_feedback_consumer(document))


class M10OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m10")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m10")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m10")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m10")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

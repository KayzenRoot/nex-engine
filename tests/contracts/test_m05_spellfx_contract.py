"""M05 SpellFX contract tests using the repository's limited stdlib checker."""
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


def valid_observation() -> dict[str, Any]:
    return {
        "schema_version": "spellfx.v1",
        "observation_id": "m05-fixture-001",
        "captured_at_utc": "2026-11-13T12:00:00Z",
        "spells": [
            {
                "spell_id": "ember-bolt",
                "element": "fire",
                "phases": [
                    {
                        "phase": "cast",
                        "duration_ms": 300,
                        "emitters": [
                            {"emitter_id": "cast-spark", "kind": "particles", "amount": 64,
                             "lifetime_ms": 400, "gpu": True, "light_bridge": False},
                        ],
                    },
                    {
                        "phase": "travel",
                        "duration_ms": 200,
                        "emitters": [
                            {"emitter_id": "travel-trail", "kind": "trail", "amount": 32,
                             "lifetime_ms": 250, "gpu": False, "light_bridge": False},
                        ],
                    },
                    {
                        "phase": "impact",
                        "duration_ms": 150,
                        "emitters": [
                            {"emitter_id": "impact-burst", "kind": "particles", "amount": 128,
                             "lifetime_ms": 600, "gpu": True, "light_bridge": False},
                            {"emitter_id": "impact-light", "kind": "light", "amount": 1,
                             "lifetime_ms": 300, "gpu": False, "light_bridge": True},
                        ],
                    },
                    {
                        "phase": "linger",
                        "duration_ms": 4000,
                        "emitters": [
                            {"emitter_id": "linger-decal", "kind": "decal", "amount": 1,
                             "lifetime_ms": 4000, "gpu": False, "light_bridge": False},
                        ],
                    },
                ],
                "gameplay_authority": {
                    "damage_owner": "gameplay",
                    "hit_detection": "gameplay",
                    "cancel_on_death": True,
                },
                "decal_policy": {"max_decals": 8, "fade_ms": 4000},
            }
        ],
        "fx_budget": {
            "max_emitters": 16,
            "max_particles": 10000,
            "max_gpu_particles": 8,
            "max_decals": 32,
        },
        "performance": unavailable_performance(),
        "provenance": unavailable_provenance(),
    }


def mock_spellfx_consumer(document: dict[str, Any]) -> list[str]:
    """Independent consumer check: schema plus cross-field SpellFX invariants."""
    errors = limited_schema_errors(document, read_schema("m05", "spellfx.v1.schema.json"))
    spells = document.get("spells")
    budget = document.get("fx_budget")
    if isinstance(spells, list) and all(isinstance(spell, dict) for spell in spells):
        spell_ids = [spell.get("spell_id") for spell in spells]
        if len(spell_ids) != len(set(spell_ids)):
            errors.append("$.spells: duplicate spell_id")
        totals = {"emitters": 0, "particles": 0, "gpu": 0, "decals": 0}
        for spell in spells:
            spell_id = spell.get("spell_id")
            phases = spell.get("phases", [])
            if not isinstance(phases, list):
                continue
            phase_names = [phase.get("phase") for phase in phases if isinstance(phase, dict)]
            if len(phase_names) != len(set(phase_names)):
                errors.append(f"$.spells[{spell_id}]: duplicate phase")
            if "impact" not in phase_names:
                errors.append(f"$.spells[{spell_id}]: impact phase is required")
            emitter_ids: list[str] = []
            total_duration = 0
            for phase in phases:
                if not isinstance(phase, dict):
                    continue
                total_duration += int(phase.get("duration_ms", 0))
                for emitter in phase.get("emitters", []):
                    if not isinstance(emitter, dict):
                        continue
                    emitter_ids.append(emitter.get("emitter_id"))
                    totals["emitters"] += 1
                    totals["particles"] += int(emitter.get("amount", 0))
                    if emitter.get("gpu"):
                        totals["gpu"] += 1
                    if emitter.get("kind") == "decal":
                        totals["decals"] += 1
                    if emitter.get("kind") in ("light", "decal") and int(emitter.get("amount", 0)) < 1:
                        errors.append(f"$.spells[{spell_id}].{emitter.get('emitter_id')}: light/decal requires amount >= 1")
                    is_light = emitter.get("kind") == "light"
                    if is_light != bool(emitter.get("light_bridge")):
                        errors.append(f"$.spells[{spell_id}].{emitter.get('emitter_id')}: light_bridge mismatch")
            if len(emitter_ids) != len(set(emitter_ids)):
                errors.append(f"$.spells[{spell_id}]: duplicate emitter_id")
            if total_duration > 60000:
                errors.append(f"$.spells[{spell_id}]: total duration exceeds 60000 ms")
            authority = spell.get("gameplay_authority", {})
            if isinstance(authority, dict):
                for key in ("damage_owner", "hit_detection"):
                    if authority.get(key) != "gameplay":
                        errors.append(f"$.spells[{spell_id}].gameplay_authority.{key}: must be gameplay")
            policy = spell.get("decal_policy")
            if isinstance(policy, dict) and isinstance(budget, dict):
                if int(policy.get("max_decals", 0)) > int(budget.get("max_decals", 0)):
                    errors.append(f"$.spells[{spell_id}].decal_policy: exceeds fx_budget.max_decals")
        if isinstance(budget, dict):
            if totals["emitters"] > int(budget.get("max_emitters", 0)):
                errors.append("$.fx_budget: emitters exceed max_emitters")
            if totals["particles"] > int(budget.get("max_particles", 0)):
                errors.append("$.fx_budget: particles exceed max_particles")
            if totals["gpu"] > int(budget.get("max_gpu_particles", 0)):
                errors.append("$.fx_budget: GPU emitters exceed max_gpu_particles")
            if totals["decals"] > int(budget.get("max_decals", 0)):
                errors.append("$.fx_budget: decals exceed max_decals")
    errors.extend(global_unavailable_errors(document))
    errors.extend(provenance_evidence_errors(document))
    return errors


class SpellFXContractTests(unittest.TestCase):
    def test_schema_is_standalone_and_versioned(self) -> None:
        schema = read_schema("m05", "spellfx.v1.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
        self.assertNotIn("$ref", str(schema))
        self.assertEqual("spellfx.v1", schema["properties"]["schema_version"]["const"])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], mock_spellfx_consumer(valid_observation()))

    def test_missing_spells_is_rejected(self) -> None:
        document = valid_observation()
        del document["spells"]
        self.assertIn(
            "$: missing required property spells",
            limited_schema_errors(document, read_schema("m05", "spellfx.v1.schema.json")),
        )

    def test_fps_claims_are_rejected(self) -> None:
        document = valid_observation()
        document["fps"] = 60
        self.assertTrue(
            any("unexpected property fps" in error for error in mock_spellfx_consumer(document))
        )

    def test_availability_semantics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "UNAVAILABLE", "unavailable_reason": "no provider"}
        self.assertEqual([], mock_spellfx_consumer(document))

        zero = valid_observation()
        zero["performance"]["measurement_status"] = "MEASURED"
        zero["performance"]["draw_calls"] = {"status": "MEASURED", "value": 0}
        self.assertEqual([], mock_spellfx_consumer(zero))

        fabricated = valid_observation()
        fabricated["performance"]["draw_calls"] = {
            "status": "UNAVAILABLE",
            "unavailable_reason": "no provider",
            "value": 0,
        }
        self.assertTrue(mock_spellfx_consumer(fabricated))

    def test_global_unavailable_forbids_measured_metrics(self) -> None:
        document = valid_observation()
        document["performance"]["gpu_render_time"] = {"status": "MEASURED", "value": 1.2}
        self.assertTrue(
            any("global UNAVAILABLE forbids MEASURED metric" in error for error in mock_spellfx_consumer(document))
        )

    def test_duplicate_spell_and_phase_are_rejected(self) -> None:
        duplicate = valid_observation()
        duplicate["spells"].append(dict(duplicate["spells"][0]))
        self.assertTrue(any("duplicate spell_id" in error for error in mock_spellfx_consumer(duplicate)))

        same_phase = valid_observation()
        same_phase["spells"][0]["phases"][1]["phase"] = "cast"
        self.assertTrue(any("duplicate phase" in error for error in mock_spellfx_consumer(same_phase)))

    def test_impact_phase_is_required(self) -> None:
        document = valid_observation()
        document["spells"][0]["phases"] = [phase for phase in document["spells"][0]["phases"] if phase["phase"] != "impact"]
        self.assertTrue(any("impact phase is required" in error for error in mock_spellfx_consumer(document)))

    def test_duplicate_emitter_id_is_rejected(self) -> None:
        document = valid_observation()
        document["spells"][0]["phases"][1]["emitters"][0]["emitter_id"] = "cast-spark"
        self.assertTrue(any("duplicate emitter_id" in error for error in mock_spellfx_consumer(document)))

    def test_gameplay_authority_must_remain_gameplay(self) -> None:
        document = valid_observation()
        document["spells"][0]["gameplay_authority"]["damage_owner"] = "visual_only"
        self.assertTrue(any("damage_owner: must be gameplay" in error for error in mock_spellfx_consumer(document)))

        document = valid_observation()
        document["spells"][0]["gameplay_authority"]["hit_detection"] = "visual_only"
        self.assertTrue(any("hit_detection: must be gameplay" in error for error in mock_spellfx_consumer(document)))

    def test_light_bridge_coherence(self) -> None:
        light_without_bridge = valid_observation()
        light_without_bridge["spells"][0]["phases"][2]["emitters"][1]["light_bridge"] = False
        self.assertTrue(
            any("light_bridge mismatch" in error for error in mock_spellfx_consumer(light_without_bridge))
        )

        bridge_on_particles = valid_observation()
        bridge_on_particles["spells"][0]["phases"][0]["emitters"][0]["light_bridge"] = True
        self.assertTrue(
            any("light_bridge mismatch" in error for error in mock_spellfx_consumer(bridge_on_particles))
        )

    def test_budget_totals(self) -> None:
        emitters = valid_observation()
        emitters["fx_budget"]["max_emitters"] = 2
        self.assertTrue(any("emitters exceed" in error for error in mock_spellfx_consumer(emitters)))

        particles = valid_observation()
        particles["fx_budget"]["max_particles"] = 100
        self.assertTrue(any("particles exceed" in error for error in mock_spellfx_consumer(particles)))

        gpu = valid_observation()
        gpu["fx_budget"]["max_gpu_particles"] = 1
        self.assertTrue(any("GPU emitters exceed" in error for error in mock_spellfx_consumer(gpu)))

        decals = valid_observation()
        decals["fx_budget"]["max_decals"] = 0
        self.assertTrue(any("decals exceed" in error for error in mock_spellfx_consumer(decals)))

    def test_duration_and_decal_policy(self) -> None:
        long_spell = valid_observation()
        long_spell["spells"][0]["phases"][3]["duration_ms"] = 60000
        self.assertTrue(any("total duration exceeds" in error for error in mock_spellfx_consumer(long_spell)))

        policy = valid_observation()
        policy["spells"][0]["decal_policy"]["max_decals"] = 64
        self.assertTrue(any("exceeds fx_budget.max_decals" in error for error in mock_spellfx_consumer(policy)))

    def test_provenance_requires_evidence_when_measured(self) -> None:
        document = valid_observation()
        document["provenance"]["measurement_status"] = "MEASURED"
        self.assertTrue(any("evidence_uri" in error for error in mock_spellfx_consumer(document)))

        document["provenance"]["evidence_uri"] = "evidence://m05-fixture"
        self.assertEqual([], mock_spellfx_consumer(document))

    def test_invalid_ids_and_vocabulary_are_rejected(self) -> None:
        document = valid_observation()
        document["spells"][0]["spell_id"] = "Ember Bolt"
        self.assertTrue(mock_spellfx_consumer(document))

        document = valid_observation()
        document["spells"][0]["element"] = "holy"
        self.assertTrue(mock_spellfx_consumer(document))

    def test_negative_perturbations_are_rejected(self) -> None:
        perturbations = []
        doc = valid_observation(); doc["spells"][0]["phases"][0]["duration_ms"] = -1; perturbations.append(doc)
        doc = valid_observation(); doc["spells"][0]["phases"][0]["emitters"][0]["amount"] = 100001; perturbations.append(doc)
        doc = valid_observation(); doc["spells"][0]["phases"][0]["emitters"][0]["kind"] = "mesh"; perturbations.append(doc)
        doc = valid_observation(); doc["spells"][0]["phases"][0]["emitters"][0]["lifetime_ms"] = 60001; perturbations.append(doc)
        doc = valid_observation(); doc["spells"][0]["phases"][2]["emitters"][1]["amount"] = 0; perturbations.append(doc)
        doc = valid_observation(); doc["fx_budget"]["max_particles"] = 1000001; perturbations.append(doc)
        doc = valid_observation(); doc["spells"][0]["decal_policy"]["fade_ms"] = 60001; perturbations.append(doc)
        doc = valid_observation(); doc["performance"]["gpu_render_time"]["value"] = -1; perturbations.append(doc)
        for document in perturbations:
            with self.subTest(document=document):
                self.assertTrue(mock_spellfx_consumer(document))


class M05OwnershipTests(unittest.TestCase):
    def test_manifest_is_contract_only_and_steward_owned(self) -> None:
        manifest = read_manifest("m05")
        self.assertIn("NOT_MODULE_ADMISSION", manifest["status"])
        self.assertFalse(manifest["rules"]["module_admission_implied"])
        self.assertEqual("integration-steward", manifest["writer"])

    def test_paths_are_relative_and_normalized(self) -> None:
        for entry in read_manifest("m05")["paths"]:
            self.assertEqual(normalize_path(entry["path"]), entry["path"].casefold())
            self.assertNotIn("..", entry["path"])

    def test_write_paths_are_disjoint(self) -> None:
        bases = [normalize_path(entry["path"]).removesuffix("/**") for entry in read_manifest("m05")["paths"]]
        for first, second in itertools.combinations(bases, 2):
            self.assertFalse(
                first == second or first.startswith(second + "/") or second.startswith(first + "/"),
                f"overlapping write paths: {first!r} and {second!r}",
            )

    def test_every_path_has_owner_and_consumers(self) -> None:
        for entry in read_manifest("m05")["paths"]:
            self.assertTrue(entry["owner"])
            self.assertIsInstance(entry["consumers"], list)


if __name__ == "__main__":
    unittest.main()

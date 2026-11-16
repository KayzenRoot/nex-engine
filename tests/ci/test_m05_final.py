"""Acceptance tests for the M05 VFX reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m05"
RUNTIME = PACK / "vfx-runtime.v1.json"
GATE = PACK / "M05-FINAL-GATE.md"
VISUAL = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m05-vfx"
STRESS = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m05-vfx-perf"
BASELINE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m05-vfx-baseline"
SMOKE = VISUAL / "spell-fx-smoke-2026-11-15.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0016-M05-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M05-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M05-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"
ELEMENTS = {"fire", "frost", "lightning", "smoke", "impact", "projectile"}
SCENES = {"corridor_static", "arena_combat", "dense_city"}


class M05FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, GATE, SMOKE):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_spellfx_smoke_passes_twelve_checks(self) -> None:
        self.assertEqual("m05_spellfx_smoke.v1", self.smoke["schema_version"])
        self.assertEqual("PASS", self.smoke["verdict"])
        self.assertEqual(12, self.smoke["checks"])
        self.assertEqual([], self.smoke["failures"])
        self.assertEqual("SPELLFX_CONTRACT_VERIFIED", self.runtime["s01"]["verdict"])
        self.assertEqual(128, self.runtime["s01"]["max_active"])
        self.assertEqual(64, self.runtime["s01"]["max_per_vfx"])

    def test_elemental_library_covers_six_effects(self) -> None:
        elements = set(self.runtime["s02"]["elements"])
        self.assertEqual(ELEMENTS, elements)
        captures = self.runtime["s02"]["captures"]
        self.assertEqual(18, len(captures))
        self.assertEqual(SCENES, {cell["scene"] for cell in captures})
        for cell in captures:
            with self.subTest(scene=cell["scene"], element=cell["element"]):
                self.assertGreater(cell["changed_pixels_pct"], 0.0)
                self.assertGreater(cell["png_bytes"], 0)
                self.assertEqual(64, len(cell["sha256"]))
        for element in ELEMENTS:
            with self.subTest(element=element):
                self.assertGreater(self.runtime["s02"]["elements"][element]["particles"], 0)

    def test_visual_evidence_is_complete(self) -> None:
        for scene in SCENES:
            with self.subTest(scene=scene):
                self.assertTrue((VISUAL / f"{scene}_baseline.png").is_file())
                for element in ELEMENTS:
                    self.assertTrue((VISUAL / f"{scene}_{element}.png").is_file())
        self.assertTrue((VISUAL / "arena_combat_all25.png").is_file())
        self.assertEqual(22, len(list(VISUAL.glob("*.png"))))

    def test_projectile_and_combat_clarity_are_limited(self) -> None:
        self.assertFalse(self.runtime["s03"]["authoritative_hit_detection"])
        self.assertFalse(self.runtime["s03"]["collision_enabled"])
        self.assertEqual("PROJECTILE_HITECHO_VISUAL_ONLY", self.runtime["s03"]["verdict"])
        self.assertFalse(self.runtime["s04"]["telegraph_system"])
        self.assertFalse(self.runtime["s04"]["flash_reduction"])
        self.assertFalse(self.runtime["s04"]["threat_budget_scheduler"])
        self.assertGreater(self.runtime["s04"]["changed_pixels_pct"], 0.0)
        self.assertEqual("COMBAT_CLARITY_LIMITED", self.runtime["s04"]["verdict"])

    def test_stress_runs_cover_one_twentyfive_and_hundred(self) -> None:
        rows = {row["events"]: row for row in self.runtime["s05"]["stress"]}
        self.assertEqual({1, 25, 100}, set(rows))
        for count, row in rows.items():
            with self.subTest(events=count):
                self.assertEqual(3, row["runs"])
                self.assertGreater(row["gpu_p95_ms"], 0.0)
                self.assertLess(row["gpu_p95_ms"], 16.67)
                self.assertGreater(row["one_percent_low_fps"], 60.0)
                self.assertGreaterEqual(row["gpu_p95_spread_pct"], 0.0)
        self.assertEqual(3, self.runtime["s05"]["baseline"]["runs"])
        self.assertLess(rows[100]["gpu_p95_ms"], 16.67)
        self.assertEqual(12, self.runtime["s05"]["lifecycle_checks"])

    def test_stress_manifests_and_hashes_exist(self) -> None:
        for directory in (STRESS, BASELINE):
            with self.subTest(directory=directory.name):
                self.assertTrue((directory / "SHA256SUMS.txt").is_file())
                manifest = json.loads((directory / "runs.v1.json").read_text(encoding="utf-8"))
                self.assertEqual("m05_vfx_runs.v1", manifest["schema_version"])
                self.assertEqual(self.runtime["source_sha"], manifest["source_sha"])
                self.assertTrue(manifest["runs"])
                for entry in manifest["runs"]:
                    self.assertTrue((directory / entry["file"]).is_file())
                    self.assertTrue((directory / f"{entry['file']}.validation.json").is_file())

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s06"]["decisions"]}
        self.assertEqual("GO", decisions["GPUParticles3D elemental library"])
        self.assertEqual("GO", decisions["SpellFX request contract"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["PulsePool lifecycle"])
        self.assertEqual("NO_GO", decisions["Combat clarity / ThreatBudget"])
        self.assertEqual("NO_GO", decisions["Cinematic quality / PoE2 parity"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m05FinalReference"]
        self.assertEqual("NEX-M05-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([10, 52, 53, 54, 55, 56, 57, 58], block["issues"])
        self.assertEqual("M05_REFERENCE_VFX_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builder_is_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for builder in ("build_fx_budget_dataset.py", "build_m05_runtime.py"):
            with self.subTest(builder=builder):
                self.assertIn(f"docs/benchmarks/m05/tools/{builder} --check", workflow)

    def test_gate_covers_the_closed_issues(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#52", "#53", "#54", "#55", "#56", "#57", "#58", "#10",
                       "M05_VFX_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

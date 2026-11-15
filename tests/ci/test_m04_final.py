"""Acceptance tests for the M04 materials reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m04"
RUNTIME = PACK / "materials-runtime.v1.json"
SCALING = PACK / "texture-scaling.v1.json"
GATE = PACK / "M04-FINAL-GATE.md"
ATLAS = REPO / "nex_modules" / "materials" / "atlas" / "atlas.v1.json"
DECAL = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-15-m04-gallery" / "decal-smoke-2026-11-15.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0015-M04-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M04-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M04-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"


class M04FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.scaling = json.loads(SCALING.read_text(encoding="utf-8"))
        cls.atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        cls.decal = json.loads(DECAL.read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, SCALING, GATE, ATLAS, DECAL):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_atlas_has_eight_materials_and_three_maps(self) -> None:
        self.assertEqual("material.v1", self.atlas["schema_version"])
        self.assertEqual(8, len(self.atlas["materials"]))
        for material in self.atlas["materials"]:
            with self.subTest(id=material["material_id"]):
                self.assertEqual(3, len(material["textures"]))
                self.assertEqual({"albedo", "normal", "orm"},
                                 {texture["slot"] for texture in material["textures"]})
                for texture in material["textures"]:
                    self.assertEqual(256, texture["width_px"])
                    self.assertEqual(256, texture["height_px"])

    def test_gallery_and_shader_are_rendered(self) -> None:
        s01 = self.runtime["s01"]
        self.assertEqual(8, s01["materials"])
        self.assertEqual(24, s01["textures"])
        self.assertEqual([1920, 1080], s01["gallery_px"])
        self.assertGreater(self.runtime["s02"]["changed_pixels_pct"], 0.0)
        self.assertGreater(self.runtime["s02"]["psnr_db"], 20.0)
        self.assertEqual("SHADER_APPLIED", self.runtime["s02"]["verdict"])

    def test_decal_visual_and_request_bridge(self) -> None:
        self.assertEqual("PASS", self.decal["verdict"])
        self.assertEqual(12, self.decal["checks"])
        self.assertEqual([], self.decal["failures"])
        self.assertGreater(self.runtime["s05"]["decal_changed_pixels_pct"], 0.0)
        self.assertEqual("DECAL_SURFACE_DERIVED", self.runtime["s05"]["verdict"])

    def test_texture_scaling_is_documented(self) -> None:
        self.assertEqual("m04_texture_scaling.v1", self.scaling["schema_version"])
        self.assertEqual(3, len(self.scaling["cells"]))
        cells = {cell["size_px"]: cell for cell in self.scaling["cells"]}
        four_k = {item["slot"]: item for item in cells[4096]["maps"]}
        self.assertEqual("GENERATED_IN_MEMORY", four_k["albedo"]["status"])
        self.assertEqual("NOT_GENERATED", four_k["normal"]["status"])
        self.assertEqual("NOT_GENERATED", four_k["orm"]["status"])
        self.assertGreater(self.runtime["s06"]["upscaled_4k_png_bytes"],
                           self.runtime["s06"]["native_1k_png_bytes"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s07"]["decisions"]}
        self.assertEqual("GO", decisions["PBR Reference Atlas"])
        self.assertEqual("GO", decisions["DecalSurface Bridge"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["TextureBudget"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m04FinalReference"]
        self.assertEqual("NEX-M04-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([9, 44, 45, 46, 47, 48, 49, 50, 51], block["issues"])
        self.assertEqual("M04_REFERENCE_MATERIALS_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builders_are_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for builder in ("build_pbr_atlas.py", "build_texture_scaling.py", "build_materials_runtime.py"):
            with self.subTest(builder=builder):
                self.assertIn(f"docs/benchmarks/m04/tools/{builder} --check", workflow)

    def test_gate_covers_the_closed_issues(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#44", "#45", "#46", "#47", "#48", "#49", "#50", "#51", "#9",
                       "M04_MATERIALS_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

"""Structural and reproducibility tests for the NEX M04 procedural material kit."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

from _preset_ab_support import load_builder

REPO = Path(__file__).resolve().parents[2]
KIT = REPO / "nex_modules" / "materials" / "kit"
TEXTURES = KIT / "textures"
MATERIALS = KIT / "materials"
OBSERVATION = KIT / "kit.v1.json"
REPORT = REPO / "docs" / "benchmarks" / "m04" / "MATERIAL-KIT.md"
TOOL = REPO / "docs" / "benchmarks" / "m04" / "tools" / "build_material_kit.py"
LOG = KIT / "evidence" / "headless-load-2026-11-15.log"
PNG_MODULE = REPO / "docs" / "benchmarks" / "m09" / "tools" / "png_image.py"
IDS = ("concrete_floor", "brushed_metal", "oak_wood", "emissive_trim")


class MaterialKitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
        cls.png = load_builder("nex_m04_png_image", PNG_MODULE)

    def test_files_and_textures_exist(self) -> None:
        for material_id in IDS:
            with self.subTest(id=material_id):
                self.assertTrue((MATERIALS / f"{material_id}.tres").is_file())
                for slot in ("albedo", "normal", "orm"):
                    self.assertTrue((TEXTURES / f"{material_id}_{slot}.png").is_file())
        for path in (KIT / "project.godot", KIT / "main.tscn", KIT / "validate_kit.gd",
                     KIT / "README.md", OBSERVATION, REPORT, LOG):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_builder_reproduces_every_byte(self) -> None:
        result = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("M04_MATERIAL_KIT_CHECK_PASS: 4 materials / 12 textures", result.stdout)

    def test_pngs_decode_as_rgba_128(self) -> None:
        for material_id in IDS:
            for slot in ("albedo", "normal", "orm"):
                with self.subTest(id=material_id, slot=slot):
                    image = self.png.read_png(TEXTURES / f"{material_id}_{slot}.png")
                    self.assertEqual((128, 128, 4), (image.width, image.height, image.channels))

    def test_observation_matches_textures_and_contract(self) -> None:
        self.assertEqual("material.v1", self.observation["schema_version"])
        self.assertEqual("m04-procedural-kit.v1", self.observation["observation_id"])
        self.assertEqual(4, len(self.observation["materials"]))
        for material in self.observation["materials"]:
            with self.subTest(id=material["material_id"]):
                self.assertIn(material["alpha_mode"], ("opaque", "mask", "blend"))
                self.assertIn(material["cull_mode"], ("back", "front", "disabled"))
                self.assertIn(material["quality_variant"], ("high", "medium", "low"))
                self.assertEqual(3, len(material["textures"]))
                for texture in material["textures"]:
                    path = TEXTURES / Path(texture["uri"]).name
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), texture["sha256"])
                    self.assertEqual(texture["srgb"], texture["slot"] == "albedo")
        self.assertEqual("UNAVAILABLE", self.observation["performance"]["measurement_status"])
        self.assertEqual("headless", self.observation["provenance"]["capture_mode"])
        self.assertEqual(40, len(self.observation["provenance"]["base_sha"]))

    def test_materials_are_data_only(self) -> None:
        for material_id in IDS:
            text = (MATERIALS / f"{material_id}.tres").read_text(encoding="utf-8")
            with self.subTest(id=material_id):
                self.assertIn('type="StandardMaterial3D"', text)
                self.assertIn(f"res://textures/{material_id}_albedo.png", text)
                self.assertIn(f"res://textures/{material_id}_normal.png", text)
                self.assertIn(f"res://textures/{material_id}_orm.png", text)
                self.assertNotIn("ShaderMaterial", text)
                self.assertNotIn("shader_parameter", text)

    def test_headless_load_log_is_evidence(self) -> None:
        text = LOG.read_text(encoding="utf-8")
        self.assertIn("KIT_LOAD_OK 28 checks", text)
        self.assertEqual(4, text.count("KIT_MATERIAL_OK"))
        self.assertNotIn("KIT_LOAD_FAIL", text)

    def test_no_rendering_or_quality_claim(self) -> None:
        for path in (REPORT, KIT / "README.md"):
            lowered = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path.name):
                self.assertNotIn("fps improved", lowered)
                self.assertNotIn("quality verified", lowered)
                self.assertNotIn("rendered benchmark", lowered)


if __name__ == "__main__":
    unittest.main()

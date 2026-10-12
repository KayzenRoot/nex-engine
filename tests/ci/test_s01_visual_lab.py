"""S01 visual-lab static contract checks in the existing required Fast Lane.

No Godot native import or GPU test is implied by these source-integrity cases.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCENES = ROOT / "nex_bench" / "scenes" / "base"
FIXTURES = ROOT / "nex_bench" / "fixtures" / "base"
IDS = ("corridor_static", "arena_combat", "dense_city")


class SceneVisualLabContractTests(unittest.TestCase):
    def test_three_scene_hashes_match_fixtures_and_index(self):
        index = json.loads((FIXTURES / "manifest.v1.json").read_text(encoding="utf-8"))
        self.assertEqual({x["id"] for x in index["scenes"]}, set(IDS))
        self.assertEqual(index["measurement"], "NOT_MEASURED")
        for record in index["scenes"]:
            with self.subTest(scene=record["id"]):
                name = record["id"]
                data = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
                actual = hashlib.sha256((SCENES / f"{name}.tscn").read_bytes()).hexdigest()
                self.assertEqual(data["schema_version"], "scene_manifest.v1")
                self.assertEqual(data["scene_id"], name)
                self.assertEqual(actual, data["scene_sha256"])
                self.assertEqual(actual, record["scene_sha256"])
                self.assertEqual(data["renderer_id"], "godot.forward_plus")
                self.assertEqual(data["camera"]["projection"], "perspective")
                self.assertEqual(data["assets"], [])

    def test_local_validator_matches_ci(self):
        result = subprocess.run(
            [sys.executable, str(SCENES / "verify_fixtures.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("S01 CONTENT INTEGRITY PASS: 3 scenes", result.stdout)

    def test_scenes_have_resolved_builtin_resources_and_camera(self):
        for name in IDS:
            with self.subTest(scene=name):
                scene = (SCENES / f"{name}.tscn").read_text(encoding="utf-8")
                declared = re.findall(r'\\[sub_resource type="[^"]+" id="([^"]+)"\\]', scene)
                referenced = re.findall(r'SubResource\\("([^"]+)"\\)', scene)
                self.assertEqual(len(declared), len(set(declared)))
                self.assertTrue(set(referenced).issubset(set(declared)))
                self.assertIn('[node name="IsometricCamera" type="Camera3D"', scene)
                self.assertIn('[node name="Sun" type="DirectionalLight3D"', scene)

    def test_standalone_project_and_viewer_scene_routes(self):
        project = (SCENES / "project.godot").read_text(encoding="utf-8")
        viewer = (SCENES / "viewer.gd").read_text(encoding="utf-8")
        view_scene = (SCENES / "viewer.tscn").read_text(encoding="utf-8")
        self.assertIn('run/main_scene="res://viewer.tscn"', project)
        self.assertIn('renderer/rendering_method="forward_plus"', project)
        self.assertIn('path="res://viewer.gd"', view_scene)
        for name in IDS:
            self.assertIn(f'res://{name}.tscn', viewer)
        for key in ("KEY_1", "KEY_2", "KEY_3"):
            self.assertIn(key, viewer)


if __name__ == "__main__":
    unittest.main()

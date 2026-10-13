#!/usr/bin/env python3
"""S01 fixture content-integrity checks. Stdlib only; not GPU rendering."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "nex_bench/fixtures/base/manifest.v1.json"
REQUIRED = {"corridor_static", "arena_combat", "dense_city"}

def verify():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    assert {x["id"] for x in index["scenes"]} == REQUIRED
    assert index["measurement"] == "NOT_MEASURED"
    for row in index["scenes"]:
        scene = ROOT / row["scene_path"]
        fixture = json.loads((ROOT / row["fixture_path"]).read_text(encoding="utf-8"))
        # Git may materialize this text scene as CRLF on Windows when
        # core.autocrlf is enabled. Fixture hashes describe canonical LF bytes.
        canonical_bytes = scene.read_bytes().replace(b"\r\n", b"\n")
        digest = hashlib.sha256(canonical_bytes).hexdigest()
        assert digest == row["scene_sha256"] == fixture["scene_sha256"], row["id"]
        assert fixture["schema_version"] == "scene_manifest.v1"
        assert fixture["scene_id"] == row["id"]
        assert fixture["seed"] == row["seed"]
        assert fixture["renderer_id"] == "godot.forward_plus"
        assert fixture["assets"] == []
        assert fixture["camera"]["projection"] == "perspective"
        assert fixture["camera"]["far_clip_m"] > fixture["camera"]["near_clip_m"]
        print(f"VERIFIED {row['id']}: {digest}")
    print("S01 CONTENT INTEGRITY PASS: 3 scenes. Godot runtime still requires separate test.")

if __name__ == "__main__":
    verify()

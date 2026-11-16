"""Acceptance tests for the M06 performance reference gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "docs" / "benchmarks" / "m06"
RUNTIME = PACK / "m06-runtime.v1.json"
GATE = PACK / "M06-FINAL-GATE.md"
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m06"
MODULES = EVIDENCE / "modules-smoke-2026-11-16.json"
STREAM = EVIDENCE / "stream-smoke-2026-11-16.json"
VRAM = EVIDENCE / "vram-smoke-2026-11-16.json"
ADR = REPO / ".engineering" / "decisions" / "NEX-ADR-0017-M06-FULL-REFERENCE-ADMISSION.md"
WO = REPO / ".engineering" / "work-orders" / "NEX-M06-FINAL-REFERENCE-WO-001.md"
LOCK = REPO / ".engineering" / "context-locks" / "NEX-M06-FINAL-REFERENCE-WO-001-EXECUTION.json"
CHECKPOINT = REPO / ".engineering" / "CHECKPOINT.json"
WORKFLOW = REPO / ".github" / "workflows" / "nex-ci-fastlane.yml"


class M06FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.modules = json.loads(MODULES.read_text(encoding="utf-8"))
        cls.stream = json.loads(STREAM.read_text(encoding="utf-8"))
        cls.vram = json.loads(VRAM.read_text(encoding="utf-8"))
        cls.manifest = json.loads((EVIDENCE / "runs.v1.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))

    def test_governance_files_exist(self) -> None:
        for path in (ADR, WO, LOCK, RUNTIME, GATE, MODULES, STREAM, VRAM,
                     EVIDENCE / "runs.v1.json", EVIDENCE / "SHA256SUMS.txt"):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

    def test_manifest_has_33_validated_runs(self) -> None:
        self.assertEqual("m06_lab_runs.v1", self.manifest["schema_version"])
        self.assertEqual(self.runtime["source_sha"], self.manifest["source_sha"])
        self.assertEqual(33, len(self.manifest["runs"]))
        for entry in self.manifest["runs"]:
            with self.subTest(run=entry["run_id"]):
                self.assertTrue((EVIDENCE / entry["file"]).is_file())
                self.assertTrue((EVIDENCE / f"{entry['file']}.validation.json").is_file())

    def test_smokes_pass(self) -> None:
        self.assertEqual("PASS", self.modules["verdict"])
        self.assertEqual(78, self.modules["checks"])
        self.assertEqual([], self.modules["failures"])
        self.assertEqual("PASS", self.stream["verdict"])
        self.assertEqual(17, self.stream["checks"])
        self.assertEqual([], self.stream["failures"])
        self.assertEqual("PASS", self.vram["verdict"])
        self.assertEqual(9, self.vram["checks"])
        self.assertEqual([], self.vram["failures"])

    def test_bottleneck_atlas_covers_the_runs(self) -> None:
        self.assertEqual("BOTTLENECK_ATLAS_DERIVED", self.runtime["s01"]["verdict"])
        self.assertEqual(33, sum(self.runtime["s01"]["classifications"].values()))
        self.assertGreater(self.runtime["s01"]["classifications"].get("gpu", 0), 0)
        self.assertGreater(self.runtime["s01"]["classifications"].get("pacing", 0), 0)

    def test_batch_weave_reduces_draw_calls(self) -> None:
        rows = self.runtime["s02"]["rows"]
        self.assertEqual(9, len(rows))
        corridor = {row["variant"]: row for row in rows if row["scene"] == "corridor_static"}
        self.assertLess(corridor["multimesh"]["draw_calls"], corridor["individual"]["draw_calls"])
        self.assertLess(corridor["multimesh"]["draw_calls"], corridor["batched"]["draw_calls"])
        self.assertEqual(0.0, corridor["multimesh"]["changed_pixels_pct"])
        self.assertLess(corridor["multimesh"]["cpu_vs_individual_pct"], 0.0)
        self.assertEqual("BATCH_WEAVE_GO", self.runtime["s02"]["verdict"])

    def test_lod_governor_is_conservative(self) -> None:
        rows = self.runtime["s03"]["rows"]
        self.assertEqual(3, len(rows))
        for row in rows:
            with self.subTest(scene=row["scene"]):
                self.assertLess(row["governor_gpu_p95_ms"], row["high_gpu_p95_ms"])
                self.assertGreater(row["changed_pixels_pct"], 0.0)
                self.assertGreater(row["psnr_db"], 30.0)
        self.assertEqual("LOD_GOVERNOR_GO_WITH_LIMITATIONS", self.runtime["s03"]["verdict"])

    def test_custom_frustum_is_rejected(self) -> None:
        rows = self.runtime["s04"]["rows"]
        self.assertEqual(3, len(rows))
        self.assertEqual("INCONCLUSIVE_NOT_BAKED", self.runtime["s04"]["occlusion_culling"])
        self.assertEqual("CUSTOM_FRUSTUM_NO_GO", self.runtime["s04"]["verdict"])
        arena = next(row for row in rows if row["scene"] == "arena_combat")
        self.assertGreater(arena["changed_pixels_pct"], 0.0)

    def test_stream_guard_loads_three_scenes(self) -> None:
        self.assertEqual(17, self.runtime["s05"]["checks"])
        self.assertEqual(3, len(self.runtime["s05"]["timings"]))
        self.assertEqual(3, self.runtime["s05"]["counts"]["ready"])
        self.assertEqual("STREAM_GUARD_GO_WITH_LIMITATIONS", self.runtime["s05"]["verdict"])

    def test_render_scale_reduces_gpu(self) -> None:
        rows = {row["tag"]: row for row in self.runtime["s06"]["rows"]}
        self.assertLess(rows["scale_085"]["gpu_p95_ms"], rows["scale_100"]["gpu_p95_ms"])
        self.assertLess(rows["scale_070"]["gpu_p95_ms"], rows["scale_085"]["gpu_p95_ms"])
        self.assertGreater(rows["scale_070"]["changed_pixels_pct"], 0.0)
        self.assertEqual("FRAMEPACER_RESEARCH_GO_WITH_LIMITATIONS", self.runtime["s06"]["verdict"])

    def test_decisions_are_conservative(self) -> None:
        decisions = {item["id"]: item["decision"] for item in self.runtime["s07"]["decisions"]}
        self.assertEqual("GO", decisions["BatchWeave / MultiMesh"])
        self.assertEqual("NO_GO", decisions["Occlusion Mapper / custom frustum"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["LOD Governor"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["VRAM Sentinel"])
        self.assertEqual("GO_WITH_LIMITATIONS", decisions["FillRate X-Ray"])

    def test_vram_and_fillrate_are_measured(self) -> None:
        self.assertGreater(self.runtime["s09"]["delta_bytes"], 0)
        self.assertEqual(22, self.runtime["s09"]["textures_loaded"])
        self.assertEqual("OK", self.runtime["s09"]["evaluation"]["state"])
        rows = self.runtime["s10"]["rows"]
        self.assertEqual(9, len(rows))
        self.assertGreater(self.runtime["s10"]["resolution_scaling"]["1"]["1440p_vs_720p_pct"], 100.0)
        self.assertEqual("FILL_RATE_XRAY_GO_WITH_LIMITATIONS", self.runtime["s10"]["verdict"])

    def test_checkpoint_block_records_the_admission(self) -> None:
        block = self.checkpoint["m06FinalReference"]
        self.assertEqual("NEX-M06-FINAL-REFERENCE-WO-001", block["id"])
        self.assertEqual([11, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68], block["issues"])
        self.assertEqual("M06_REFERENCE_PERFORMANCE_ONLY", block["runtimeAdmission"])
        self.assertFalse(block["ciRelaxation"])
        self.assertEqual("ADMIN_SOLO_NOT_INDEPENDENT", block["audit"])

    def test_builder_is_enforced(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/m06/tools/build_m06_runtime.py --check", workflow)

    def test_gate_covers_the_closed_issues(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in ("#59", "#60", "#61", "#62", "#63", "#64", "#65", "#66", "#67", "#68", "#11",
                       "M06_PERFORMANCE_REFERENCE_COMPLETE", "Nenhuma paridade com PoE2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_false_independent_approval(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (ADR, WO, GATE))
        self.assertNotIn("INDEPENDENT_APPROVED", combined)
        self.assertIn("ADMIN_SOLO / NOT_INDEPENDENT", combined)


if __name__ == "__main__":
    unittest.main()

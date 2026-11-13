#!/usr/bin/env python3
"""Build or verify the NEX M01 baseline audit manifest.

Usage:
  python build_manifest.py [--head <sha>] [--check]

--check recomputes every referenced digest and compares with manifest.json.
No network, no writes outside manifest.json when building.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PACK = Path(__file__).resolve().parents[1]
MANIFEST = PACK / "manifest.json"
BASE_SHA = "871fd1bc89c272ba04327ddc81e407d35ff5fee0"

ARTIFACTS = [
    (".nex/toolchain/NEX-M00-WO-001-toolchain-lock.json", "toolchain"),
    ("contracts/m01/scene_manifest.v1.schema.json", "contract"),
    ("contracts/m01/telemetry_run.v1.schema.json", "contract"),
    ("contracts/m01/ownership.v1.json", "contract"),
    ("contracts/m02/render_core.v1.schema.json", "contract"),
    ("contracts/m07/render2d.v1.schema.json", "contract"),
    ("nex_bench/telemetry/fixtures/synthetic_run.v1.json", "s02-fixture"),
    ("nex_bench/telemetry/framepulse.py", "s02-implementation"),
    ("tests/telemetry/test_framepulse.py", "s02-test"),
    ("nex_bench/visual_truth/compare.py", "s03-implementation"),
    ("tests/ci/test_visual_truth.py", "s03-test"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/R9-PARTIAL-REPORT.md", "s04-report"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/HISTORICAL-PRESERVATION-CHECK.txt", "s04-preservation"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/SHA256SUMS.txt", "s04-sums"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/GUI-INITIAL.png", "s04-visual"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/GPU-F9-DIAGNOSTICS-AFTER-FOCUS.png", "s04-visual"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-13-r9-qualification/SCENE-25-GEOMETRY-PRE-RUN.png", "s04-visual"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/RESUMPTION-REPORT.md", "s04-resumption-report"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577762-42755782.json", "s04-run"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577762-42755782.validation.json", "s04-validation"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577798-78108593.json", "s04-run"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577798-78108593.validation.json", "s04-validation"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577830-110647047.json", "s04-run"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577830-110647047.validation.json", "s04-validation"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577863-143192521.json", "s04-run"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-r9-resumption/gpu_profile_1794577863-143192521.validation.json", "s04-validation"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05/SESSION-FACTS.txt", "s05-facts"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05/ANALYSIS.md", "s05-analysis"),
    ("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05/SHA256SUMS.txt", "s05-sums"),
    ("docs/research/nex-m01/RADAR-RD-2026-11-13.md", "s06-radar"),
    ("docs/research/nex-m01/EXPERIMENT-BACKLOG.md", "s06-backlog"),
    ("tests/ci/test_research_notes.py", "s06-test"),
    ("qa/bug-reports/NEX-QA-AUDIT-WO-001/REPORT.md", "qa-report"),
    ("qa/bug-reports/NEX-QA-AUDIT-WO-001/FUZZ-RESULTS.json", "qa-results"),
    ("tests/ci/test_qa_audit_regressions.py", "qa-regression-test"),
    ("nex_bench/scenes/lighting_matrix/lighting_matrix.gd", "s05-implementation"),
    ("nex_bench/scenes/lighting_matrix/lighting_matrix.tscn", "s05-scene"),
    ("nex_bench/presets/lighting_matrix/presets.v1.json", "s05-presets"),
    ("nex_bench/scenes/lighting_matrix/validate_lighting_matrix.py", "s05-validator"),
    ("tests/ci/test_lighting_matrix.py", "s05-test"),
    ("docs/benchmarks/m01/budget.v1.json", "budget"),
]

S05_EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-13-s05"
for json_path in sorted(S05_EVIDENCE.glob("gpu_profile_*.json")):
    relative = json_path.relative_to(REPO).as_posix()
    if json_path.name.endswith(".s05-validation.json"):
        ARTIFACTS.append((relative, "s05-validation"))
    else:
        ARTIFACTS.append((relative, "s05-run"))
        ARTIFACTS.append((relative + ".s05-validation.json", "s05-validation"))


def git_head() -> str:
    result = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise SystemExit("cannot resolve git HEAD")
    return result.stdout.strip()


def staged_blob(relative: str) -> bytes:
    """Return the index blob bytes so CRLF checkouts cannot change the recorded digest."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "cat-file", "blob", ":" + relative],
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"ARTIFACT NOT STAGED: {relative}")
    return result.stdout


def sha256_blob(relative: str) -> tuple[str, int]:
    content = staged_blob(relative)
    return hashlib.sha256(content).hexdigest(), len(content)


def artifact_entries() -> list[dict]:
    entries = []
    seen = set()
    for relative, kind in ARTIFACTS:
        if relative in seen:
            continue
        seen.add(relative)
        path = REPO / relative
        if not path.is_file():
            raise SystemExit(f"MISSING ARTIFACT: {relative}")
        digest, size = sha256_blob(relative)
        entries.append({"path": relative, "kind": kind, "sha256": digest, "bytes": size})
    return entries


def build(head_sha: str | None = None) -> dict:
    return {
        "schema_version": "nex_m01_baseline_manifest.v1",
        "status": "FROZEN_PROPOSED",
        "work_order": "NEX-M01-S07-WO-001",
        "issue": 27,
        "audit": "ADMIN_SOLO_NOT_INDEPENDENT",
        "base_sha": BASE_SHA,
        "head_sha_at_manifest_generation": head_sha or git_head(),
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "godot": {
            "tag": "4.7.2-stable",
            "commit": "ed1daf0bf001b61586d9930840f2f1394092c079",
            "binary_sha256": "ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424",
        },
        "hardware": {
            "gpu": "NVIDIA GeForce RTX 5050",
            "driver": "617.14",
            "os": "Windows 11 build 26300",
            "host_ram": "not audited",
        },
        "settings": {"renderer": "forward_plus", "driver": "vulkan", "viewport": [1280, 720], "vsync": 1, "max_fps": 0},
        "matrices": {
            "s02": {"status": "SYNTHETIC_NOT_MEASURED", "fixture": "nex_bench/telemetry/fixtures/synthetic_run.v1.json"},
            "s03": {"status": "SYNTHETIC_COMPARATOR_TESTED", "implementation": "nex_bench/visual_truth/compare.py"},
            "s04": {"status": "12_OF_12_COMPLETE", "counts": [25, 50, 100, 200], "combined_max": 25,
                     "invalid_runs": ["1791933080-760888025"], "invalid_reason": "invalid_monotonic_tick",
                     "validator": "nex_bench/gpu_profile/validate_gpu_profile.py"},
            "s05": {"status": "15_OF_15_COMPLETE", "counts": [25, 100, 200], "combined_max": 25,
                     "baseline_repetitions": 3, "validator": "nex_bench/scenes/lighting_matrix/validate_lighting_matrix.py"},
            "s06": {"status": "RESEARCH_ONLY", "candidates": 10},
        },
        "artifacts": artifact_entries(),
        "claims": {
            "engine_complete": False,
            "targets_achieved": False,
            "gpu_benchmark_claim": False,
            "cross_session_comparison_allowed": False,
            "headless_or_ci_as_gpu_benchmark": False,
        },
        "budget": "docs/benchmarks/m01/budget.v1.json",
        "checkpoint_delta": ".engineering/checkpoint-deltas/NEX-M01-S07-WO-001-PROPOSED.md",
    }


def check() -> int:
    if not MANIFEST.is_file():
        print("MISSING manifest.json")
        return 1
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fresh = build(existing.get("head_sha_at_manifest_generation"))
    if fresh["artifacts"] != existing.get("artifacts"):
        print("ARTIFACT DIGESTS DIVERGED")
        return 1
    if fresh["claims"] != existing.get("claims"):
        print("CLAIMS BLOCK DIVERGED")
        return 1
    print(f"MANIFEST_OK artifacts={len(fresh['artifacts'])}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", default=BASE_SHA)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    MANIFEST.write_text(json.dumps(build(args.head), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MANIFEST_WRITTEN artifacts={len(json.loads(MANIFEST.read_text(encoding='utf-8'))['artifacts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

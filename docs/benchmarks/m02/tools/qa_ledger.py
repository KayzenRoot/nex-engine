#!/usr/bin/env python3
"""Build or verify the NEX M02 QA ledger.

Usage:
  python qa_ledger.py --write
  python qa_ledger.py --check

The ledger compares the frozen M01 baseline against each S01-S06 improvement.
A scene or performance PASS is rejected unless its own evidence is present.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parents[1] / "qa-ledger.v1.json"
CONTRACT = REPO / "docs" / "benchmarks" / "m02" / "qa-contract.v1.json"
BASELINE = REPO / "docs" / "benchmarks" / "m01" / "manifest.json"
INTERFACE = "docs/benchmarks/m02/INTERFACE-M03-M06.md"
SOURCE_SHA = "9b40dac928d568cb7783b9e8ae830f35fa2acc21"
SCENES = ["corridor_static", "arena_combat", "dense_city"]
COMPONENTS = [
    {"id": "S01", "name": "Isometric camera", "module": "nex_modules/render3d/camera/",
     "structural_checks": 32, "evidence": ["nex_modules/render3d/camera/evidence/headless-smoke-2026-11-13.log"],
     "structural_status": "PASS", "scene_comparison": "INCONCLUSIVE_NOT_RUN",
     "performance": "INCONCLUSIVE_NOT_RUN", "note": "Structural smoke only; real-scene A/B/A not run."},
    {"id": "S02", "name": "Sightline reveal", "module": "nex_modules/render3d/sightline/",
     "structural_checks": 49, "evidence": ["nex_modules/render3d/sightline/evidence/headless-smoke-2026-11-13.log"],
     "structural_status": "PASS", "scene_comparison": "INCONCLUSIVE_NOT_RUN",
     "performance": "INCONCLUSIVE_NOT_RUN", "note": "Mock occluders only; real obscurance not measured."},
    {"id": "S03", "name": "DepthWeave composition", "module": "nex_modules/render3d/depth_composition/",
     "structural_checks": 37, "evidence": ["nex_modules/render3d/depth_composition/evidence/headless-smoke-2026-11-13.log"],
     "structural_status": "PASS", "scene_comparison": "INCONCLUSIVE_NOT_RUN",
     "performance": "INCONCLUSIVE_NOT_RUN", "note": "Mock spheres; z-fighting on real meshes not measured."},
    {"id": "S04", "name": "TemporalGuard gate", "module": "nex_modules/render3d/temporal/",
     "structural_checks": 51, "evidence": ["nex_modules/render3d/temporal/evidence/headless-smoke-2026-11-13.log"],
     "structural_status": "PASS", "scene_comparison": "INCONCLUSIVE_NOT_RUN",
     "performance": "INCONCLUSIVE_NOT_RUN", "note": "Synthetic sequences; real TAA/upscale not measured."},
    {"id": "S05", "name": "RenderPassport profiles", "module": "nex_modules/render3d/profiles/",
     "structural_checks": 87, "evidence": ["nex_modules/render3d/profiles/evidence/headless-smoke-2026-11-13.log"],
     "structural_status": "PASS", "scene_comparison": "INCONCLUSIVE_NOT_RUN",
     "performance": "INCONCLUSIVE_NOT_RUN", "note": "Capability states documented, not probed on real scenes."},
    {"id": "S06", "name": "R&D decision atlas", "module": "docs/research/nex-m02/",
     "structural_checks": 16, "evidence": ["docs/research/nex-m02/hypotheses.v1.json"],
     "structural_status": "PASS", "scene_comparison": "NOT_APPLICABLE_RESEARCH",
     "performance": "NOT_APPLICABLE_RESEARCH", "note": "Research only; no rendering claim."},
]
SCENE_STATUSES = {"PASS", "FAIL", "INCONCLUSIVE_NOT_RUN", "NOT_APPLICABLE_RESEARCH", "BLOCKED"}
PERFORMANCE_STATUSES = {"MEASURED", "INCONCLUSIVE_NOT_RUN", "NOT_APPLICABLE_RESEARCH", "BLOCKED"}
STRUCTURAL_STATUSES = {"PASS", "FAIL", "BLOCKED"}


def staged_blob(relative: str) -> bytes:
    """Hash committed content, not a CRLF-converted working-tree checkout."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "cat-file", "blob", ":" + relative],
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"EVIDENCE NOT IN THE GIT INDEX: {relative}")
    return result.stdout


def staged_sha(relative: str) -> tuple[str, int]:
    content = staged_blob(relative)
    return hashlib.sha256(content).hexdigest(), len(content)


def _evidence_entries(component: dict) -> list[dict]:
    entries = []
    for relative in component["evidence"]:
        if not (REPO / relative).is_file():
            raise SystemExit(f"MISSING EVIDENCE: {relative}")
        digest, size = staged_sha(relative)
        entries.append({"path": relative, "sha256": digest, "bytes": size})
    return entries


def build() -> dict:
    components = []
    for component in COMPONENTS:
        entry = {key: value for key, value in component.items() if key != "evidence"}
        entry["evidence"] = _evidence_entries(component)
        components.append(entry)
    return {
        "schema_version": "nex_m02_qa_ledger.v1",
        "source_sha": SOURCE_SHA,
        "baseline": {"manifest": str(BASELINE.relative_to(REPO)).replace("\\", "/"),
                     "sha256": staged_sha(str(BASELINE.relative_to(REPO)).replace("\\", "/"))[0]},
        "contract": {"path": str(CONTRACT.relative_to(REPO)).replace("\\", "/"),
                     "sha256": staged_sha(str(CONTRACT.relative_to(REPO)).replace("\\", "/"))[0]},
        "components": components,
        "scenes": SCENES,
        "targets": {
            "quality_1080p60": "ASPIRATIONAL_NOT_MEASURED",
            "performance_120": "EXPERIMENTAL_NOT_MEASURED",
        },
        "defects": {"high": 0, "critical": 0},
        "integration": {"mode": "SERIAL_STEWARD", "conflicts": 0, "pending_external_prs": 0},
        "security": {"new_high_critical": 0, "new_assets": False},
        "claims": {"scene_pass": False, "measured_gain": False, "performance_attained": False},
        "interface": INTERFACE,
    }


def _validate_component(component: dict, index: int, errors: list[str]) -> None:
    label = f"components[{index}]"
    for key in ("id", "name", "module", "structural_checks", "structural_status",
                "scene_comparison", "performance", "evidence", "note"):
        if key not in component:
            errors.append(f"{label}: missing {key}")
    if component.get("structural_status") not in STRUCTURAL_STATUSES:
        errors.append(f"{label}: invalid structural_status")
    if component.get("scene_comparison") not in SCENE_STATUSES:
        errors.append(f"{label}: invalid scene_comparison")
    if component.get("performance") not in PERFORMANCE_STATUSES:
        errors.append(f"{label}: invalid performance")
    evidence = component.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label}: evidence is required")
        return
    for item in evidence:
        if not isinstance(item, dict) or len(str(item.get("sha256", ""))) != 64:
            errors.append(f"{label}: evidence entry needs a SHA-256")
    if component.get("structural_status") == "PASS" and not evidence:
        errors.append(f"{label}: PASS without evidence")
    if component.get("scene_comparison") == "PASS" and not component.get("scene_evidence"):
        errors.append(f"{label}: scene PASS without scene_evidence")
    if component.get("performance") == "MEASURED" and not component.get("performance_evidence"):
        errors.append(f"{label}: measured performance without performance_evidence")


def validate(ledger: dict) -> list[str]:
    if not isinstance(ledger, dict):
        return ["ledger must be an object"]
    errors: list[str] = []
    if ledger.get("schema_version") != "nex_m02_qa_ledger.v1":
        errors.append("unsupported schema_version")
    components = ledger.get("components")
    if not isinstance(components, list) or len(components) != 6:
        errors.append("exactly six components are required")
    else:
        seen = set()
        for index, component in enumerate(components):
            if not isinstance(component, dict):
                errors.append(f"components[{index}] must be an object")
                continue
            if component.get("id") in seen:
                errors.append(f"duplicate component id: {component.get('id')}")
            seen.add(component.get("id"))
            _validate_component(component, index, errors)
    if ledger.get("defects", {}).get("high", 0) != 0 or ledger.get("defects", {}).get("critical", 0) != 0:
        errors.append("HIGH/CRITICAL defects block acceptance")
    if ledger.get("integration", {}).get("conflicts", 0) != 0:
        errors.append("integration conflicts must be zero")
    if ledger.get("integration", {}).get("mode") != "SERIAL_STEWARD":
        errors.append("integration must be SERIAL_STEWARD")
    claims = ledger.get("claims", {})
    if any(bool(value) for value in claims.values()):
        errors.append("claims must be false without measured evidence")
    targets = ledger.get("targets", {})
    if targets.get("quality_1080p60") != "ASPIRATIONAL_NOT_MEASURED" or targets.get("performance_120") != "EXPERIMENTAL_NOT_MEASURED":
        errors.append("performance targets must remain unmeasured")
    if ledger.get("scenes") != SCENES:
        errors.append("the three canonical M01 scenes are required")
    if ledger.get("interface") != INTERFACE:
        errors.append("interface document path is required")
    return errors


def check(ledger: dict) -> list[str]:
    errors = validate(ledger)
    if errors:
        return errors
    fresh = build()
    if fresh["components"] != ledger.get("components"):
        errors.append("component evidence digests diverged")
    for key in ("baseline", "contract", "targets", "defects", "integration", "security", "claims"):
        if fresh[key] != ledger.get(key):
            errors.append(f"{key} block diverged")
    return errors


def main(argv: list[str]) -> int:
    write_mode = "--write" in argv
    if write_mode:
        OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("QA_LEDGER_WRITTEN")
        return 0
    if not OUTPUT.is_file():
        print("MISSING qa-ledger.v1.json")
        return 1
    errors = check(json.loads(OUTPUT.read_text(encoding="utf-8")))
    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print("QA_LEDGER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

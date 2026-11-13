#!/usr/bin/env python3
"""Deterministic GO/NO_GO/RESEARCH_MORE rules for NEX M02 R&D hypotheses.

Usage:
  python decision_engine.py hypotheses.v1.json
  python decision_engine.py --check hypotheses.v1.json

The engine only recommends. Owner decisions remain PENDING and are never
inferred, approved or auto-promoted by this tool.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DECISIONS = {"GO", "NO_GO", "RESEARCH_MORE"}
KINDS = {"render_feature", "process_tool"}
GAPS = {"NONE", "MEASURED", "PARTIAL", "UNKNOWN"}
ALTERNATIVES = {"config", "shader", "addon", "none"}
RISKS = {"NONE", "LOW", "MEDIUM", "HIGH"}
LICENSES = {"NONE", "COMPATIBLE", "INCOMPATIBLE"}
COMPAT = {"COMPATIBLE", "CONFLICTS", "UNKNOWN"}
EVIDENCE = {"MEASURED", "PROTOTYPE_VERIFIED", "NOT_MEASURED", "INCONCLUSIVE"}
COSTS = {"NONE", "LOW", "MEDIUM", "HIGH"}


class HypothesisError(ValueError):
    pass


def recommend(hypothesis: dict) -> tuple[str, str]:
    """Return (decision, reason). Rules are ordered and total."""
    if hypothesis.get("kind") == "process_tool":
        if (hypothesis.get("evidence_status") == "PROTOTYPE_VERIFIED"
                and hypothesis.get("visual_risk") in ("NONE", "LOW")
                and hypothesis.get("rollback")):
            return "GO", "PROCESS_TOOL_PROTOTYPE_VERIFIED"
        return "RESEARCH_MORE", "PROCESS_TOOL_NEEDS_EVIDENCE"
    if hypothesis.get("redundant_with_native") or hypothesis.get("native_gap") == "NONE":
        return "NO_GO", "NATIVE_SUFFICIENT"
    if hypothesis.get("evidence_status") != "MEASURED":
        return "RESEARCH_MORE", "EVIDENCE_NOT_MEASURED"
    if hypothesis.get("visual_risk") == "HIGH" or hypothesis.get("license_risk") == "INCOMPATIBLE":
        return "NO_GO", "HIGH_RISK_OR_LICENSE"
    if not hypothesis.get("rollback"):
        return "NO_GO", "NO_ROLLBACK"
    if hypothesis.get("simplest_alternative") in ("config", "shader", "addon"):
        return "RESEARCH_MORE", "SIMPLER_ALTERNATIVE_FIRST"
    return "GO", "MEASURED_GAP_ROLLBACK_READY"


def validate(document: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["document must be an object"]
    if document.get("schema_version") != "nex_m02_research_hypotheses.v1":
        errors.append("unsupported schema_version")
    hypotheses = document.get("hypotheses")
    if not isinstance(hypotheses, list) or not hypotheses:
        return errors + ["hypotheses must be a non-empty list"]
    seen: set[str] = set()
    for index, hypothesis in enumerate(hypotheses):
        label = f"hypotheses[{index}]"
        if not isinstance(hypothesis, dict):
            errors.append(label + " must be an object")
            continue
        required = ("id", "name", "kind", "owner_module", "touches_modules", "question",
                    "native_gap", "redundant_with_native", "simplest_alternative",
                    "data_contract", "cost", "visual_risk", "license_risk",
                    "compatibility_2_5d", "rollback", "benchmark", "metrics",
                    "evidence_status", "sources", "owner_decision", "recommended")
        for key in required:
            if key not in hypothesis:
                errors.append(f"{label}: missing {key}")
        if not errors:
            identifier = str(hypothesis["id"])
            if identifier in seen:
                errors.append(f"duplicate hypothesis id: {identifier}")
            seen.add(identifier)
            if not str(hypothesis["question"]).endswith("?"):
                errors.append(f"{label}: question must be refutable and end with '?'")
            if hypothesis["kind"] not in KINDS:
                errors.append(f"{label}: invalid kind")
            if hypothesis["native_gap"] not in GAPS:
                errors.append(f"{label}: invalid native_gap")
            if hypothesis["simplest_alternative"] not in ALTERNATIVES:
                errors.append(f"{label}: invalid simplest_alternative")
            if hypothesis["visual_risk"] not in RISKS:
                errors.append(f"{label}: invalid visual_risk")
            if hypothesis["license_risk"] not in LICENSES:
                errors.append(f"{label}: invalid license_risk")
            if hypothesis["compatibility_2_5d"] not in COMPAT:
                errors.append(f"{label}: invalid compatibility_2_5d")
            if hypothesis["evidence_status"] not in EVIDENCE:
                errors.append(f"{label}: invalid evidence_status")
            if hypothesis["recommended"] not in DECISIONS:
                errors.append(f"{label}: invalid recommended decision")
            if hypothesis["owner_decision"] != "PENDING":
                errors.append(f"{label}: owner_decision must remain PENDING")
            if hypothesis["owner_module"] not in hypothesis["touches_modules"]:
                errors.append(f"{label}: owner_module must be listed in touches_modules")
            if not isinstance(hypothesis["sources"], list) or not hypothesis["sources"]:
                errors.append(f"{label}: sources are required")
            else:
                for source in hypothesis["sources"]:
                    if not str(source).startswith("https://docs.godotengine.org/"):
                        errors.append(f"{label}: source is not official Godot documentation")
            benchmark = hypothesis["benchmark"]
            if not isinstance(benchmark, dict) or not all(key in benchmark for key in ("a", "b", "a2", "plan")):
                errors.append(f"{label}: A/B/A benchmark plan is required")
            cost = hypothesis["cost"]
            if not isinstance(cost, dict) or any(cost.get(key) not in COSTS for key in ("cpu", "gpu", "vram", "maintenance")):
                errors.append(f"{label}: invalid cost block")
    rejected = document.get("rejected_redundancies")
    if not isinstance(rejected, list) or not rejected:
        errors.append("rejected_redundancies must be a non-empty list")
    else:
        for index, entry in enumerate(rejected):
            if entry.get("decision") != "NO_GO":
                errors.append(f"rejected_redundancies[{index}] must be NO_GO")
            for key in ("id", "name", "reason", "source"):
                if not entry.get(key):
                    errors.append(f"rejected_redundancies[{index}]: missing {key}")
    return errors


def evaluate(document: dict) -> list[dict]:
    results = []
    for hypothesis in document.get("hypotheses", []):
        decision, reason = recommend(hypothesis)
        results.append({"id": hypothesis.get("id"), "name": hypothesis.get("name"),
                        "decision": decision, "reason": reason})
    return results


def check(document: dict) -> list[str]:
    errors = validate(document)
    if errors:
        return errors
    for hypothesis in document["hypotheses"]:
        decision, _ = recommend(hypothesis)
        if hypothesis["recommended"] != decision:
            errors.append(f"{hypothesis['id']}: recommended={hypothesis['recommended']} but engine={decision}")
    return errors


def main(argv: list[str]) -> int:
    args = [arg for arg in argv[1:] if arg != "--check"]
    check_mode = "--check" in argv
    path = Path(args[0]) if args else Path(__file__).resolve().parents[1] / "hypotheses.v1.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    errors = check(document) if check_mode else validate(document)
    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    for result in evaluate(document):
        print(f"{result['id']}: {result['decision']} ({result['reason']})")
    if check_mode:
        print("HYPOTHESES_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

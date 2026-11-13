#!/usr/bin/env python3
"""Deterministic GO/NO_GO/RESEARCH_MORE rules for NEX M02 R&D hypotheses.

Usage:
  python decision_engine.py
  python decision_engine.py --check

The input path is fixed next to this module; no caller-supplied path is read.
The engine only recommends. Owner decisions remain PENDING and are never
approved or promoted by this tool.
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
HYPOTHESIS_KEYS = (
    "id", "name", "kind", "owner_module", "touches_modules", "question",
    "native_gap", "redundant_with_native", "simplest_alternative",
    "data_contract", "cost", "visual_risk", "license_risk",
    "compatibility_2_5d", "rollback", "benchmark", "metrics",
    "evidence_status", "sources", "owner_decision", "recommended",
)


def recommend(hypothesis: dict) -> tuple[str, str]:
    """Return (decision, reason). Rules are ordered and total."""
    if hypothesis.get("kind") == "process_tool":
        verified = hypothesis.get("evidence_status") == "PROTOTYPE_VERIFIED"
        safe = hypothesis.get("visual_risk") in ("NONE", "LOW") and bool(hypothesis.get("rollback"))
        return ("GO", "PROCESS_TOOL_PROTOTYPE_VERIFIED") if verified and safe else (
            "RESEARCH_MORE", "PROCESS_TOOL_NEEDS_EVIDENCE")
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


def _check_enum(value, allowed: set[str], label: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{label}: invalid value {value!r}")


def _require_keys(hypothesis: dict, label: str, errors: list[str]) -> None:
    for key in HYPOTHESIS_KEYS:
        if key not in hypothesis:
            errors.append(f"{label}: missing {key}")


def _validate_sources(hypothesis: dict, label: str, errors: list[str]) -> None:
    sources = hypothesis.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{label}: sources are required")
        return
    for source in sources:
        if not str(source).startswith("https://docs.godotengine.org/"):
            errors.append(f"{label}: source is not official Godot documentation")


def _validate_benchmark_and_cost(hypothesis: dict, label: str, errors: list[str]) -> None:
    benchmark = hypothesis.get("benchmark")
    if not isinstance(benchmark, dict) or any(key not in benchmark for key in ("a", "b", "a2", "plan")):
        errors.append(f"{label}: A/B/A benchmark plan is required")
    cost = hypothesis.get("cost")
    if not isinstance(cost, dict):
        errors.append(f"{label}: invalid cost block")
        return
    for key in ("cpu", "gpu", "vram", "maintenance"):
        _check_enum(cost.get(key), COSTS, f"{label}.cost.{key}", errors)


def _validate_hypothesis_values(hypothesis: dict, label: str, errors: list[str]) -> None:
    _check_enum(hypothesis.get("kind"), KINDS, f"{label}.kind", errors)
    _check_enum(hypothesis.get("native_gap"), GAPS, f"{label}.native_gap", errors)
    _check_enum(hypothesis.get("simplest_alternative"), ALTERNATIVES, f"{label}.simplest_alternative", errors)
    _check_enum(hypothesis.get("visual_risk"), RISKS, f"{label}.visual_risk", errors)
    _check_enum(hypothesis.get("license_risk"), LICENSES, f"{label}.license_risk", errors)
    _check_enum(hypothesis.get("compatibility_2_5d"), COMPAT, f"{label}.compatibility_2_5d", errors)
    _check_enum(hypothesis.get("evidence_status"), EVIDENCE, f"{label}.evidence_status", errors)
    _check_enum(hypothesis.get("recommended"), DECISIONS, f"{label}.recommended", errors)
    if not str(hypothesis.get("question", "")).endswith("?"):
        errors.append(f"{label}: question must be refutable and end with '?'")
    if hypothesis.get("owner_decision") != "PENDING":
        errors.append(f"{label}: owner_decision must remain PENDING")
    if hypothesis.get("owner_module") not in hypothesis.get("touches_modules", []):
        errors.append(f"{label}: owner_module must be listed in touches_modules")
    _validate_sources(hypothesis, label, errors)
    _validate_benchmark_and_cost(hypothesis, label, errors)


def _validate_hypothesis(hypothesis, label: str, errors: list[str], seen: set[str]) -> None:
    if not isinstance(hypothesis, dict):
        errors.append(label + " must be an object")
        return
    _require_keys(hypothesis, label, errors)
    identifier = str(hypothesis.get("id", ""))
    if identifier in seen:
        errors.append(f"duplicate hypothesis id: {identifier}")
    seen.add(identifier)
    _validate_hypothesis_values(hypothesis, label, errors)


def _validate_rejected(rejected, errors: list[str]) -> None:
    if not isinstance(rejected, list) or not rejected:
        errors.append("rejected_redundancies must be a non-empty list")
        return
    for index, entry in enumerate(rejected):
        if not isinstance(entry, dict):
            errors.append(f"rejected_redundancies[{index}] must be an object")
            continue
        if entry.get("decision") != "NO_GO":
            errors.append(f"rejected_redundancies[{index}] must be NO_GO")
        for key in ("id", "name", "reason", "source"):
            if not entry.get(key):
                errors.append(f"rejected_redundancies[{index}]: missing {key}")


def validate(document: dict) -> list[str]:
    if not isinstance(document, dict):
        return ["document must be an object"]
    errors: list[str] = []
    if document.get("schema_version") != "nex_m02_research_hypotheses.v1":
        errors.append("unsupported schema_version")
    hypotheses = document.get("hypotheses")
    if not isinstance(hypotheses, list) or not hypotheses:
        return errors + ["hypotheses must be a non-empty list"]
    seen: set[str] = set()
    for index, hypothesis in enumerate(hypotheses):
        _validate_hypothesis(hypothesis, f"hypotheses[{index}]", errors, seen)
    _validate_rejected(document.get("rejected_redundancies"), errors)
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
    check_mode = "--check" in argv
    document = json.loads((Path(__file__).resolve().parents[1] / "hypotheses.v1.json").read_text(encoding="utf-8"))
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

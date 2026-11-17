#!/usr/bin/env python3
"""Build the M09 editor-tools report from deterministic smoke evidence."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parents[1] / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from runtime_report import render_json, sha  # noqa: E402 - shared tool module

REPO = Path(__file__).resolve().parents[4]
SMOKE = REPO / "nex_modules" / "tools" / "editor_lab" / "evidence" / "m09-editor-smoke-2026-11-17.json"
RESOLVER_LOG = REPO / "nex_modules" / "tools" / "preset_resolver" / "evidence" / "headless-smoke-2026-11-13.log"
FIXTURES = REPO / "nex_modules" / "tools" / "editor_lab" / "fixtures"
OUTPUT = REPO / "docs" / "benchmarks" / "m09"
REPORT_JSON = OUTPUT / "editor-tools.v1.json"
REPORT_MD = OUTPUT / "EDITOR-TOOLS.md"
SOURCE_SHA = "371ca4ab4a5f70debc96e84bba55aba3870fc9cf"


def _resolver_checks() -> int:
    text = RESOLVER_LOG.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("NEX_M09_RESOLVER_SMOKE_PASS:"):
            return int(line.split(":", 1)[1].strip().split()[0])
    raise ValueError("resolver smoke has no pass line")


def build_report() -> dict[str, Any]:
    smoke = load_json(SMOKE)
    if smoke.get("schema_version") != "m09_editor_smoke.v1":
        raise ValueError("editor smoke schema is invalid")
    if smoke.get("source_sha") != SOURCE_SHA:
        raise ValueError("editor smoke source SHA is stale")
    if smoke.get("verdict") != "PASS" or smoke.get("failures") != []:
        raise ValueError("editor smoke did not pass")
    checks = int(smoke.get("checks", 0))
    if checks != 42:
        raise ValueError("editor smoke must contain 42 checks")
    resolver_checks = _resolver_checks()
    if resolver_checks != 50:
        raise ValueError("resolver smoke must contain 50 checks")
    lint = smoke["lint"]
    summary = lint["summary"]
    if int(summary["total"]) != 13 or int(summary["counts"]["error"]) != 4:
        raise ValueError("PerfLint summary is unexpected")
    plan = smoke["import_plan"]
    if plan["counts"] != {"accepted": 1, "rejected": 3, "noop": 2, "conflicts": 1}:
        raise ValueError("ImportGuard plan is unexpected")
    recipe = smoke["recipe"]
    if recipe.get("schema_version") != "nex_bench_recipe.v1":
        raise ValueError("recipe schema is unexpected")
    fixtures = sorted(FIXTURES.glob("*.json"))
    if len(fixtures) != 4:
        raise ValueError("editor lab must contain 4 fixtures")
    return {
        "schema_version": "m09_editor_tools.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-17",
        "s01": {"resolver_checks": resolver_checks, "verdict": "PRESET_RESOLVER_VERIFIED"},
        "s02": {"checks": checks, "findings": summary["total"],
                "errors": summary["counts"]["error"], "warns": summary["counts"]["warn"],
                "codes": summary["codes"], "highest": summary["highest"],
                "verdict": "PERFLINT_DERIVED"},
        "s03": {"counts": plan["counts"], "snapshot": smoke.get("import_snapshot", ""),
                "verdict": "IMPORT_GUARD_DERIVED"},
        "s04": {"recipe_id": recipe.get("recipe_id", ""), "scene_id": recipe.get("scene_id", ""),
                "preset_id": recipe.get("preset_id", ""), "seed": recipe.get("seed", 0),
                "driver": recipe.get("driver", ""), "runs": recipe.get("runs", 0),
                "verdict": "BENCHMARK_RECIPE_DERIVED"},
        "s05": {"checks": resolver_checks + checks, "fixtures": len(fixtures),
                "third_party_assets": 0, "verdict": "M09_EDITOR_QA_VERIFIED"},
        "decisions": [
            {"id": "PresetResolver / preset_pack.v1", "decision": "GO",
             "evidence": f"{resolver_checks} headless checks; no runtime application"},
            {"id": "PerfLint", "decision": "GO_WITH_LIMITATIONS",
             "evidence": f"{checks} checks; 13 deterministic findings (4 errors, 9 warns)"},
            {"id": "ImportGuard", "decision": "GO_WITH_LIMITATIONS",
             "evidence": "1 accepted / 3 rejected / 2 noop / 1 conflict; plan only, no writes"},
            {"id": "BenchmarkRecipe", "decision": "GO_WITH_LIMITATIONS",
             "evidence": "recipe generated and validated; no benchmark executed"},
        ],
        "fixtures": [{"name": path.name, "sha256": sha(path), "bytes": path.stat().st_size}
                     for path in fixtures],
        "verdict": "M09_EDITOR_TOOLS_REFERENCE_DERIVED",
        "observations": [
            "PresetResolver still passes 50 headless checks",
            "PerfLint reports 13 deterministic findings: 4 errors and 9 warnings",
            "ImportGuard plans 1 accepted, 3 rejected, 2 noop and 1 conflict without writing files",
            "BenchmarkRecipe builds a reproducible recipe with pinned driver and source SHA",
            "all editor tools run headless with deterministic fixtures",
        ],
        "limitations": [
            "fixtures only; no asset is imported, rendered or benchmarked",
            "PerfLint warnings are heuristics, not measured performance",
            "ImportGuard never writes; the real import pipeline remains future work",
            "no FPS, frame-time, VRAM or quality claim",
            "no production art, no PoE2 parity and no generalized claim",
        ],
        "runs": 1,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Editor tools",
        "",
        "**Status:** `M09_EDITOR_TOOLS_REFERENCE_DERIVED / HEADLESS_FIXTURES / NO_IMPORT_OR_RENDER / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **Engine:** Godot 4.7.2-stable",
        "",
        "## S01 · PresetResolver",
        "",
        f"- **{report['s01']['verdict']}**: {report['s01']['resolver_checks']} checks headless.",
        "",
        "## S02 · PerfLint",
        "",
        f"- **{report['s02']['verdict']}**: {report['s02']['checks']} checks; "
        f"{report['s02']['findings']} findings ({report['s02']['errors']} errors, "
        f"{report['s02']['warns']} warns); highest `{report['s02']['highest']}`.",
        "",
        "| Código | Ocorrências |",
        "|---|---:|",
    ]
    for code, count in sorted(report["s02"]["codes"].items()):
        lines.append(f"| {code} | {count} |")
    lines.extend([
        "",
        "## S03 · ImportGuard",
        "",
        f"- accepted **{report['s03']['counts']['accepted']}**, rejected **{report['s03']['counts']['rejected']}**, "
        f"noop **{report['s03']['counts']['noop']}**, conflicts **{report['s03']['counts']['conflicts']}**.",
        "- Plano determinístico; nenhum arquivo é escrito ou sobrescrito.",
        "",
        "## S04 · BenchmarkRecipe",
        "",
        f"- Recipe `{report['s04']['recipe_id']}`; scene `{report['s04']['scene_id']}`, "
        f"preset `{report['s04']['preset_id']}`, seed `{report['s04']['seed']}`, "
        f"driver `{report['s04']['driver']}`, runs `{report['s04']['runs']}`.",
        "",
        "## S05 · QA",
        "",
        f"- {report['s05']['checks']} checks totais; {report['s05']['fixtures']} fixtures; "
        f"{report['s05']['third_party_assets']} assets de terceiros.",
        "",
        "## Decisões",
        "",
        "| Tecnologia | Decisão | Evidência |",
        "|---|---|---|",
    ])
    for decision in report["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend(["", "## Observações", ""])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m09/tools/build_m09_editor_tools.py`; não é benchmark de jogo.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M09_EDITOR_TOOLS")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

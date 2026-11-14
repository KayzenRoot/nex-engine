#!/usr/bin/env python3
"""NEX M09 measurement atlas builder.

Indexes the eight integrated M09 evidence bundles, verifies their manifests and
report counts, extracts key measured values and writes a deterministic JSON/
Markdown atlas. No new measurement is performed and no general performance or
quality claim is made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli  # noqa: E402 - local tool module

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS = REPO_ROOT / "docs/benchmarks/m09"
EVIDENCE_ROOT = REPO_ROOT / "nex_bench/gpu_profile/evidence"
OUTPUT_DIR = DOCS
REPORT_JSON = DOCS / "measurement-atlas.v1.json"
REPORT_MD = DOCS / "MEASUREMENT-ATLAS.md"

REPORT_SCHEMA = "m09_measurement_atlas.v1"


def _evidence_path(name: str) -> Path:
    return EVIDENCE_ROOT / name


def _findings_preset_ab(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": report["deltas_high_vs_low"]["gpu_p95_pct"],
            "runs": len(report["runs"])}


def _findings_scaling(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": {
        count: value["gpu_p95_pct"] for count, value in report["deltas_high_vs_low"].items()
    }, "scaling_25_to_200_pct": report["scaling_25_to_200"]}


def _findings_m01_ab(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": {
        scene["scene_id"]: scene["deltas_high_vs_low"]["gpu_p95_pct"] for scene in report["scenes"]
    }}


def _findings_visual(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "aa_identical": all(scene["summary"]["aa_all_identical"] for scene in report["scenes"]),
        "ab_changed_pixels_pct": {
            scene["scene_id"]: scene["summary"]["ab_changed_pixels_pct_median"] for scene in report["scenes"]
        },
    }


def _findings_res_scaling(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": {
        key: value["gpu_p95_pct"] for key, value in report["deltas_high_vs_low"].items()
    }, "scaling_960_to_1920_pct": report["scaling_960_to_1920"]}


def _findings_interaction(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": {
        key: value["gpu_p95_pct"] for key, value in report["deltas_high_vs_low"].items()
    }, "resolution_scaling_pct": report["resolution_scaling"],
       "proxy_scaling_pct": report["proxy_scaling"]}


def _findings_cross_scene(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": {
        scene["scene_id"]: {
            key: value["gpu_p95_pct"] for key, value in scene["deltas_high_vs_low"].items()
        } for scene in report["scenes"]
    }}


def _findings_interaction_200(report: dict[str, Any]) -> dict[str, Any]:
    return {"gpu_p95_high_vs_low_pct": {
        key: value["gpu_p95_pct"] for key, value in report["deltas_high_vs_low"].items()
    }, "resolution_scaling_pct": report["resolution_scaling"],
       "context_100_to_200_pct": report["context_100_to_200"]}


ENTRIES: tuple[dict[str, Any], ...] = (
    {"id": "preset-ab", "kind": "performance", "report": "ab.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-preset-ab", "runs": 6, "files": 15,
     "findings": _findings_preset_ab},
    {"id": "proxy-scaling", "kind": "performance", "report": "scaling.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-preset-scaling", "runs": 18, "files": 39,
     "findings": _findings_scaling},
    {"id": "m01-ab", "kind": "performance", "report": "m01-ab.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-m01-ab", "runs": 18, "files": 39,
     "findings": _findings_m01_ab},
    {"id": "m01-visual", "kind": "visual", "report": "m01-visual.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-m01-visual", "runs": 18, "files": 21,
     "findings": _findings_visual},
    {"id": "res-scaling", "kind": "performance", "report": "res-scaling.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-res-scaling", "runs": 18, "files": 39,
     "findings": _findings_res_scaling},
    {"id": "interaction", "kind": "performance", "report": "interaction.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-interaction", "runs": 24, "files": 51,
     "findings": _findings_interaction},
    {"id": "cross-scene", "kind": "performance", "report": "cross-scene.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-cross-scene", "runs": 48, "files": 99,
     "findings": _findings_cross_scene},
    {"id": "interaction-200", "kind": "performance", "report": "interaction-200.v1.json",
     "evidence": "windows-rtx5050-2026-11-14-interaction-200", "runs": 12, "files": 27,
     "findings": _findings_interaction_200},
)


def _source_sha(report: dict[str, Any]) -> str:
    return str(report.get("source_sha") or report.get("harness_source_sha") or "")


def _load_entry(entry: dict[str, Any]) -> dict[str, Any]:
    report_path = DOCS / entry["report"]
    if not report_path.is_file():
        raise ValueError("report is missing: " + entry["report"])
    report = load_json(report_path)
    evidence = _evidence_path(entry["evidence"])
    manifest_path = evidence / "runs.v1.json"
    if not manifest_path.is_file():
        raise ValueError("evidence manifest is missing: " + entry["evidence"])
    manifest = load_json(manifest_path)
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != entry["runs"]:
        raise ValueError(f"{entry['id']}: manifest run count is invalid")
    sums_path = evidence / "SHA256SUMS.txt"
    if not sums_path.is_file():
        raise ValueError(f"{entry['id']}: SHA256SUMS is missing")
    file_count = len([line for line in sums_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    if file_count != entry["files"]:
        raise ValueError(f"{entry['id']}: evidence file count is invalid")
    source_sha = _source_sha(report)
    manifest_sha = str(manifest.get("source_sha") or manifest.get("harness_source_sha") or "")
    if not source_sha or source_sha != manifest_sha:
        raise ValueError(f"{entry['id']}: source SHA mismatch")
    findings: Callable[[dict[str, Any]], dict[str, Any]] = entry["findings"]
    return {
        "id": entry["id"],
        "kind": entry["kind"],
        "report": entry["report"],
        "evidence_bundle": "nex_bench/gpu_profile/evidence/" + entry["evidence"],
        "runs": entry["runs"],
        "evidence_files": file_count,
        "source_sha": source_sha,
        "verdict": report.get("verdict"),
        "key_findings": findings(report),
    }


def build_report() -> dict[str, Any]:
    entries = [_load_entry(entry) for entry in ENTRIES]
    performance_runs = sum(entry["runs"] for entry in entries if entry["kind"] == "performance")
    visual_images = sum(entry["runs"] for entry in entries if entry["kind"] == "visual")
    cross_findings = [
        "The high preset costs more GPU time than the low preset in every measured scene and cell; the relative cost grows with resolution.",
        "At 50-200 proxies on arena_combat, resolution dominates GPU cost while proxy count has a small GPU effect and a larger CPU effect.",
        "The resolution-dominance pattern repeats in corridor_static and dense_city, not only in arena_combat.",
        "Visual A/A captures are byte-identical within each scene/preset pair; A/B captures differ in 1.745-4.077% of pixels at 1280x720.",
        "All evidence is single-session on one RTX 5050; no cross-device or cross-session generalization is claimed.",
    ]
    open_questions = [
        "2560x1440 and ultrawide resolutions above 1920x1080 are not measured.",
        "Other GPUs, drivers and CPU platforms are not measured.",
        "Animation, temporal effects, camera motion and real game workloads are not covered.",
        "Preset application in the hub/engine and M09 parent admission remain out of scope.",
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "totals": {
            "bundles": len(entries),
            "performance_captures": performance_runs,
            "visual_images": visual_images,
            "evidence_files": sum(entry["evidence_files"] for entry in entries),
            "unique_source_shas": len({entry["source_sha"] for entry in entries}),
        },
        "runs": performance_runs,
        "images": visual_images,
        "entries": entries,
        "cross_experiment_findings": cross_findings,
        "open_questions": open_questions,
        "verdict": "MEASUREMENT_CAMPAIGN_INDEXED",
        "limitations": [
            "synthesis of already integrated evidence; no new capture",
            "single session and one GPU across all bundles",
            "measurements are costs and visual pixel differences, not game FPS or quality",
            "no cross-device or cross-session generalization",
            "M09 parent remains NOT_ADMITTED",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M09 · Measurement atlas — RTX 5050",
        "",
        "**Status:** `MEASUREMENT_CAMPAIGN_INDEXED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Totais:** {report['totals']['bundles']} bundles · {report['totals']['performance_captures']} capturas de performance · "
        f"{report['totals']['visual_images']} imagens · {report['totals']['evidence_files']} arquivos de evidência · "
        f"{report['totals']['unique_source_shas']} source SHAs",
        "",
        "## Bundles",
        "",
        "| Bundle | Tipo | Runs | Arquivos | Source SHA | Verdict |",
        "|---|---|---:|---:|---|---|",
    ]
    for entry in report["entries"]:
        lines.append(
            f"| {entry['id']} | {entry['kind']} | {entry['runs']} | {entry['evidence_files']} | "
            f"`{entry['source_sha'][:12]}` | {entry['verdict']} |"
        )
    lines.extend(["", "## Achados cross-experiment", ""])
    lines.extend(f"- {finding}" for finding in report["cross_experiment_findings"])
    lines.extend(["", "## Perguntas abertas", ""])
    lines.extend(f"- {question}" for question in report["open_questions"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Atlas gerado por `docs/benchmarks/m09/tools/build_measurement_atlas.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "M09_ATLAS")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

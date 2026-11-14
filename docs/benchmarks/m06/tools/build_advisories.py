#!/usr/bin/env python3
"""Build deterministic performance advisories from the M09 performance.v1 bundle.

The tool consumes already converted observations, computes render headroom and
GPU/CPU frame shares, and emits safe recommendations. It performs no new
measurement and makes no FPS, quality or universal gain claim.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SOURCE = REPO_ROOT / "docs/benchmarks/m06/observations/m09-observations.v1.json"
SOURCE_FULL = REPO_ROOT / "docs/benchmarks/m06/observations/m09-observations-full.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m06"
OUTPUT_JSON = OUTPUT_DIR / "advisories.v1.json"
OUTPUT_MD = OUTPUT_DIR / "ADVISORIES.md"
OUTPUT_JSON_FULL = OUTPUT_DIR / "advisories-full.v1.json"
OUTPUT_MD_FULL = OUTPUT_DIR / "ADVISORIES-FULL.md"
EXPECTED_OBSERVATIONS = 12
EXPECTED_OBSERVATIONS_FULL = 156
DEFAULT_TITLE = "NEX M06 · Performance advisories — RTX 5050"
FULL_TITLE = "NEX M06 · Performance advisories (full dataset) — RTX 5050"

SCHEMA_VERSION = "m06_performance_advisories.v1"
RECOMMENDATIONS = {
    "pacing": {
        "action": "re-measure with a higher cap or a heavier workload before optimizing",
        "reason": "the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap",
        "risk": "LOW",
    },
    "gpu": {
        "action": "reduce resolution scale, MSAA, shadow quality or glow, then re-measure",
        "reason": "GPU render p95 is the dominant render pressure",
        "risk": "LOW",
    },
    "cpu": {
        "action": "reduce draw calls or object count, or move work off the main thread, then re-measure",
        "reason": "CPU render p95 is the dominant render pressure",
        "risk": "LOW",
    },
    "memory": {
        "action": "inspect VRAM and allocation pressure before optimizing",
        "reason": "memory pressure is the declared bottleneck",
        "risk": "LOW",
    },
    "unknown": {
        "action": "collect draw calls and VRAM before optimizing",
        "reason": "no single render pressure dominates in the measured fields",
        "risk": "LOW",
    },
    "insufficient_data": {
        "action": "collect GPU, CPU and pacing measurements before optimizing",
        "reason": "the observation does not provide enough measured fields",
        "risk": "LOW",
    },
}
LIMITATIONS = [
    "advisories are derived from one session on one RTX 5050; no cross-device or cross-session generalization",
    "renderer allocation bytes are session history, not device VRAM",
    "GPU render timing can describe earlier work and is not frame-aligned",
    "headroom is relative to this capped run and does not prove capacity at another cap or workload",
    "no FPS gain, quality or universal recommendation is claimed",
]


def _load(path: Path) -> Any:
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)

    def constant(token):
        raise ValueError("non-finite JSON: " + token)

    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def _measured(observation: dict[str, Any], group: str, key: str) -> float:
    entry = observation.get(group, {}).get(key)
    if not isinstance(entry, dict) or entry.get("status") != "MEASURED":
        raise ValueError(f"{observation.get('observation_id')}: {group}.{key} is not MEASURED")
    value = entry.get("value")
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{observation.get('observation_id')}: {group}.{key} value is invalid")
    return float(value)


def _advisory(observation: dict[str, Any]) -> dict[str, Any]:
    if observation.get("schema_version") != "performance.v1":
        raise ValueError("observation schema is invalid")
    observation_id = observation.get("observation_id")
    workload = observation.get("workload", {})
    max_fps = int(workload.get("max_fps", 0))
    if max_fps <= 0:
        raise ValueError(f"{observation_id}: max_fps must be positive")
    gpu_ms = _measured(observation, "timings", "gpu_render_ms")
    cpu_ms = _measured(observation, "timings", "cpu_render_ms")
    pacing_ms = _measured(observation, "timings", "frame_pacing_ms")
    if pacing_ms <= 0:
        raise ValueError(f"{observation_id}: frame_pacing_ms must be positive")
    render_ms = max(gpu_ms, cpu_ms)
    headroom_ms = max(0.0, pacing_ms - render_ms)
    target_frame_ms = 1000.0 / max_fps
    classification = observation.get("bottleneck", {}).get("classification")
    if classification not in RECOMMENDATIONS:
        raise ValueError(f"{observation_id}: unsupported bottleneck classification")
    recommendation = dict(RECOMMENDATIONS[classification])
    recommendation["requires_measurement"] = True
    return {
        "observation_id": observation_id,
        "scene_id": workload.get("scene_id"),
        "proxy_count": int(workload.get("proxy_count", 0)),
        "resolution_px": [
            int(workload.get("resolution", {}).get("width_px", 0)),
            int(workload.get("resolution", {}).get("height_px", 0)),
        ],
        "bottleneck": classification,
        "measured": {
            "gpu_render_ms": round(gpu_ms, 3),
            "cpu_render_ms": round(cpu_ms, 3),
            "frame_pacing_ms": round(pacing_ms, 3),
            "render_ms": round(render_ms, 3),
        },
        "frame_budget": {
            "max_fps": max_fps,
            "target_frame_ms": round(target_frame_ms, 3),
            "render_headroom_ms": round(headroom_ms, 3),
            "render_headroom_vs_target_ms": round(max(0.0, target_frame_ms - render_ms), 3),
            "gpu_share_of_frame_pct": round(gpu_ms / pacing_ms * 100.0, 2),
            "cpu_share_of_frame_pct": round(cpu_ms / pacing_ms * 100.0, 2),
        },
        "recommendation": recommendation,
    }


def build_report(source_path: Path = SOURCE, expected_count: int = EXPECTED_OBSERVATIONS) -> dict[str, Any]:
    source = _load(source_path)
    observations = source.get("observations")
    if not isinstance(observations, list) or len(observations) != expected_count:
        raise ValueError(f"source observation bundle must contain {expected_count} observations")
    advisories = [_advisory(observation) for observation in observations]
    if len({advisory["observation_id"] for advisory in advisories}) != expected_count:
        raise ValueError("advisory ids must be unique")
    counts: dict[str, int] = {}
    for advisory in advisories:
        counts[advisory["bottleneck"]] = counts.get(advisory["bottleneck"], 0) + 1
    headrooms = [advisory["frame_budget"]["render_headroom_ms"] for advisory in advisories]
    gpu_shares = [advisory["frame_budget"]["gpu_share_of_frame_pct"] for advisory in advisories]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_bundle": source_path.relative_to(REPO_ROOT).as_posix(),
        "observation_count": len(advisories),
        "advisories": advisories,
        "summary": {
            "bottleneck_counts": counts,
            "min_render_headroom_ms": min(headrooms),
            "max_render_headroom_ms": max(headrooms),
            "max_gpu_share_of_frame_pct": max(gpu_shares),
            "target_frame_ms_240_fps": round(1000.0 / 240.0, 3),
        },
        "verdict": "ADVISORIES_DERIVED_FROM_MEASURED_OBSERVATIONS",
        "limitations": LIMITATIONS,
    }


def render_markdown(report: dict[str, Any], title: str = DEFAULT_TITLE) -> str:
    lines = [
        f"# {title}",
        "",
        "**Status:** `ADVISORIES_DERIVED_FROM_MEASURED_OBSERVATIONS / SINGLE_SESSION / NO_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['source_bundle']}` · **Observações:** {report['observation_count']}",
        "",
        "## Resumo",
        "",
        f"- Bottlenecks: {report['summary']['bottleneck_counts']}.",
        f"- Headroom de render: {report['summary']['min_render_headroom_ms']:.3f}–{report['summary']['max_render_headroom_ms']:.3f} ms.",
        f"- Maior participação GPU no frame: {report['summary']['max_gpu_share_of_frame_pct']:.2f}%.",
        f"- Frame alvo a 240 fps: {report['summary']['target_frame_ms_240_fps']:.3f} ms.",
        "",
        "## Advisórios",
        "",
        "| Observação | Cena | Proxies | Resolução | GPU ms | CPU ms | Pacing ms | Headroom ms | GPU % | CPU % | Bottleneck |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for advisory in report["advisories"]:
        measured = advisory["measured"]
        budget = advisory["frame_budget"]
        lines.append(
            f"| {advisory['observation_id']} | {advisory['scene_id']} | {advisory['proxy_count']} | "
            f"{advisory['resolution_px'][0]}×{advisory['resolution_px'][1]} | {measured['gpu_render_ms']:.3f} | "
            f"{measured['cpu_render_ms']:.3f} | {measured['frame_pacing_ms']:.3f} | "
            f"{budget['render_headroom_ms']:.3f} | {budget['gpu_share_of_frame_pct']:.2f} | "
            f"{budget['cpu_share_of_frame_pct']:.2f} | {advisory['bottleneck']} |"
        )
    lines.extend(["", "## Recomendações", ""])
    for advisory in report["advisories"]:
        recommendation = advisory["recommendation"]
        lines.append(
            f"- `{advisory['observation_id']}`: {recommendation['action']} "
            f"({recommendation['reason']}; risco {recommendation['risk']}; requer nova medição)."
        )
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m06/tools/build_advisories.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _render_and_write(
    source_path: Path,
    expected_count: int,
    output_json: Path,
    output_md: Path,
    title: str,
    check_only: bool,
) -> int:
    report = build_report(source_path, expected_count)
    rendered_json = render_json(report)
    rendered_md = render_markdown(report, title)
    if check_only:
        if not output_json.is_file() or not output_md.is_file():
            print("M06_ADVISORIES_CHECK_FAIL: outputs missing")
            return 1
        if output_json.read_text(encoding="utf-8") != rendered_json:
            print("M06_ADVISORIES_CHECK_FAIL: JSON is stale")
            return 1
        if output_md.read_text(encoding="utf-8") != rendered_md:
            print("M06_ADVISORIES_CHECK_FAIL: Markdown is stale")
            return 1
        print(f"M06_ADVISORIES_CHECK_PASS: {len(report['advisories'])} advisories")
        return 0
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_json)
    with open(output_md, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_md)
    print(f"M06_ADVISORIES_WRITE_PASS: {len(report['advisories'])} advisories")
    return 0


def main(argv: list[str]) -> int:
    modes = {
        "--check": (SOURCE, EXPECTED_OBSERVATIONS, OUTPUT_JSON, OUTPUT_MD, DEFAULT_TITLE, True),
        "--full": (SOURCE_FULL, EXPECTED_OBSERVATIONS_FULL, OUTPUT_JSON_FULL, OUTPUT_MD_FULL, FULL_TITLE, False),
        "--check-full": (SOURCE_FULL, EXPECTED_OBSERVATIONS_FULL, OUTPUT_JSON_FULL, OUTPUT_MD_FULL, FULL_TITLE, True),
    }
    if len(argv) == 1 and argv[0] in modes:
        return _render_and_write(*modes[argv[0]])
    if argv:
        print("usage: build_advisories.py [--check|--full|--check-full]")
        return 2
    return _render_and_write(SOURCE, EXPECTED_OBSERVATIONS, OUTPUT_JSON, OUTPUT_MD, DEFAULT_TITLE, False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

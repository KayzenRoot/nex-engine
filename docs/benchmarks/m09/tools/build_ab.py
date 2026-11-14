#!/usr/bin/env python3
"""NEX M09 preset A/B/A report builder.

Reads the three validated captures, verifies the run manifest, recomputes
aggregates and writes a deterministic JSON report plus Markdown. No new
measurement is performed and no general performance claim is made.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab")
EVIDENCE = REPO_ROOT / EVIDENCE_REL
MANIFEST = EVIDENCE / "runs.v1.json"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m09"
REPORT_JSON = OUTPUT_DIR / "ab.v1.json"
REPORT_MD = OUTPUT_DIR / "AB-REPORT.md"

REPORT_SCHEMA = "m09_preset_ab.v1"
RUNS_SCHEMA = "preset_ab_runs.v1"
PRESETS = ("ab-low", "ab-high")
METRICS = ("GPU_RENDER_MS", "CPU_RENDER_MS", "FRAME_PACING_INTERVAL_MS", "MAIN_LOOP_INTERVAL_MS", "RENDERER_ALLOCATION_BYTES")


def load_json(path: Path) -> Any:
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)

    def constant(token):
        raise ValueError(f"non-finite JSON: {token}")

    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=pairs,
        parse_constant=constant,
    )


def load_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    if manifest.get("schema_version") != RUNS_SCHEMA:
        raise ValueError("runs manifest schema is invalid")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 3:
        raise ValueError("runs manifest must contain 3 runs")
    if [run.get("sequence") for run in runs] != [1, 2, 3]:
        raise ValueError("runs manifest sequence must be 1,2,3")
    if len({run.get("run_id") for run in runs}) != 3:
        raise ValueError("runs manifest run ids must be unique")
    for run in runs:
        if run.get("preset_id") not in PRESETS:
            raise ValueError("runs manifest preset is invalid")
    return manifest


def load_capture(run_id: str) -> dict[str, Any]:
    path = EVIDENCE / f"gpu_profile_{run_id}.json"
    if not path.is_file():
        raise ValueError(f"capture not found: {run_id}")
    document = load_json(path)
    if document.get("run_status") != "COMPLETE":
        raise ValueError(f"{run_id}: run_status is not COMPLETE")
    workload = document.get("workload", {})
    if workload.get("scene") != "Preset A/B/A" or workload.get("proxy_count") != 200 or workload.get("effect_mode") != "lights":
        raise ValueError(f"{run_id}: workload provenance is invalid")
    settings = document.get("settings", {})
    if settings.get("max_fps") != 240 or settings.get("vsync_mode") != 0:
        raise ValueError(f"{run_id}: settings provenance is invalid")
    series = document.get("series", {})
    metrics: dict[str, Any] = {}
    for key in METRICS:
        entry = series.get(key, {})
        if entry.get("status") != "MEASURED":
            raise ValueError(f"{run_id}: {key} is not MEASURED")
        aggregates = entry.get("aggregates", {})
        metrics[key] = {
            "mean": float(aggregates["mean"]),
            "p50": float(aggregates["p50"]),
            "p95": float(aggregates["p95"]),
            "p99": float(aggregates["p99"]),
        }
    return {
        "run_id": run_id,
        "source_sha": document.get("source_sha"),
        "captured_at_utc": document.get("captured_at_utc"),
        "metrics": metrics,
        "one_percent_low_fps": float(document["measurement"]["one_percent_low_fps"]),
        "observed_seconds": float(document["measurement"]["observed_seconds"]),
        "viewport": document.get("viewport", {}).get("resolution_px"),
    }


def load_validation(run_id: str) -> dict[str, Any]:
    path = EVIDENCE / f"gpu_profile_{run_id}.json.validation.json"
    if not path.is_file():
        raise ValueError(f"validation not found: {run_id}")
    document = load_json(path)
    if document.get("status") != "PASS":
        raise ValueError(f"{run_id}: validation is not PASS")
    return document


METRIC_KEYS = {"GPU_RENDER_MS": "gpu_ms", "CPU_RENDER_MS": "cpu_ms", "FRAME_PACING_INTERVAL_MS": "pacing_ms"}


def _metric(run: dict[str, Any], key: str, percentile: str = "p95") -> float:
    return float(run[METRIC_KEYS[key]][percentile])


def _pct(value: float, baseline: float) -> float:
    return round((value - baseline) / baseline * 100.0, 1)


def build_report() -> dict[str, Any]:
    manifest = load_manifest()
    source_sha = manifest.get("source_sha")
    runs: list[dict[str, Any]] = []
    for entry in manifest["runs"]:
        run_id = entry["run_id"]
        capture = load_capture(run_id)
        validation = load_validation(run_id)
        if capture["source_sha"] != source_sha or validation.get("source_sha") != source_sha:
            raise ValueError(f"{run_id}: source_sha mismatch")
        if capture["viewport"] != [1280, 720]:
            raise ValueError(f"{run_id}: unexpected viewport")
        runs.append(
            {
                "sequence": entry["sequence"],
                "run_id": run_id,
                "preset_id": entry["preset_id"],
                "captured_at_utc": capture["captured_at_utc"],
                "observed_seconds": round(capture["observed_seconds"], 3),
                "gpu_ms": {key: round(capture["metrics"]["GPU_RENDER_MS"][key], 3) for key in ("p50", "p95", "p99")},
                "cpu_ms": {key: round(capture["metrics"]["CPU_RENDER_MS"][key], 3) for key in ("p50", "p95", "p99")},
                "pacing_ms": {key: round(capture["metrics"]["FRAME_PACING_INTERVAL_MS"][key], 3) for key in ("p50", "p95", "p99")},
                "one_percent_low_fps": round(capture["one_percent_low_fps"], 2),
                "renderer_allocation_bytes": int(capture["metrics"]["RENDERER_ALLOCATION_BYTES"]["p50"]),
            }
        )
    low_runs = [run for run in runs if run["preset_id"] == "ab-low"]
    high_runs = [run for run in runs if run["preset_id"] == "ab-high"]
    if len(low_runs) != 2 or len(high_runs) != 1:
        raise ValueError("expected two ab-low runs and one ab-high run")
    low_gpu_p95 = statistics.median(_metric(run, "GPU_RENDER_MS") for run in low_runs)
    low_cpu_p95 = statistics.median(_metric(run, "CPU_RENDER_MS") for run in low_runs)
    low_pacing_p95 = statistics.median(_metric(run, "FRAME_PACING_INTERVAL_MS") for run in low_runs)
    low_gpu_p50 = statistics.median(_metric(run, "GPU_RENDER_MS", "p50") for run in low_runs)
    low_one_percent = statistics.median(run["one_percent_low_fps"] for run in low_runs)
    high = high_runs[0]
    deltas = {
        "gpu_p95_pct": _pct(_metric(high, "GPU_RENDER_MS"), low_gpu_p95),
        "gpu_p50_pct": _pct(_metric(high, "GPU_RENDER_MS", "p50"), low_gpu_p50),
        "cpu_p95_pct": _pct(_metric(high, "CPU_RENDER_MS"), low_cpu_p95),
        "pacing_p95_pct": _pct(_metric(high, "FRAME_PACING_INTERVAL_MS"), low_pacing_p95),
        "one_percent_low_pct": _pct(high["one_percent_low_fps"], low_one_percent),
    }
    first_low, second_low = low_runs
    aa = {
        "gpu_p95_pct": _pct(_metric(second_low, "GPU_RENDER_MS"), _metric(first_low, "GPU_RENDER_MS")),
        "cpu_p95_pct": _pct(_metric(second_low, "CPU_RENDER_MS"), _metric(first_low, "CPU_RENDER_MS")),
        "pacing_p95_pct": _pct(_metric(second_low, "FRAME_PACING_INTERVAL_MS"), _metric(first_low, "FRAME_PACING_INTERVAL_MS")),
        "one_percent_low_pct": _pct(second_low["one_percent_low_fps"], first_low["one_percent_low_fps"]),
    }
    observations = [
        f"ab-high GPU p95: {_metric(high, 'GPU_RENDER_MS'):.3f} ms vs ab-low median {low_gpu_p95:.3f} ms ({deltas['gpu_p95_pct']:+.1f}%).",
        f"ab-high CPU p95: {_metric(high, 'CPU_RENDER_MS'):.3f} ms vs ab-low median {low_cpu_p95:.3f} ms ({deltas['cpu_p95_pct']:+.1f}%).",
        f"Pacing p95: {_metric(high, 'FRAME_PACING_INTERVAL_MS'):.3f} ms vs {low_pacing_p95:.3f} ms ({deltas['pacing_p95_pct']:+.1f}%); both runs are capped at 240 fps.",
        f"A/A stability: GPU p95 {aa['gpu_p95_pct']:+.1f}%, CPU p95 {aa['cpu_p95_pct']:+.1f}%, 1% low {aa['one_percent_low_pct']:+.1f}% between the two ab-low runs.",
        "The measured difference is a GPU cost of the high preset on this synthetic workload, not a game FPS or quality claim.",
    ]
    report = {
        "schema_version": REPORT_SCHEMA,
        "source_sha": source_sha,
        "evidence_bundle": str(EVIDENCE_REL).replace("\\", "/"),
        "session_date": "2026-11-14",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "Vulkan 1.4.351"},
        "godot_version": "4.7.2-stable",
        "viewport_px": [1280, 720],
        "settings": {"vsync_mode": 0, "max_fps": 240},
        "runs": runs,
        "baselines": {
            "ab-low": {
                "runs": len(low_runs),
                "gpu_p50_ms": round(low_gpu_p50, 3),
                "gpu_p95_ms": round(low_gpu_p95, 3),
                "cpu_p95_ms": round(low_cpu_p95, 3),
                "pacing_p95_ms": round(low_pacing_p95, 3),
                "one_percent_low_fps": round(low_one_percent, 2),
            }
        },
        "deltas_high_vs_low": deltas,
        "aa_stability": aa,
        "verdict": "MEASURED_COST_OBSERVED",
        "observations": observations,
        "limitations": [
            "single session; one ab-high run and two ab-low runs",
            "synthetic 200-proxy workload at 1280x720; no cross-scene generalization",
            "max_fps 240 and vsync disabled; frame pacing is capped",
            "renderer allocation bytes are session history, not device VRAM",
            "GPU render timing can describe earlier work and is not frame-aligned",
            "the harness applies a subset of preset_pack.v1 settings",
            "no FPS gain, quality or universal recommendation is claimed",
        ],
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# NEX M09 · Preset A/B/A — RTX 5050",
        "",
        "**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['evidence_bundle']}` · **Source SHA:** `{report['source_sha']}`",
        f"**Hardware:** {report['hardware']['gpu']} · {report['hardware']['driver']} · {report['godot_version']}",
        f"**Viewport:** {report['viewport_px'][0]}×{report['viewport_px'][1]} · vsync {report['settings']['vsync_mode']} · max_fps {report['settings']['max_fps']}",
        "",
        "## Runs",
        "",
        "| Seq | Preset | Run | GPU p50 | GPU p95 | CPU p95 | Pacing p95 | 1% low | Alloc MiB |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for run in report["runs"]:
        lines.append(
            f"| {run['sequence']} | {run['preset_id']} | {run['run_id']} | "
            f"{run['gpu_ms']['p50']:.3f} | {run['gpu_ms']['p95']:.3f} | "
            f"{run['cpu_ms']['p95']:.3f} | {run['pacing_ms']['p95']:.3f} | "
            f"{run['one_percent_low_fps']:.2f} | {run['renderer_allocation_bytes'] / 1048576.0:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Deltas (ab-high vs ab-low median)",
            "",
            f"- GPU p95: **{report['deltas_high_vs_low']['gpu_p95_pct']:+.1f}%**",
            f"- GPU p50: {report['deltas_high_vs_low']['gpu_p50_pct']:+.1f}%",
            f"- CPU p95: {report['deltas_high_vs_low']['cpu_p95_pct']:+.1f}%",
            f"- Pacing p95: {report['deltas_high_vs_low']['pacing_p95_pct']:+.1f}%",
            f"- 1% low: {report['deltas_high_vs_low']['one_percent_low_pct']:+.1f}%",
            "",
            "## A/A stability (ab-low run 2 vs run 1)",
            "",
            f"- GPU p95: {report['aa_stability']['gpu_p95_pct']:+.1f}%",
            f"- CPU p95: {report['aa_stability']['cpu_p95_pct']:+.1f}%",
            f"- Pacing p95: {report['aa_stability']['pacing_p95_pct']:+.1f}%",
            f"- 1% low: {report['aa_stability']['one_percent_low_pct']:+.1f}%",
            "",
            "## Observações",
            "",
        ]
    )
    lines.extend(f"- {observation}" for observation in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Relatório gerado por `docs/benchmarks/m09/tools/build_ab.py`; não é benchmark nem claim de ganho.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _safe_output(path: Path) -> Path:
    base = OUTPUT_DIR.resolve()
    candidate = path.resolve()
    if candidate.parent != base:
        raise ValueError("output path escapes docs/benchmarks/m09")
    return candidate


def write_outputs(report: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(_safe_output(REPORT_JSON), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_json(report))
    with open(_safe_output(REPORT_MD), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_markdown(report))


def main(argv: list[str]) -> int:
    report = build_report()
    rendered_json = render_json(report)
    rendered_md = render_markdown(report)
    if argv == ["--check"]:
        if not REPORT_JSON.is_file() or not REPORT_MD.is_file():
            print("AB_CHECK_FAIL: outputs missing")
            return 1
        if REPORT_JSON.read_text(encoding="utf-8") != rendered_json:
            print("AB_CHECK_FAIL: ab.v1.json is stale")
            return 1
        if REPORT_MD.read_text(encoding="utf-8") != rendered_md:
            print("AB_CHECK_FAIL: AB-REPORT.md is stale")
            return 1
        print(f"AB_CHECK_PASS: {len(report['runs'])} runs")
        return 0
    if argv:
        print("usage: build_ab.py [--check]")
        return 2
    write_outputs(report)
    print(f"AB_WRITE_PASS: {len(report['runs'])} runs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

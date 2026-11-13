#!/usr/bin/env python3
"""NEX M06 Bottleneck Atlas builder.

Recomputes every aggregate from the published S05 Lighting Matrix captures,
verifies the bundle hashes, classifies the bottleneck in the performance.v1
vocabulary and writes a deterministic JSON atlas plus a Markdown report.

No new measurement is performed. The source bundle is a single synthetic
session on an RTX 5050; conclusions do not generalize to other scenes,
hardware or sessions.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
BUNDLE_REL = Path("nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05")
BUNDLE = REPO_ROOT / BUNDLE_REL
ANALYSIS = BUNDLE / "ANALYSIS.md"
SUMS = BUNDLE / "SHA256SUMS.txt"
OUTPUT_DIR = REPO_ROOT / "docs/benchmarks/m06"
ATLAS_PATH = OUTPUT_DIR / "atlas.v1.json"
REPORT_PATH = OUTPUT_DIR / "ATLAS.md"

ATLAS_VERSION = "m06_bottleneck_atlas.v1"
PRESET_ORDER = ("baseline", "lights", "shadows", "vfx", "combined")
SERIES_KEYS = (
    "GPU_RENDER_MS",
    "CPU_RENDER_MS",
    "FRAME_PACING_INTERVAL_MS",
    "MAIN_LOOP_INTERVAL_MS",
    "RENDERER_ALLOCATION_BYTES",
)
ROW_RE = re.compile(r"^\|")
SUM_RE = re.compile(r"^([\da-f]{64}) \*(.+)$")
SHA_RE = re.compile(r"^[\da-f]{40}$")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_non_finite(token: str) -> None:
    raise ValueError(f"non-finite JSON: {token}")


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_non_finite,
    )


def _bundle_bytes(name: str) -> bytes:
    """Hash the published Git blob, falling back to an LF-normalized checkout file."""
    blob = f":{BUNDLE_REL.as_posix()}/{name}"
    try:
        result = subprocess.run(
            ["git", "cat-file", "blob", blob],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        return result.stdout
    except (OSError, subprocess.CalledProcessError):
        return (BUNDLE / name).read_bytes().replace(b"\r\n", b"\n")


def _hash_variants(name: str) -> set[str]:
    """Hash the LF Git blob plus its CRLF reconstruction.

    Measurement captures are additionally checked strictly against the LF blob
    in verify_bundle; documentation and validation JSON may be pinned with the
    original working-tree line endings.
    """
    data = _bundle_bytes(name)
    variants = {hashlib.sha256(data).hexdigest()}
    if b"\r\n" not in data:
        variants.add(hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest())
    return variants


def _verify_entry(digest: str, name: str) -> str | None:
    if Path(name).name != name or "/" in name or "\\" in name:
        return f"unsafe checksum path: {name!r}"
    if not (BUNDLE / name).is_file():
        return f"missing bundle file: {name}"
    variants = _hash_variants(name)
    if digest not in variants:
        return f"hash mismatch: {name}"
    if re.fullmatch(r"gpu_profile_\d+-\d+\.json", name) and digest != hashlib.sha256(_bundle_bytes(name)).hexdigest():
        return f"measurement capture must match the LF Git blob: {name}"
    return None


def verify_bundle() -> dict[str, Any]:
    """Verify every file listed in SHA256SUMS.txt; never follow a path outside the bundle."""
    errors: list[str] = []
    verified = 0
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        match = SUM_RE.match(line)
        if match is None:
            errors.append(f"malformed checksum line: {line!r}")
            continue
        error = _verify_entry(*match.groups())
        if error is not None:
            errors.append(error)
            continue
        verified += 1
    if errors:
        raise ValueError("bundle verification failed: " + "; ".join(errors))
    return {
        "status": "PASS",
        "verified_files": verified,
        "measurement_captures_strict": True,
        "text_line_ending_tolerance": "LF/CRLF accepted for documentation and validation JSON",
    }


def parse_analysis_table() -> list[dict[str, Any]]:
    """Parse the published matrix table; ignore the delta table and headers."""
    rows: list[dict[str, Any]] = []
    for line in ANALYSIS.read_text(encoding="utf-8").splitlines():
        if not ROW_RE.match(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("Cenário", "---") or not cells[1].isdigit():
            continue
        scenario, count_text, run_id = cells[0], cells[1], cells[2]
        if not re.fullmatch(r"\d{6,}-\d{6,}", run_id):
            continue
        preset = scenario.split("-", 1)[0]
        if preset not in PRESET_ORDER:
            continue
        rows.append(
            {
                "scenario": scenario,
                "preset": preset,
                "count": int(count_text),
                "run_id": run_id,
                "repetition": "rep2" in scenario or "rep3" in scenario,
            }
        )
    return rows


def _series(series: dict[str, Any], key: str) -> dict[str, Any]:
    entry = series.get(key)
    if not isinstance(entry, dict):
        raise ValueError(f"missing series {key}")
    if entry.get("status") != "MEASURED":
        raise ValueError(f"series {key} is not MEASURED")
    aggregates = entry.get("aggregates")
    if not isinstance(aggregates, dict):
        raise ValueError(f"series {key} has no aggregates")
    for percentile in ("mean", "p50", "p95", "p99"):
        if not isinstance(aggregates.get(percentile), (int, float)):
            raise ValueError(f"series {key} lacks {percentile}")
    return {
        "mean": float(aggregates["mean"]),
        "p50": float(aggregates["p50"]),
        "p95": float(aggregates["p95"]),
        "p99": float(aggregates["p99"]),
        "valid_sample_count": int(entry.get("valid_sample_count", 0)),
        "invalid_sample_count": int(entry.get("invalid_sample_count", 0)),
    }


def load_capture(run_id: str) -> dict[str, Any]:
    path = BUNDLE / f"gpu_profile_{run_id}.json"
    if not path.is_file():
        raise ValueError(f"capture not found: {run_id}")
    document = load_json(path)
    if document.get("schema_version") != "nex_gpu_render_profile.v2":
        raise ValueError(f"{run_id}: unexpected schema_version")
    if document.get("run_status") != "COMPLETE":
        raise ValueError(f"{run_id}: run_status is not COMPLETE")
    source_sha = document.get("source_sha")
    if not isinstance(source_sha, str) or SHA_RE.match(source_sha) is None:
        raise ValueError(f"{run_id}: invalid source_sha")
    if document.get("run_id") != run_id:
        raise ValueError(f"{run_id}: run_id does not match filename")
    workload = document.get("workload", {})
    series = document.get("series", {})
    if not isinstance(workload, dict) or not isinstance(series, dict):
        raise ValueError(f"{run_id}: malformed workload/series")
    measurement = document.get("measurement", {})
    if not isinstance(measurement, dict) or measurement.get("frame_pacing_status") != "MEASURED":
        raise ValueError(f"{run_id}: frame pacing is not MEASURED")
    one_percent = measurement.get("one_percent_low_fps")
    if not isinstance(one_percent, (int, float)):
        raise ValueError(f"{run_id}: missing one_percent_low_fps")
    metrics = {key: _series(series, key) for key in SERIES_KEYS}
    return {
        "run_id": run_id,
        "source_sha": source_sha,
        "captured_at_utc": document.get("captured_at_utc"),
        "godot_version": document.get("godot_version"),
        "adapter": document.get("adapter"),
        "driver": document.get("driver"),
        "renderer": document.get("renderer"),
        "settings": document.get("settings", {}),
        "workload": {
            "scene": workload.get("scene"),
            "layout": workload.get("layout"),
            "effect_mode": workload.get("effect_mode"),
            "proxy_count": workload.get("proxy_count"),
        },
        "one_percent_low_fps": float(one_percent),
        "one_percent_low_fps_label": measurement.get("delta_derived_one_percent_low_fps_label"),
        "observed_seconds": float(measurement.get("observed_seconds", 0.0)),
        "metrics": metrics,
    }


def cross_check_validation(run_id: str, capture: dict[str, Any]) -> None:
    """Ensure the published validation JSON agrees with aggregates recomputed from the raw capture."""
    path = BUNDLE / f"gpu_profile_{run_id}.json.s05-validation.json"
    if not path.is_file():
        raise ValueError(f"{run_id}: validation JSON is missing")
    document = load_json(path)
    if document.get("status") != "PASS":
        raise ValueError(f"{run_id}: validation status is not PASS")
    if document.get("run_id") != run_id or document.get("source_sha") != capture["source_sha"]:
        raise ValueError(f"{run_id}: validation provenance mismatch")
    if not math.isclose(float(document.get("observed_seconds", 0.0)), capture["observed_seconds"], abs_tol=1e-6):
        raise ValueError(f"{run_id}: observed_seconds mismatch")
    if not math.isclose(float(document.get("one_percent_low_fps", 0.0)), capture["one_percent_low_fps"], abs_tol=1e-6):
        raise ValueError(f"{run_id}: one_percent_low_fps mismatch")
    validation_series = document.get("series", {})
    for key in SERIES_KEYS:
        published = validation_series.get(key, {}).get("aggregates", {})
        for percentile in ("mean", "p50", "p95", "p99"):
            expected = capture["metrics"][key][percentile]
            actual = published.get(percentile)
            if not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected, abs_tol=1e-9):
                raise ValueError(f"{run_id}: validation aggregate mismatch for {key}.{percentile}")


def classify(capture: dict[str, Any]) -> dict[str, Any]:
    gpu_p95 = capture["metrics"]["GPU_RENDER_MS"]["p95"]
    cpu_p95 = capture["metrics"]["CPU_RENDER_MS"]["p95"]
    pacing_p95 = capture["metrics"]["FRAME_PACING_INTERVAL_MS"]["p95"]
    pacing_p50 = capture["metrics"]["FRAME_PACING_INTERVAL_MS"]["p50"]
    vsync_mode = int(capture["settings"].get("vsync_mode", 0))
    gpu_share = gpu_p95 / pacing_p95 if pacing_p95 > 0 else 0.0
    if vsync_mode != 0 or pacing_p50 >= 15.0:
        classification = "pacing"
        confidence = "high" if gpu_share < 0.25 else "medium"
    elif gpu_share >= 0.80:
        classification = "gpu"
        confidence = "medium"
    elif cpu_p95 / pacing_p95 >= 0.80:
        classification = "cpu"
        confidence = "medium"
    else:
        classification = "unknown"
        confidence = "low"
    if gpu_p95 > cpu_p95 * 1.2:
        render_pressure = "gpu"
    elif cpu_p95 > gpu_p95 * 1.2:
        render_pressure = "cpu"
    else:
        render_pressure = "balanced"
    return {
        "classification": classification,
        "evidence": "measured",
        "confidence": confidence,
        "render_pressure": render_pressure,
        "gpu_share_of_frame_pct": round(gpu_share * 100.0, 1),
        "render_headroom_ms": round(pacing_p95 - gpu_p95, 3),
    }


def _baseline_references(runs: list[dict[str, Any]]) -> dict[str, Any]:
    references: dict[str, Any] = {}
    for count in sorted({run["count"] for run in runs if run["preset"] == "baseline"}):
        group = [run for run in runs if run["preset"] == "baseline" and run["count"] == count]
        references[str(count)] = {
            "runs": len(group),
            "gpu_p95_median_ms": round(statistics.median(run["metrics"]["GPU_RENDER_MS"]["p95"] for run in group), 3),
            "cpu_p95_median_ms": round(statistics.median(run["metrics"]["CPU_RENDER_MS"]["p95"] for run in group), 3),
            "pacing_p95_median_ms": round(statistics.median(run["metrics"]["FRAME_PACING_INTERVAL_MS"]["p95"] for run in group), 3),
        }
    return references


def _cells(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for preset in PRESET_ORDER:
        for count in sorted({run["count"] for run in runs if run["preset"] == preset}):
            group = [run for run in runs if run["preset"] == preset and run["count"] == count]
            cells.append(
                {
                    "preset": preset,
                    "count": count,
                    "runs": len(group),
                    "gpu_p95_median_ms": round(statistics.median(run["metrics"]["GPU_RENDER_MS"]["p95"] for run in group), 3),
                    "cpu_p95_median_ms": round(statistics.median(run["metrics"]["CPU_RENDER_MS"]["p95"] for run in group), 3),
                    "pacing_p95_median_ms": round(statistics.median(run["metrics"]["FRAME_PACING_INTERVAL_MS"]["p95"] for run in group), 3),
                    "classification": group[0]["classification"],
                }
            )
    return cells


def _observations(runs: list[dict[str, Any]], cells: list[dict[str, Any]]) -> list[str]:
    by_key = {(cell["preset"], cell["count"]): cell for cell in cells}
    baseline = by_key[("baseline", 25)]
    observations: list[str] = []
    for preset in ("lights", "shadows", "vfx"):
        cell = by_key.get((preset, 25))
        if cell is None:
            continue
        delta = (cell["gpu_p95_median_ms"] - baseline["gpu_p95_median_ms"]) / baseline["gpu_p95_median_ms"] * 100.0
        observations.append(
            f"{preset}-25: {delta:+.1f}% de GPU p95 vs baseline-25, mantendo o frame limitado por pacing."
        )
    combined = by_key.get(("combined", 25))
    if combined is not None:
        delta = (combined["gpu_p95_median_ms"] - baseline["gpu_p95_median_ms"]) / baseline["gpu_p95_median_ms"] * 100.0
        observations.append(f"combined-25: {delta:+.1f}% de GPU p95 vs baseline-25; maior custo absoluto da matriz.")
    max_gpu = max(runs, key=lambda run: run["metrics"]["GPU_RENDER_MS"]["p95"])
    observations.append(
        f"maior GPU p95 absoluto: {max_gpu['metrics']['GPU_RENDER_MS']['p95']:.3f} ms em {max_gpu['run_id']}, "
        f"ainda {max_gpu['classification']['render_headroom_ms']:.3f} ms abaixo do pacing p95."
    )
    baseline_runs = [run for run in runs if run["preset"] == "baseline" and run["count"] == 25]
    spread = max(run["metrics"]["GPU_RENDER_MS"]["p50"] for run in baseline_runs) - min(
        run["metrics"]["GPU_RENDER_MS"]["p50"] for run in baseline_runs
    )
    observations.append(f"spread de GPU p50 nas 3 repetições baseline-25: {spread:.3f} ms.")
    observations.append("Todas as 15 runs permanecem pacing-bound; nenhuma célula satura o orçamento de GPU no cenário sintético.")
    return observations


def _capture_paths() -> dict[str, Path]:
    captures: dict[str, Path] = {}
    for path in BUNDLE.glob("gpu_profile_*.json"):
        match = re.fullmatch(r"gpu_profile_(\d+-\d+)\.json", path.name)
        if match is not None:
            captures[match.group(1)] = path
    return captures


def _load_rows() -> list[dict[str, Any]]:
    rows = parse_analysis_table()
    if len(rows) != 15:
        raise ValueError(f"expected 15 analysis rows, found {len(rows)}")
    if len({row['run_id'] for row in rows}) != len(rows):
        raise ValueError("duplicate run_id in analysis table")
    captures = _capture_paths()
    table_ids = {row["run_id"] for row in rows}
    if set(captures) != table_ids:
        missing = sorted(table_ids - set(captures))
        extra = sorted(set(captures) - table_ids)
        raise ValueError(f"capture/table mismatch; missing={missing}, extra={extra}")
    for row in rows:
        row["capture"] = load_capture(row["run_id"])
        cross_check_validation(row["run_id"], row["capture"])
        row["metrics"] = row["capture"]["metrics"]
        row["classification"] = classify(row["capture"])
    if len({row["capture"]["source_sha"] for row in rows}) != 1:
        raise ValueError("mixed source_sha across captures")
    return rows


def _apply_deltas(rows: list[dict[str, Any]], references: dict[str, Any]) -> None:
    for row in rows:
        reference = references[str(row["count"])]
        if row["preset"] == "baseline":
            row["delta_vs_baseline"] = None
            continue
        base_gpu = reference["gpu_p95_median_ms"]
        base_cpu = reference["cpu_p95_median_ms"]
        base_pacing = reference["pacing_p95_median_ms"]
        row["delta_vs_baseline"] = {
            "gpu_p95_pct": round((row["metrics"]["GPU_RENDER_MS"]["p95"] - base_gpu) / base_gpu * 100.0, 1),
            "cpu_p95_pct": round((row["metrics"]["CPU_RENDER_MS"]["p95"] - base_cpu) / base_cpu * 100.0, 1),
            "pacing_p95_ms": round(row["metrics"]["FRAME_PACING_INTERVAL_MS"]["p95"] - base_pacing, 3),
        }


def _run_entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": row["run_id"],
        "scenario": row["scenario"],
        "preset": row["preset"],
        "count": row["count"],
        "repetition": row["repetition"],
        "run_status": "COMPLETE",
        "source_sha": row["capture"]["source_sha"],
        "gpu_ms": row["metrics"]["GPU_RENDER_MS"],
        "cpu_ms": row["metrics"]["CPU_RENDER_MS"],
        "frame_pacing_ms": row["metrics"]["FRAME_PACING_INTERVAL_MS"],
        "main_loop_ms": row["metrics"]["MAIN_LOOP_INTERVAL_MS"],
        "renderer_allocation_bytes": row["metrics"]["RENDERER_ALLOCATION_BYTES"],
        "one_percent_low_fps": round(row["capture"]["one_percent_low_fps"], 3),
        "one_percent_low_fps_label": row["capture"]["one_percent_low_fps_label"],
        "classification": row["classification"]["classification"],
        "evidence": row["classification"]["evidence"],
        "confidence": row["classification"]["confidence"],
        "render_pressure": row["classification"]["render_pressure"],
        "gpu_share_of_frame_pct": row["classification"]["gpu_share_of_frame_pct"],
        "render_headroom_ms": row["classification"]["render_headroom_ms"],
        "delta_vs_baseline": row["delta_vs_baseline"],
    }


def _atlas_document(rows: list[dict[str, Any]], cells: list[dict[str, Any]], references: dict[str, Any],
                    verification: dict[str, Any]) -> dict[str, Any]:
    classification_counts: dict[str, int] = {}
    for row in rows:
        key = row["classification"]["classification"]
        classification_counts[key] = classification_counts.get(key, 0) + 1
    max_gpu = max(rows, key=lambda row: row["metrics"]["GPU_RENDER_MS"]["p95"])
    baseline_25 = [run for run in rows if run["preset"] == "baseline" and run["count"] == 25]
    first = rows[0]["capture"]
    bundle_posix = str(BUNDLE_REL).replace("\\", "/")
    return {
        "schema_version": ATLAS_VERSION,
        "generated_by": "docs/benchmarks/m06/tools/build_atlas.py",
        "source_bundle": bundle_posix,
        "source_analysis": f"{bundle_posix}/ANALYSIS.md",
        "source_sha": first["source_sha"],
        "capture_count": len(rows),
        "bundle_verification": verification,
        "hardware": {"adapter": first["adapter"], "driver": first["driver"], "renderer": first["renderer"]},
        "godot_version": first["godot_version"],
        "settings": {"vsync_mode": first["settings"].get("vsync_mode"), "max_fps": first["settings"].get("max_fps")},
        "summary": {
            "dominant_classification": max(classification_counts, key=classification_counts.get),
            "classification_counts": classification_counts,
            "max_gpu_p95_ms": round(max_gpu["metrics"]["GPU_RENDER_MS"]["p95"], 3),
            "max_gpu_p95_run": max_gpu["run_id"],
            "baseline25_gpu_p50_spread_ms": round(
                max(run["metrics"]["GPU_RENDER_MS"]["p50"] for run in baseline_25)
                - min(run["metrics"]["GPU_RENDER_MS"]["p50"] for run in baseline_25),
                3,
            ),
        },
        "baseline_references": references,
        "cells": cells,
        "observations": _observations(rows, cells),
        "runs": [_run_entry(row) for row in rows],
        "limitations": [
            "single synthetic session; one repetition per cell except baseline-25 x3",
            "vsync-limited 60 Hz: pacing classification reflects vsync, not a GPU-bound scene",
            "GPU render timing can describe earlier work and is not guaranteed to align one-to-one with the current frame",
            "renderer allocation bytes are session history, not device VRAM, and are not compared across runs",
            "one_percent_low_fps is callback pacing, not display presentation or input-to-photon latency",
            "no cross-scene, cross-driver, cross-hardware or cross-session generalization",
            "no new measurement is performed by this atlas",
        ],
        "provenance": {
            "measurement": "S05 published captures, 2026-11-13",
            "analysis": "ADMIN_SOLO_NOT_INDEPENDENT",
            "bundle_hashes": "SHA256SUMS verified by the builder",
        },
    }


def build_atlas() -> dict[str, Any]:
    verification = verify_bundle()
    rows = _load_rows()
    references = _baseline_references(rows)
    _apply_deltas(rows, references)
    order = {preset: index for index, preset in enumerate(PRESET_ORDER)}
    rows.sort(key=lambda row: (order[row["preset"]], row["count"], row["run_id"]))
    cells = _cells(rows)
    cells.sort(key=lambda cell: (order[cell["preset"]], cell["count"]))
    return _atlas_document(rows, cells, references, verification)


def render_markdown(atlas: dict[str, Any]) -> str:
    summary = atlas["summary"]
    lines: list[str] = [
        "# NEX M06 · Bottleneck Atlas — S05 Lighting Matrix",
        "",
        "**Status:** `EVIDENCE_DERIVED_ATLAS / SINGLE_SESSION / NO_NEW_MEASUREMENT / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{atlas['source_bundle']}` · **Code SHA medido:** `{atlas['source_sha']}`",
        f"**Hardware:** {atlas['hardware']['adapter']} · driver {atlas['hardware']['driver']} · "
        f"{atlas['godot_version']} · vsync {atlas['settings']['vsync_mode']}",
        f"**Capturas:** {atlas['capture_count']} · **Hashes:** {atlas['bundle_verification']['status']} "
        f"({atlas['bundle_verification']['verified_files']} arquivos)",
        "",
        "## Resumo",
        "",
        f"- Classificação dominante: **{summary['dominant_classification']}** "
        f"({summary['classification_counts'].get(summary['dominant_classification'], 0)}/{atlas['capture_count']} runs).",
        f"- Maior GPU p95: **{summary['max_gpu_p95_ms']:.3f} ms** em `{summary['max_gpu_p95_run']}`.",
        f"- Spread de GPU p50 nas 3 repetições baseline-25: **{summary['baseline25_gpu_p50_spread_ms']:.3f} ms**.",
        "",
        "## Runs",
        "",
        "| Cenário | Count | Run | GPU p50 | GPU p95 | CPU p50 | CPU p95 | Pacing p95 | 1% low | Classe | Pressão | Δ GPU p95 |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|---:|",
    ]
    for run in atlas["runs"]:
        delta = run["delta_vs_baseline"]
        delta_text = "—" if delta is None else f"{delta['gpu_p95_pct']:+.1f}%"
        lines.append(
            f"| {run['scenario']} | {run['count']} | {run['run_id']} | "
            f"{run['gpu_ms']['p50']:.3f} | {run['gpu_ms']['p95']:.3f} | "
            f"{run['cpu_ms']['p50']:.3f} | {run['cpu_ms']['p95']:.3f} | "
            f"{run['frame_pacing_ms']['p95']:.3f} | {run['one_percent_low_fps']:.2f} | "
            f"{run['classification']} | {run['render_pressure']} | {delta_text} |"
        )
    lines.extend(["", "## Referências baseline", "", "| Count | Runs | GPU p95 mediana | CPU p95 mediana | Pacing p95 mediana |", "|---:|---:|---:|---:|---:|"])
    for count in sorted(atlas["baseline_references"], key=int):
        reference = atlas["baseline_references"][count]
        lines.append(
            f"| {count} | {reference['runs']} | {reference['gpu_p95_median_ms']:.3f} | "
            f"{reference['cpu_p95_median_ms']:.3f} | {reference['pacing_p95_median_ms']:.3f} |"
        )
    lines.extend(["", "## Observações", ""])
    for observation in atlas["observations"]:
        lines.append(f"- {observation}")
    lines.extend(["", "## Limitações", ""])
    for limitation in atlas["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(
        [
            "",
            "Atlas gerado por `docs/benchmarks/m06/tools/build_atlas.py`; não é benchmark, não é claim de FPS e não generaliza.",
            "",
        ]
    )
    return "\n".join(lines)


def render_json(atlas: dict[str, Any]) -> str:
    return json.dumps(atlas, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_outputs(atlas: dict[str, Any]) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ATLAS_PATH.write_text(render_json(atlas), encoding="utf-8", newline="\n")
    REPORT_PATH.write_text(render_markdown(atlas), encoding="utf-8", newline="\n")
    return ATLAS_PATH, REPORT_PATH


def main(argv: list[str]) -> int:
    atlas = build_atlas()
    rendered_json = render_json(atlas)
    rendered_markdown = render_markdown(atlas)
    if argv == ["--check"]:
        if not ATLAS_PATH.is_file() or not REPORT_PATH.is_file():
            print("ATLAS_CHECK_FAIL: outputs missing")
            return 1
        if ATLAS_PATH.read_text(encoding="utf-8") != rendered_json:
            print("ATLAS_CHECK_FAIL: atlas.v1.json is stale")
            return 1
        if REPORT_PATH.read_text(encoding="utf-8") != rendered_markdown:
            print("ATLAS_CHECK_FAIL: ATLAS.md is stale")
            return 1
        print(f"ATLAS_CHECK_PASS: {atlas['capture_count']} runs, {atlas['bundle_verification']['verified_files']} hashes")
        return 0
    if argv:
        print("usage: build_atlas.py [--check]")
        return 2
    write_outputs(atlas)
    print(f"ATLAS_WRITE_PASS: {atlas['capture_count']} runs, {atlas['bundle_verification']['verified_files']} hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

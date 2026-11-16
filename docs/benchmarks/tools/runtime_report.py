"""Shared helpers for NEX native runtime report builders."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "m09" / "tools"))

from common import load_json, run_cli  # noqa: E402 - shared local tool module
from png_image import compare, read_png  # noqa: E402 - shared local tool module
from preset_report import load_capture, transform_run  # noqa: E402 - shared local tool module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pct(new: float, old: float) -> float:
    return round((new - old) / old * 100.0, 2)


def diff(first: Path, second: Path) -> dict:
    return compare(read_png(first), read_png(second), 2)


def load_manifest(path: Path, schema: str, source_sha: str, expected: int,
                  modes: tuple[str, ...] | None = None) -> dict:
    manifest = load_json(path)
    if manifest.get("schema_version") != schema:
        raise ValueError("runs manifest schema is invalid")
    if manifest.get("source_sha") != source_sha:
        raise ValueError("runs manifest source SHA is stale")
    runs = manifest.get("runs", [])
    if len(runs) != expected:
        raise ValueError(f"runs manifest must contain {expected} runs")
    if [entry.get("sequence") for entry in runs] != list(range(1, expected + 1)):
        raise ValueError("runs manifest sequence is invalid")
    if modes is not None and {entry.get("mode") for entry in runs} != set(modes):
        raise ValueError("runs manifest modes are incomplete")
    return manifest


def metrics(evidence: Path, manifest: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for entry in manifest["runs"]:
        capture = load_capture(evidence, entry["run_id"], entry["scene"], entry["layout"],
                               int(entry["proxy_count"]), include_allocation=True)
        result[entry["mode"]] = transform_run(entry, capture, include_allocation=True)
    return result


def run_lab_report(build, render_md, output: Path, json_path: Path, md_path: Path,
                   argv: list[str], prefix: str) -> int:
    return run_cli(build, render_json, render_md, output, json_path, md_path, argv, prefix)


def markdown_document(title: str, status: str, report: dict) -> list[str]:
    return [
        f"# {title}",
        "",
        f"**Status:** `{status}`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
    ]


def parse_pass_line(path: Path, prefix: str) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith(prefix):
            return int(line.split(":", 1)[1].strip().split()[0])
    raise ValueError(f"smoke log has no pass line for {prefix}")


def report_metadata(source_sha: str) -> dict:
    return {
        "source_sha": source_sha,
        "session_date": "2026-11-16",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
    }


def markdown_quality_table(rows: dict[str, dict], modes: tuple[str, ...]) -> list[str]:
    lines = ["| Perfil | GPU p95 | GPU vs base | Pixels |", "|---|---:|---:|---:|"]
    for mode in modes:
        row = rows[mode]
        lines.append(f"| {mode} | {row['gpu_p95_ms']:.3f} ms | {row['gpu_vs_baseline_pct']:+.2f}% | "
                     f"{row['changed_pixels_pct']:.3f}% |")
    return lines


def markdown_tail(report: dict, decisions: list[dict]) -> list[str]:
    lines = ["", "## S08 · decisões", ""]
    lines.extend(decision_lines(decisions))
    lines.extend([
        "",
        f"- {report['s08']['runs']} runs, {report['s08']['images']} imagens, "
        f"{report['s08']['planner_checks']} checks de planner, "
        f"{report['s08']['third_party_assets']} assets de terceiros.",
        "",
        "## Observações",
        "",
    ])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    return lines


def mode_rows(evidence: Path, manifest: dict, modes: tuple[str, ...],
              image_prefix: str) -> dict[str, dict]:
    images = evidence / "images"
    metric_rows = metrics(evidence, manifest)
    baseline = metric_rows["baseline"]
    rows: dict[str, dict] = {}
    for mode in modes:
        item = metric_rows[mode]
        image_diff = diff(images / f"{image_prefix}_baseline.png", images / f"{image_prefix}_{mode}.png") if mode != "baseline" else {
            "changed_pixels_pct": 0.0, "mean_abs_diff": 0.0, "psnr_db": None}
        rows[mode] = {
            "gpu_p95_ms": item["gpu_ms"]["p95"], "cpu_p95_ms": item["cpu_ms"]["p95"],
            "pacing_p95_ms": item["pacing_ms"]["p95"], "one_percent_low_fps": item["one_percent_low_fps"],
            "renderer_allocation_bytes": item["renderer_allocation_bytes"],
            "gpu_vs_baseline_pct": pct(item["gpu_ms"]["p95"], baseline["gpu_ms"]["p95"]),
            "cpu_vs_baseline_pct": pct(item["cpu_ms"]["p95"], baseline["cpu_ms"]["p95"]),
            "changed_pixels_pct": image_diff["changed_pixels_pct"],
            "mean_abs_diff": image_diff["mean_abs_diff"], "psnr_db": image_diff["psnr_db"],
            "png_bytes": (images / f"{image_prefix}_{mode}.png").stat().st_size,
        }
    return rows


def markdown_mode_table(rows: dict[str, dict], modes: tuple[str, ...]) -> list[str]:
    lines = ["| Modo | GPU p95 | CPU p95 | GPU vs base | Pixels | PSNR |",
             "|---|---:|---:|---:|---:|---:|"]
    for mode in modes:
        row = rows[mode]
        psnr = f"{row['psnr_db']:.2f} dB" if row["psnr_db"] is not None else "—"
        lines.append(f"| {mode} | {row['gpu_p95_ms']:.3f} ms | {row['cpu_p95_ms']:.3f} ms | "
                     f"{row['gpu_vs_baseline_pct']:+.2f}% | {row['changed_pixels_pct']:.3f}% | {psnr} |")
    return lines


def decision_lines(decisions: list[dict]) -> list[str]:
    lines = ["| Tecnologia | Decisão | Evidência |", "|---|---|---|"]
    for decision in decisions:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    return lines


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

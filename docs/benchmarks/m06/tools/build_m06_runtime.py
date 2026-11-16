#!/usr/bin/env python3
"""Build the M06 performance reference report from native lab evidence."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parents[1] / "m09" / "tools"))
sys.path.insert(0, str(TOOLS))
from common import load_json, run_cli  # noqa: E402 - shared local tool module
from convert_m09_observations import _bottleneck  # noqa: E402 - shared classifier
from png_image import compare, read_png  # noqa: E402 - shared local tool module
from preset_report import load_capture, summarize, transform_run  # noqa: E402 - shared local tool module

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "nex_bench" / "gpu_profile" / "evidence" / "windows-rtx5050-2026-11-16-m06"
IMAGES = EVIDENCE / "images"
LOGS = EVIDENCE / "logs"
OUTPUT = REPO / "docs" / "benchmarks" / "m06"
REPORT_JSON = OUTPUT / "m06-runtime.v1.json"
REPORT_MD = OUTPUT / "M06-RUNTIME.md"
SOURCE_SHA = "c763319d04d0bf353c15db8378872bdf8fab1734"
SCENES = ("corridor_static", "arena_combat", "dense_city")
SCALE_TAGS = {"scale_100": 1.0, "scale_085": 0.85, "scale_070": 0.7}
FILLRATE_COUNTS = (1, 10, 100)
FILLRATE_RESOLUTIONS = ((1280, 720), (1920, 1080), (2560, 1440))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pct(new: float, old: float) -> float:
    return round((new - old) / old * 100.0, 2)


def _diff(first: Path, second: Path) -> dict[str, Any]:
    return compare(read_png(first), read_png(second), 2)


def _log_json(path: Path, prefix: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in reversed(text.splitlines()):
        if line.startswith(prefix):
            return json.loads(line[len(prefix):])
    return {}


def _load_manifest() -> dict[str, Any]:
    manifest = load_json(EVIDENCE / "runs.v1.json")
    if manifest.get("schema_version") != "m06_lab_runs.v1":
        raise ValueError("M06 runs manifest schema is invalid")
    if manifest.get("source_sha") != SOURCE_SHA:
        raise ValueError("M06 runs manifest source SHA is stale")
    runs = manifest.get("runs", [])
    if len(runs) != 33:
        raise ValueError("M06 runs manifest must contain 33 runs")
    if [entry.get("sequence") for entry in runs] != list(range(1, 34)):
        raise ValueError("M06 runs manifest sequence is invalid")
    return manifest


def _group_metrics(manifest: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for entry in manifest["runs"]:
        capture = load_capture(EVIDENCE, entry["run_id"], entry["scene"], entry["layout"],
                               int(entry["proxy_count"]), include_allocation=True)
        run = transform_run(entry, capture, include_allocation=True)
        groups.setdefault((entry["mode"], entry["scene_id"], entry["variant"]), []).append(run)
    return {key: summarize(group, include_allocation=True) for key, group in groups.items()}


def _smoke(name: str) -> dict[str, Any]:
    return load_json(EVIDENCE / name)


def _instancing_rows(metrics: dict[tuple[str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scene in SCENES:
        base = metrics[("instancing", scene, "individual")]
        for variant in ("individual", "multimesh", "batched"):
            item = metrics[("instancing", scene, variant)]
            log = LOGS / f"{scene}_instancing_{variant}.log"
            m06 = _log_json(log, "NEX_PRESET_AB_M06 ")
            render = _log_json(log, "NEX_PRESET_AB_M06_METRICS ")
            image = IMAGES / f"{scene}_instancing_{variant}.png"
            diff = _diff(IMAGES / f"{scene}_instancing_individual.png", image) if variant != "individual" else {
                "changed_pixels_pct": 0.0, "mean_abs_diff": 0.0, "psnr_db": 100.0}
            rows.append({
                "scene": scene, "variant": variant,
                "gpu_p95_ms": item["gpu_p95_ms"], "cpu_p95_ms": item["cpu_p95_ms"],
                "one_percent_low_fps": item["one_percent_low_fps"],
                "gpu_vs_individual_pct": _pct(item["gpu_p95_ms"], base["gpu_p95_ms"]),
                "cpu_vs_individual_pct": _pct(item["cpu_p95_ms"], base["cpu_p95_ms"]),
                "draw_calls": int(render.get("draw_calls", 0)),
                "objects": int(render.get("objects", 0)),
                "primitives": int(render.get("primitives", 0)),
                "groups": int(m06.get("groups", 0)),
                "instances": int(m06.get("instances", 0)),
                "changed_pixels_pct": diff["changed_pixels_pct"],
                "psnr_db": diff["psnr_db"],
                "png_bytes": image.stat().st_size,
            })
    return rows


def _lod_rows(metrics: dict[tuple[str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scene in SCENES:
        high = metrics[("lod", scene, "high")]
        governor = metrics[("lod", scene, "governor")]
        log = LOGS / f"{scene}_lod_governor.log"
        counts = _log_json(log, "NEX_PRESET_AB_M06 ")
        diff = _diff(IMAGES / f"{scene}_lod_high.png", IMAGES / f"{scene}_lod_governor.png")
        rows.append({
            "scene": scene,
            "high_gpu_p95_ms": high["gpu_p95_ms"], "governor_gpu_p95_ms": governor["gpu_p95_ms"],
            "gpu_delta_pct": _pct(governor["gpu_p95_ms"], high["gpu_p95_ms"]),
            "high_one_percent_low_fps": high["one_percent_low_fps"],
            "governor_one_percent_low_fps": governor["one_percent_low_fps"],
            "one_percent_low_delta_pct": _pct(governor["one_percent_low_fps"], high["one_percent_low_fps"]),
            "high_instances": int(counts.get("high", 0)), "low_instances": int(counts.get("low", 0)),
            "changed_pixels_pct": diff["changed_pixels_pct"],
            "mean_abs_diff": diff["mean_abs_diff"], "psnr_db": diff["psnr_db"],
        })
    return rows


def _frustum_rows(metrics: dict[tuple[str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scene in SCENES:
        off = metrics[("frustum", scene, "off")]
        on = metrics[("frustum", scene, "on")]
        counts = _log_json(LOGS / f"{scene}_frustum_on.log", "NEX_PRESET_AB_M06 ")
        off_render = _log_json(LOGS / f"{scene}_frustum_off.log", "NEX_PRESET_AB_M06_METRICS ")
        on_render = _log_json(LOGS / f"{scene}_frustum_on.log", "NEX_PRESET_AB_M06_METRICS ")
        diff = _diff(IMAGES / f"{scene}_frustum_off.png", IMAGES / f"{scene}_frustum_on.png")
        rows.append({
            "scene": scene,
            "off_gpu_p95_ms": off["gpu_p95_ms"], "on_gpu_p95_ms": on["gpu_p95_ms"],
            "gpu_delta_pct": _pct(on["gpu_p95_ms"], off["gpu_p95_ms"]),
            "off_cpu_p95_ms": off["cpu_p95_ms"], "on_cpu_p95_ms": on["cpu_p95_ms"],
            "cpu_delta_pct": _pct(on["cpu_p95_ms"], off["cpu_p95_ms"]),
            "off_draw_calls": int(off_render.get("draw_calls", 0)),
            "on_draw_calls": int(on_render.get("draw_calls", 0)),
            "visible": int(counts.get("visible", 0)), "culled": int(counts.get("culled", 0)),
            "changed_pixels_pct": diff["changed_pixels_pct"],
            "mean_abs_diff": diff["mean_abs_diff"], "psnr_db": diff["psnr_db"],
        })
    return rows


def _render_scale_rows(metrics: dict[tuple[str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base = metrics[("render_scale", "arena_combat", "scale_100")]
    for tag in ("scale_100", "scale_085", "scale_070"):
        item = metrics[("render_scale", "arena_combat", tag)]
        diff = _diff(IMAGES / "arena_combat_render_scale_scale_100.png",
                     IMAGES / f"arena_combat_render_scale_{tag}.png") if tag != "scale_100" else {
            "changed_pixels_pct": 0.0, "mean_abs_diff": 0.0, "psnr_db": 100.0}
        rows.append({
            "tag": tag, "scale": SCALE_TAGS[tag],
            "gpu_p95_ms": item["gpu_p95_ms"], "gpu_delta_pct": _pct(item["gpu_p95_ms"], base["gpu_p95_ms"]),
            "one_percent_low_fps": item["one_percent_low_fps"],
            "changed_pixels_pct": diff["changed_pixels_pct"],
            "mean_abs_diff": diff["mean_abs_diff"], "psnr_db": diff["psnr_db"],
        })
    return rows


def _overdraw(count: int, width: int, height: int, sprite_px: float = 64.0, layers: int = 1) -> float:
    return round(count * sprite_px * sprite_px * layers / float(width * height), 4)


def _fillrate_rows(metrics: dict[tuple[str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for count in FILLRATE_COUNTS:
        for width, height in FILLRATE_RESOLUTIONS:
            key = ("fillrate", "corridor_static", f"{count}_{width}x{height}")
            item = metrics[key]
            rows.append({
                "count": count, "width": width, "height": height,
                "gpu_p95_ms": item["gpu_p95_ms"], "cpu_p95_ms": item["cpu_p95_ms"],
                "one_percent_low_fps": item["one_percent_low_fps"],
                "overdraw_proxy": _overdraw(count, width, height),
                "renderer_allocation_bytes": item["renderer_allocation_bytes_median"],
            })
    return rows


def _classification_counts(metrics: dict[tuple[str, str, str], dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for key, item in sorted(metrics.items()):
        bottleneck = _bottleneck(item["gpu_p95_ms"], item["cpu_p95_ms"], item["pacing_p95_ms"])
        classification = str(bottleneck["classification"])
        counts[classification] = counts.get(classification, 0) + 1
        rows.append({"group": "/".join(key), "classification": classification,
                     "gpu_p95_ms": item["gpu_p95_ms"], "cpu_p95_ms": item["cpu_p95_ms"],
                     "pacing_p95_ms": item["pacing_p95_ms"],
                     "gpu_share_of_frame_pct": round(item["gpu_p95_ms"] / item["pacing_p95_ms"] * 100.0, 2)})
    return {"groups": rows, "classifications": counts, "verdict": "BOTTLENECK_ATLAS_DERIVED"}


def build_report() -> dict[str, Any]:
    manifest = _load_manifest()
    metrics = _group_metrics(manifest)
    modules = _smoke("modules-smoke-2026-11-16.json")
    stream = _smoke("stream-smoke-2026-11-16.json")
    vram = _smoke("vram-smoke-2026-11-16.json")
    if modules.get("verdict") != "PASS" or int(modules.get("checks", 0)) < 70:
        raise ValueError("M06 module smoke did not pass")
    if stream.get("verdict") != "PASS" or int(stream.get("checks", 0)) < 15:
        raise ValueError("M06 stream smoke did not pass")
    if vram.get("verdict") != "PASS" or int(vram.get("checks", 0)) < 8:
        raise ValueError("M06 VRAM smoke did not pass")
    instancing = _instancing_rows(metrics)
    lod = _lod_rows(metrics)
    frustum = _frustum_rows(metrics)
    render_scale = _render_scale_rows(metrics)
    fillrate = _fillrate_rows(metrics)
    images = sorted(IMAGES.glob("*.png"))
    if len(images) != 27:
        raise ValueError("M06 lab must contain 27 images")
    fillrate_by_key = {(row["count"], row["width"]): row for row in fillrate}
    resolution_scaling = {
        str(count): {
            "1080p_vs_720p_pct": _pct(fillrate_by_key[(count, 1920)]["gpu_p95_ms"], fillrate_by_key[(count, 1280)]["gpu_p95_ms"]),
            "1440p_vs_720p_pct": _pct(fillrate_by_key[(count, 2560)]["gpu_p95_ms"], fillrate_by_key[(count, 1280)]["gpu_p95_ms"]),
        }
        for count in FILLRATE_COUNTS
    }
    count_scaling = {
        f"{width}x{height}": {
            "10_vs_1_pct": _pct(fillrate_by_key[(10, width)]["gpu_p95_ms"], fillrate_by_key[(1, width)]["gpu_p95_ms"]),
            "100_vs_1_pct": _pct(fillrate_by_key[(100, width)]["gpu_p95_ms"], fillrate_by_key[(1, width)]["gpu_p95_ms"]),
        }
        for width, height in FILLRATE_RESOLUTIONS
    }
    instancing_draw_calls = {
        scene: {row["variant"]: row["draw_calls"] for row in instancing if row["scene"] == scene}
        for scene in SCENES
    }
    decisions = [
        {"id": "Bottleneck Atlas", "decision": "GO",
         "evidence": "33 native runs classified from measured GPU/CPU/pacing"},
        {"id": "BatchWeave / MultiMesh", "decision": "GO",
         "evidence": "draw calls fall 385->223 in corridor with near-zero image diff"},
        {"id": "LOD Governor", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "GPU p95 -8.2%/-7.1%/-1.0%; 1% low mixed and 0.967-4.314% pixels change"},
        {"id": "Occlusion Mapper / custom frustum", "decision": "NO_GO",
         "evidence": "GPU unchanged; arena false-hide 2.284% and no corridor draw-call gain"},
        {"id": "StreamGuard", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "17 checks; cold loads 14.0-21.0 ms; no scene streaming policy"},
        {"id": "FramePacer / static render scale", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "GPU -15.4% at 0.85 and -28.2% at 0.7; 2.478-3.748% pixels change"},
        {"id": "VRAM Sentinel", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "engine video memory 12.6 MB -> 211.5 MB while loading 22 textures"},
        {"id": "FillRate X-Ray", "decision": "GO_WITH_LIMITATIONS",
         "evidence": "1440p +135.9% vs 720p at 1 event; 100 events +11.1% vs 1 at 1080p"},
    ]
    return {
        "schema_version": "m06_performance_runtime.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-16",
        "hardware": {"gpu": "NVIDIA GeForce RTX 5050", "driver": "NVIDIA 617.14 / Vulkan forward_plus"},
        "godot_version": "4.7.2-stable",
        "s01": _classification_counts(metrics),
        "s02": {"rows": instancing, "draw_calls": instancing_draw_calls, "verdict": "BATCH_WEAVE_GO"},
        "s03": {"rows": lod, "verdict": "LOD_GOVERNOR_GO_WITH_LIMITATIONS"},
        "s04": {"rows": frustum, "occlusion_culling": "INCONCLUSIVE_NOT_BAKED",
                "verdict": "CUSTOM_FRUSTUM_NO_GO"},
        "s05": {
            "checks": int(stream["checks"]), "failures": stream["failures"],
            "frames_waited": int(stream["frames_waited"]),
            "timings": stream["timings"], "counts": stream["state"]["counts"],
            "verdict": "STREAM_GUARD_GO_WITH_LIMITATIONS",
        },
        "s06": {
            "checks": int(modules["checks"]), "rows": render_scale,
            "policy": "hysteresis + cooldown; adaptive dynamic policy not enabled",
            "verdict": "FRAMEPACER_RESEARCH_GO_WITH_LIMITATIONS",
        },
        "s07": {"decisions": decisions},
        "s08": {
            "runs": 33, "images": len(images), "module_checks": int(modules["checks"]),
            "stream_checks": int(stream["checks"]), "vram_checks": int(vram["checks"]),
            "third_party_assets": 0, "verdict": "M06_PERFORMANCE_QA_VERIFIED",
        },
        "s09": {
            "checks": int(vram["checks"]), "textures_loaded": int(vram["textures_loaded"]),
            "before": vram["before"], "after": vram["after"], "delta_bytes": int(vram["delta_bytes"]),
            "evaluation": vram["evaluation"], "verdict": "VRAM_SENTINEL_GO_WITH_LIMITATIONS",
        },
        "s10": {
            "rows": fillrate, "resolution_scaling": resolution_scaling, "count_scaling": count_scaling,
            "sprite_px": 64, "layers": 1, "fragment_counter": "UNAVAILABLE",
            "verdict": "FILL_RATE_XRAY_GO_WITH_LIMITATIONS",
        },
        "verdict": "M06_PERFORMANCE_REFERENCE_DERIVED",
        "observations": [
            "33 native runs cover instancing, LOD, frustum, render scale and fillrate",
            "MultiMesh keeps the frame visually identical while reducing corridor draw calls 385->223",
            "LOD Governor lowers GPU p95 by 8.2%/7.1%/1.0% with 0.967-4.314% pixel change",
            "custom frustum mapping does not reduce GPU time and hides 2.284% of the arena frame",
            "render scale 0.85/0.70 lowers GPU p95 by 15.4%/28.2% with 2.478%/3.748% pixel change",
            "100 VFX events at 1440p cost 5.578 ms GPU p95 versus 5.061 ms at 1 event",
            "StreamGuard loads three scenes in 14.0-21.0 ms with 17 checks",
            "VRAM Sentinel observes 198.9 MB of engine video memory for 22 loaded textures",
        ],
        "limitations": [
            "single session, one GPU and driver; 1920x1080 lab unless stated",
            "custom LOD governor is not Godot automatic mesh LOD or a production LOD engine",
            "true occlusion culling requires baked occluders and was not exercised",
            "no dynamic adaptive render scale, no shader prewarm and no VRAM eviction",
            "draw calls are engine counters, not per-material GPU pipeline proof",
            "overdraw is a deterministic proxy, not a fragment counter",
            "no production game, no PoE2 parity and no generalized FPS claim",
        ],
        "runs": 33,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M06 · Performance runtime",
        "",
        "**Status:** `M06_PERFORMANCE_REFERENCE_DERIVED / NATIVE_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **GPU:** {report['hardware']['gpu']} · {report['godot_version']}",
        "",
        "## S01 · Bottleneck Atlas",
        "",
        f"- **{report['s01']['verdict']}**: {sum(report['s01']['classifications'].values())} grupos nativos.",
        f"- Classificações: `{report['s01']['classifications']}`.",
        "",
        "## S02 · BatchWeave",
        "",
        "| Cena | Variante | GPU p95 | CPU p95 | Draw calls | GPU vs individual | Pixels |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["s02"]["rows"]:
        lines.append(f"| {row['scene']} | {row['variant']} | {row['gpu_p95_ms']:.3f} ms | "
                     f"{row['cpu_p95_ms']:.3f} ms | {row['draw_calls']} | "
                     f"{row['gpu_vs_individual_pct']:+.2f}% | {row['changed_pixels_pct']:.3f}% |")
    lines.extend([
        "",
        "## S03 · LOD Governor",
        "",
        "| Cena | High GPU | Governor GPU | Delta GPU | 1% low delta | High/Low | Pixels | PSNR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["s03"]["rows"]:
        lines.append(f"| {row['scene']} | {row['high_gpu_p95_ms']:.3f} ms | {row['governor_gpu_p95_ms']:.3f} ms | "
                     f"{row['gpu_delta_pct']:+.2f}% | {row['one_percent_low_delta_pct']:+.2f}% | "
                     f"{row['high_instances']}/{row['low_instances']} | {row['changed_pixels_pct']:.3f}% | "
                     f"{row['psnr_db']:.2f} dB |")
    lines.extend([
        "",
        "## S04 · Occlusion Mapper",
        "",
        "| Cena | GPU off | GPU on | Delta GPU | CPU delta | Draw calls | Culled | Pixels |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["s04"]["rows"]:
        lines.append(f"| {row['scene']} | {row['off_gpu_p95_ms']:.3f} ms | {row['on_gpu_p95_ms']:.3f} ms | "
                     f"{row['gpu_delta_pct']:+.2f}% | {row['cpu_delta_pct']:+.2f}% | "
                     f"{row['off_draw_calls']}->{row['on_draw_calls']} | {row['culled']} | "
                     f"{row['changed_pixels_pct']:.3f}% |")
    lines.extend([
        "",
        f"- Oclusão real: **{report['s04']['occlusion_culling']}** (sem occluders baked).",
        "",
        "## S05 · StreamGuard",
        "",
        f"- **{report['s05']['checks']} checks**, {report['s05']['frames_waited']} frames até pronto; "
        f"estado `{report['s05']['counts']}`.",
    ])
    for item in report["s05"]["timings"]:
        lines.append(f"- `{item['path']}`: {item['elapsed_ms']:.3f} ms")
    lines.extend([
        "",
        "## S06 · FramePacer / render scale",
        "",
        "| Escala | GPU p95 | Delta | 1% low | Pixels | PSNR |",
        "|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["s06"]["rows"]:
        lines.append(f"| {row['scale']:.2f} | {row['gpu_p95_ms']:.3f} ms | {row['gpu_delta_pct']:+.2f}% | "
                     f"{row['one_percent_low_fps']:.2f} | {row['changed_pixels_pct']:.3f}% | {row['psnr_db']:.2f} dB |")
    lines.extend([
        "",
        "## S07 · decisões",
        "",
        "| Tecnologia | Decisão | Evidência |",
        "|---|---|---|",
    ])
    for decision in report["s07"]["decisions"]:
        lines.append(f"| {decision['id']} | **{decision['decision']}** | {decision['evidence']} |")
    lines.extend([
        "",
        "## S08 · QA",
        "",
        f"- {report['s08']['runs']} runs, {report['s08']['images']} imagens, "
        f"{report['s08']['module_checks']} checks de módulos, {report['s08']['stream_checks']} de streaming e "
        f"{report['s08']['vram_checks']} de VRAM.",
        "",
        "## S09 · VRAM Sentinel",
        "",
        f"- {report['s09']['textures_loaded']} texturas; engine video memory "
        f"{report['s09']['before']['video_bytes']} -> {report['s09']['after']['video_bytes']} bytes "
        f"(+{report['s09']['delta_bytes']}).",
        f"- Estado `{report['s09']['evaluation']['state']}` com ratio {report['s09']['evaluation']['ratio']}.",
        "",
        "## S10 · FillRate X-Ray",
        "",
        "| Eventos | Resolução | GPU p95 | CPU p95 | Overdraw proxy |",
        "|---:|---|---:|---:|---:|",
    ])
    for row in report["s10"]["rows"]:
        lines.append(f"| {row['count']} | {row['width']}x{row['height']} | {row['gpu_p95_ms']:.3f} ms | "
                     f"{row['cpu_p95_ms']:.3f} ms | {row['overdraw_proxy']:.4f} |")
    lines.extend([
        "",
        "## Observações",
        "",
    ])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m06/tools/build_m06_runtime.py`; não é paridade com PoE2.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT, REPORT_JSON, REPORT_MD,
                   argv, "M06_PERFORMANCE_RUNTIME")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

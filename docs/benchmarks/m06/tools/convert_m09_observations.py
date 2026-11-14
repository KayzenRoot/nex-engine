#!/usr/bin/env python3
"""Convert selected M09 GPU-profile captures into performance.v1 observations.

The converter reads already integrated evidence, maps measured aggregates into
the M06 contract, marks unavailable fields explicitly and classifies the
bottleneck. It performs no new measurement and does not admit M06.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_ROOT = REPO_ROOT / "nex_bench/gpu_profile/evidence"
OUTPUT = REPO_ROOT / "docs/benchmarks/m06/observations/m09-observations.v1.json"
SCHEMA_VERSION = "performance.v1"
BUNDLE_VERSION = "m06_observation_bundle.v1"

SELECTORS = (
    {"bundle": "windows-rtx5050-2026-11-14-preset-ab", "sequence": 1, "id": "m09-preset-ab-low"},
    {"bundle": "windows-rtx5050-2026-11-14-preset-ab", "sequence": 2, "id": "m09-preset-ab-high"},
    {"bundle": "windows-rtx5050-2026-11-14-m01-ab", "sequence": 1, "id": "m09-m01-corridor-low"},
    {"bundle": "windows-rtx5050-2026-11-14-m01-ab", "sequence": 2, "id": "m09-m01-corridor-high"},
    {"bundle": "windows-rtx5050-2026-11-14-res-scaling", "sequence": 1, "id": "m09-res-960-low"},
    {"bundle": "windows-rtx5050-2026-11-14-res-scaling", "sequence": 2, "id": "m09-res-960-high"},
    {"bundle": "windows-rtx5050-2026-11-14-res-scaling", "sequence": 13, "id": "m09-res-1920-low"},
    {"bundle": "windows-rtx5050-2026-11-14-res-scaling", "sequence": 14, "id": "m09-res-1920-high"},
    {"bundle": "windows-rtx5050-2026-11-14-interaction-200", "sequence": 1, "id": "m09-i200-960-low"},
    {"bundle": "windows-rtx5050-2026-11-14-interaction-200", "sequence": 2, "id": "m09-i200-960-high"},
    {"bundle": "windows-rtx5050-2026-11-14-interaction-200", "sequence": 7, "id": "m09-i200-1920-low"},
    {"bundle": "windows-rtx5050-2026-11-14-interaction-200", "sequence": 8, "id": "m09-i200-1920-high"},
)

SCENE_IDS = {
    "Preset A/B/A": "preset-ab",
    "M01 Corridor A/B/A": "m01-corridor",
    "M01 Arena A/B/A": "m01-arena",
    "M01 City A/B/A": "m01-city",
}


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_non_finite(token: str) -> None:
    raise ValueError("non-finite JSON: " + token)


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_non_finite,
    )


def _entry(manifest: dict[str, Any], sequence: int) -> dict[str, Any]:
    matches = [entry for entry in manifest["runs"] if entry.get("sequence") == sequence]
    if len(matches) != 1:
        raise ValueError(f"manifest sequence {sequence} is not unique")
    return matches[0]


def _series(document: dict[str, Any], key: str, aggregate: str) -> float:
    entry = document.get("series", {}).get(key)
    if not isinstance(entry, dict) or entry.get("status") != "MEASURED":
        raise ValueError(f"{key} is not MEASURED")
    value = entry.get("aggregates", {}).get(aggregate)
    if not isinstance(value, (int, float)):
        raise ValueError(f"{key}.{aggregate} is missing")
    return float(value)


def _first_raw_csv(snapshot: Any) -> str:
    if not isinstance(snapshot, dict):
        return ""
    samples = snapshot.get("samples")
    if not isinstance(samples, list):
        return ""
    for sample in samples:
        if isinstance(sample, dict) and isinstance(sample.get("raw_csv"), str):
            return sample["raw_csv"]
    return ""


def _raw_csv(document: dict[str, Any]) -> str:
    snapshots = document.get("device_snapshots")
    if not isinstance(snapshots, list):
        single = document.get("device_snapshot")
        snapshots = [single] if isinstance(single, dict) else []
    for snapshot in snapshots:
        raw = _first_raw_csv(snapshot)
        if raw:
            return raw
    return ""


def _driver_version(document: dict[str, Any]) -> str:
    raw = _raw_csv(document)
    if raw and "," in raw:
        fields = [field.strip() for field in raw.split(",")]
        if len(fields) > 1 and fields[1]:
            return fields[1]
    return str(document.get("driver") or "unknown")


def _bottleneck(gpu_ms: float, cpu_ms: float, pacing_ms: float) -> dict[str, Any]:
    if pacing_ms > max(gpu_ms, cpu_ms) + 1.0:
        return {
            "classification": "pacing",
            "evidence": "measured",
            "confidence": "high",
            "rationale": (
                f"frame pacing p95 {pacing_ms:.3f} ms exceeds max(gpu {gpu_ms:.3f}, "
                f"cpu {cpu_ms:.3f}) by more than 1 ms; the 240 fps cap dominates."
            ),
        }
    if gpu_ms > cpu_ms * 1.5:
        return {
            "classification": "gpu",
            "evidence": "measured",
            "confidence": "medium",
            "rationale": f"GPU p95 {gpu_ms:.3f} ms exceeds CPU p95 {cpu_ms:.3f} ms by more than 50%.",
        }
    if cpu_ms > gpu_ms * 1.5:
        return {
            "classification": "cpu",
            "evidence": "measured",
            "confidence": "medium",
            "rationale": f"CPU p95 {cpu_ms:.3f} ms exceeds GPU p95 {gpu_ms:.3f} ms by more than 50%.",
        }
    return {
        "classification": "unknown",
        "evidence": "measured",
        "confidence": "low",
        "rationale": "GPU and CPU render p95 are within 50% of each other; no render pressure dominates.",
    }


def _observation(selector: dict[str, Any]) -> dict[str, Any]:
    bundle = EVIDENCE_ROOT / selector["bundle"]
    manifest = load_json(bundle / "runs.v1.json")
    entry = _entry(manifest, selector["sequence"])
    run_id = entry["run_id"]
    capture = load_json(bundle / f"gpu_profile_{run_id}.json")
    if capture.get("run_status") != "COMPLETE":
        raise ValueError(f"{run_id}: run_status is not COMPLETE")
    workload = capture.get("workload", {})
    scene = workload.get("scene")
    if scene not in SCENE_IDS:
        raise ValueError(f"{run_id}: unsupported scene {scene!r}")
    width, height = capture["viewport"]["resolution_px"]
    gpu_ms = _series(capture, "GPU_RENDER_MS", "p95")
    cpu_ms = _series(capture, "CPU_RENDER_MS", "p95")
    pacing_ms = _series(capture, "FRAME_PACING_INTERVAL_MS", "p95")
    allocation = _series(capture, "RENDERER_ALLOCATION_BYTES", "p50")
    source_sha = capture.get("source_sha")
    if not isinstance(source_sha, str) or len(source_sha) != 40:
        raise ValueError(f"{run_id}: invalid source_sha")
    return {
        "schema_version": SCHEMA_VERSION,
        "observation_id": selector["id"],
        "captured_at_utc": capture["captured_at_utc"],
        "workload": {
            "scene_id": SCENE_IDS[scene],
            "proxy_count": int(workload.get("proxy_count", 0)),
            "effect_mode": "lights",
            "resolution": {"width_px": int(width), "height_px": int(height), "unit": "px"},
            "vsync": int(capture.get("settings", {}).get("vsync_mode", 0)) != 0,
            "max_fps": int(capture.get("settings", {}).get("max_fps", 0)),
        },
        "frame_interval": {
            "status": "UNAVAILABLE",
            "provider": "SceneTree._process(delta)",
            "unavailable_reason": "raw interval samples are retained in the source capture",
        },
        "timings": {
            "gpu_render_ms": {"status": "MEASURED", "value": round(gpu_ms, 3)},
            "cpu_render_ms": {"status": "MEASURED", "value": round(cpu_ms, 3)},
            "frame_pacing_ms": {"status": "MEASURED", "value": round(pacing_ms, 3)},
        },
        "resources": {
            "draw_calls": {"status": "UNAVAILABLE", "unavailable_reason": "the profiler does not expose draw calls"},
            "objects_rendered": {
                "status": "UNAVAILABLE",
                "unavailable_reason": "object count is declared by the workload, not queried from the renderer",
            },
            "renderer_allocation_bytes": {"status": "MEASURED", "value": int(allocation)},
            "vram_used_bytes": {"status": "UNAVAILABLE", "unavailable_reason": "device VRAM is not process-attributed"},
        },
        "bottleneck": _bottleneck(gpu_ms, cpu_ms, pacing_ms),
        "provenance": {
            "base_sha": source_sha,
            "head_sha": source_sha,
            "godot_version": str(capture.get("godot_version", "unknown")),
            "hardware": {
                "gpu_model": str(capture.get("adapter", "unknown")),
                "driver_version": _driver_version(capture),
            },
            "capture_mode": "windowed",
            "measurement_status": "MEASURED",
            "evidence_uri": (
                "nex_bench/gpu_profile/evidence/"
                + selector["bundle"]
                + "/gpu_profile_"
                + run_id
                + ".json"
            ),
        },
    }


def build_bundle() -> dict[str, Any]:
    observations = [_observation(selector) for selector in SELECTORS]
    if len({observation["observation_id"] for observation in observations}) != len(observations):
        raise ValueError("observation ids must be unique")
    return {
        "schema_version": BUNDLE_VERSION,
        "source": "M09 integrated evidence bundles",
        "observations": observations,
    }


def render_json(bundle: dict[str, Any]) -> str:
    return json.dumps(bundle, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    bundle = build_bundle()
    rendered = render_json(bundle)
    if argv == ["--check"]:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("M06_OBS_CHECK_FAIL: output is stale")
            return 1
        print(f"M06_OBS_CHECK_PASS: {len(bundle['observations'])} observations")
        return 0
    if argv:
        print("usage: convert_m09_observations.py [--check]")
        return 2
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)
    print(f"M06_OBS_WRITE_PASS: {len(bundle['observations'])} observations")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

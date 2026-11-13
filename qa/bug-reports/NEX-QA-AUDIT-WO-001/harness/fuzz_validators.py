#!/usr/bin/env python3
"""Deterministic robustness harness for NEX validators (NEX-QA-AUDIT-WO-001, Issue #20).

Runs a fixed corpus of malformed/edge-case inputs against the repository's
parsers and validators, classifying controlled rejections versus unexpected
exceptions. No network, no randomness, no writes outside a temporary directory.
"""
from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
REPORT_DIR = Path(__file__).resolve().parent.parent


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GPU_VALIDATOR = load_module(REPO / "nex_bench" / "gpu_profile" / "validate_gpu_profile.py", "qa_gpu_validator")
FRAMEPULSE = load_module(REPO / "nex_bench" / "telemetry" / "framepulse.py", "qa_framepulse")
COMPARE = load_module(REPO / "nex_bench" / "visual_truth" / "compare.py", "qa_compare")
CI_BUILD = load_module(REPO / "tooling" / "godot" / "ci_build.py", "qa_ci_build")

RESULTS: dict[str, dict] = {}


def record(target: str, case: str, expected: str, outcome: str, detail: str = "") -> None:
    bucket = RESULTS.setdefault(target, {"cases": 0, "expected_accept": 0, "expected_reject": 0, "unexpected": [], "unexpected_accepts": []})
    bucket["cases"] += 1
    bucket[f"expected_{expected}"] += 1
    if outcome == "unexpected_exception":
        bucket["unexpected"].append({"case": case, "detail": detail})
    elif outcome == "unexpected_accept":
        bucket["unexpected_accepts"].append({"case": case, "detail": detail})


def run_case(target: str, case: str, expected: str, call, *, controlled=(ValueError,)) -> None:
    try:
        call()
    except controlled as exc:  # controlled, documented rejection family
        if expected == "accept":
            record(target, case, expected, "unexpected_exception", f"{type(exc).__name__}: {exc}")
        else:
            record(target, case, expected, "rejected")
    except Exception as exc:  # noqa: BLE001 - the point is to catch unexpected exception types
        record(target, case, expected, "unexpected_exception", f"{type(exc).__name__}: {exc}")
    else:
        if expected == "reject":
            record(target, case, expected, "unexpected_accept", "accepted an input the contract marks invalid")
        else:
            record(target, case, expected, "accepted")


# ---------------------------------------------------------------- GPU validator
def gpu_case(payload: bytes, expected: str = "reject") -> None:
    run_case("gpu_profile_validator", payload[:60].decode("utf-8", "replace") or "<empty>", expected,
             lambda: GPU_VALIDATOR.validate_payload(payload), controlled=(ValueError,))


gpu_malformed = [
    b"",
    b"null",
    b"[]",
    b"{}",
    b'{"a":1,"a":2}',
    b'{"sample":NaN}',
    b'{"sample":Infinity}',
    b'{"sample":-Infinity}',
    b'{"sample":1e9999}',
    b'{"x":' + b"9" * 400 + b"}",
    b"[" * 2000 + b"]" * 2000,
    b'{"truncated":',
    b"\xff\xfe\x00\x01",
    b'{"schema_version":"nex_gpu_render_profile.v2"}',
    b'{"schema_version":"unsupported"}',
    b"[" * 10000,
]
for index, payload in enumerate(gpu_malformed):
    gpu_case(payload)

oversized = b'{"padding":"' + b"a" * (8_000_001) + b'"}'
gpu_case(oversized)

# ---------------------------------------------------------------- framepulse
def framepulse_raw(payload: str, expected: str = "reject") -> None:
    run_case("framepulse_analyzer", payload[:60] or "<empty>", expected,
             lambda: FRAMEPULSE.analyze_json(payload), controlled=(ValueError,))


FRAMEPULSE_FIXTURE = (REPO / "nex_bench" / "telemetry" / "fixtures" / "synthetic_run.v1.json").read_text(encoding="utf-8")
run_case("framepulse_analyzer", "synthetic fixture", "accept", lambda: FRAMEPULSE.analyze_json(FRAMEPULSE_FIXTURE))

for payload in [
    "",
    "null",
    "[]",
    "{}",
    '{"a":1,"a":2}',
    '{"sample":NaN}',
    '{"sample":Infinity}',
    '{"sample":1e9999}',
    '{"truncated":',
    '{"frame_times_ms": [1, "x"]}',
    "[" * 10000,
]:
    framepulse_raw(payload)

fixture = json.loads(FRAMEPULSE_FIXTURE)
mutations = []
mutated = json.loads(json.dumps(fixture))
mutated["sample_count"] = mutated["sample_count"] + 1
mutations.append(("sample_count mismatch", mutated))
mutated = json.loads(json.dumps(fixture))
mutated["samples"][1]["timestamp_ms"] = mutated["samples"][0]["timestamp_ms"]
mutations.append(("non-monotonic timestamp", mutated))
mutated = json.loads(json.dumps(fixture))
mutated["samples"][0]["frame_time_ms"] = -1.0
mutations.append(("negative frame time", mutated))
mutated = json.loads(json.dumps(fixture))
mutated["frame_time_unit"] = "seconds"
mutations.append(("wrong frame unit", mutated))
for label, mutated in mutations:
    run_case("framepulse_analyzer", label, "reject",
             lambda mutated=mutated: FRAMEPULSE.analyze_json(json.dumps(mutated)), controlled=(ValueError,))


# ---------------------------------------------------------------- PNG parser
def png_chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def png_bytes(width: int, height: int, color_type: int, payload: bytes, filter_method: int = 0) -> bytes:
    header = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header) + png_chunk(b"IDAT", zlib.compress(payload)) + png_chunk(b"IEND", b"")


def png_case(name: str, content: bytes, expected: str) -> None:
    def call() -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.png"
            path.write_bytes(content)
            COMPARE.read_png(path)

    run_case("visual_truth_png", name, expected, call)


valid_png = png_bytes(2, 1, 2, bytes([0]) + bytes([0, 0, 0, 0, 0, 0]))
png_case("valid 2x1 RGB", valid_png, "accept")
png_case("empty file", b"", "reject")
png_case("bad signature", b"NOTPNG" + valid_png[6:], "reject")
png_case("truncated header", valid_png[:10], "reject")
png_case("zero dimensions", png_bytes(0, 1, 2, b""), "reject")
png_case("oversized dimensions", png_bytes(40000, 1, 2, b""), "reject")
png_case("duplicate IHDR", b"\x89PNG\r\n\x1a\n" + valid_png[8:29] + valid_png[8:], "reject")
png_case("trailing data", valid_png + b"junk", "reject")
png_case("nonempty IEND", valid_png[:-12] + png_chunk(b"IEND", b"x"), "reject")
png_case("bad row filter", png_bytes(1, 1, 2, bytes([5, 1, 2, 3])), "reject")
png_case("zlib size mismatch", png_bytes(2, 2, 2, bytes([0, 0, 0, 0, 0, 0])), "reject")
png_case("unsupported color type", png_bytes(1, 1, 0, bytes([0, 1])), "reject")
corrupt_crc = bytearray(valid_png)
corrupt_crc[20] ^= 0xFF
png_case("corrupt CRC", bytes(corrupt_crc), "reject")
png_case("compressed bomb", png_bytes(2000, 2000, 2, zlib.compress(b"\x00" * (2001 * 4000))[:64]), "reject")


# ---------------------------------------------------------------- allowlists
ALLOWED = list(CI_BUILD.TRUSTED_DOWNLOAD_URLS)
for url in ALLOWED:
    run_case("ci_build_allowlist", f"allowed {url[:48]}", "accept",
             lambda url=url: CI_BUILD.trusted_download_url(url), controlled=(ValueError, CI_BUILD.IntegrityError))


def expect_reject(url: str) -> None:
    run_case("ci_build_allowlist", url[:60], "reject",
             lambda: CI_BUILD.trusted_download_url(url), controlled=(ValueError, CI_BUILD.IntegrityError))


for url in [
    "",
    "http://github.com/godotengine/godot/releases/download/x/file.zip",
    "https://evil.example/godot.zip",
    "https://github.com.evil.example/godot.zip",
    "https://github.com@evil.example/godot.zip",
    "https://github.com:444/godot.zip",
    "https://GitHub.com/godotengine/godot/releases/download/x/file.zip",
    "https://github.com./godot.zip",
    "https://github.com%2eevil.example/godot.zip",
    "file:///etc/passwd",
    "https://github.com/godot.zip?next=https://evil.example",
    "https://github.com/godot.zip#fragment",
    ALLOWED[0] + " ",
    ALLOWED[0].replace("https://", "https://user:secret@"),
]:
    expect_reject(url)


def summarize() -> int:
    total = sum(bucket["cases"] for bucket in RESULTS.values())
    unexpected = sum(len(bucket["unexpected"]) for bucket in RESULTS.values())
    unexpected_accepts = sum(len(bucket["unexpected_accepts"]) for bucket in RESULTS.values())
    document = {
        "schema": "nex.qa.fuzz.v1",
        "generated_by": "NEX-QA-AUDIT-WO-001",
        "repo_root": str(REPO),
        "python": sys.version.split()[0],
        "targets": RESULTS,
        "totals": {
            "cases": total,
            "unexpected_exceptions": unexpected,
            "unexpected_accepts": unexpected_accepts,
        },
    }
    (REPORT_DIR / "FUZZ-RESULTS.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document["totals"], sort_keys=True))
    for target, bucket in sorted(RESULTS.items()):
        print(f"{target}: cases={bucket['cases']} unexpected={len(bucket['unexpected'])} unexpected_accepts={len(bucket['unexpected_accepts'])}")
    return 0 if unexpected == 0 and unexpected_accepts == 0 else 1


if __name__ == "__main__":
    raise SystemExit(summarize())

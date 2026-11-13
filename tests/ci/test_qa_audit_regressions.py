"""Regression tests from NEX-QA-AUDIT-WO-001 (Issue #20 robustness audit)."""
from __future__ import annotations

import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load(relative_path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, REPO / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GPU_VALIDATOR = _load("nex_bench/gpu_profile/validate_gpu_profile.py", "qa_reg_gpu_validator")
FRAMEPULSE = _load("nex_bench/telemetry/framepulse.py", "qa_reg_framepulse")
COMPARE = _load("nex_bench/visual_truth/compare.py", "qa_reg_compare")
CI_BUILD = _load("tooling/godot/ci_build.py", "qa_reg_ci_build")


def _png_chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def _png(width: int, height: int, rows: bytes, color_type: int = 2) -> bytes:
    header = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", header) + _png_chunk(b"IDAT", zlib.compress(rows)) + _png_chunk(b"IEND", b"")


class GPUValidatorRobustnessTests(unittest.TestCase):
    def test_malformed_json_is_rejected_with_profile_error(self) -> None:
        for payload in (b"", b"null", b"[]", b"{}", b'{"a":1,"a":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.subTest(payload=payload):
                with self.assertRaises(GPU_VALIDATOR.ProfileError):
                    GPU_VALIDATOR.validate_payload(payload)

    def test_deep_nesting_is_converted_to_profile_error(self) -> None:
        with self.assertRaises(GPU_VALIDATOR.ProfileError):
            GPU_VALIDATOR.validate_payload(b"[" * 10000)


class FramePulseRobustnessTests(unittest.TestCase):
    def test_malformed_json_is_rejected(self) -> None:
        for payload in ("", "null", "[]", "{}", '{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.subTest(payload=payload):
                with self.assertRaises(FRAMEPULSE.FramePulseError):
                    FRAMEPULSE.analyze_json(payload)

    def test_deep_nesting_is_not_silently_accepted(self) -> None:
        # QA-FINDING-001 (OPEN): current code propagates RecursionError instead of
        # FramePulseError. After the Correction WO, this must require FramePulseError only.
        with self.assertRaises((FRAMEPULSE.FramePulseError, RecursionError)):
            FRAMEPULSE.analyze_json("[" * 10000)


class PngParserRobustnessTests(unittest.TestCase):
    def test_minimal_rgb_png_roundtrips(self) -> None:
        content = _png(1, 1, bytes([0, 10, 20, 30]))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "valid.png"
            path.write_bytes(content)
            self.assertEqual((1, 1, bytes([10, 20, 30])), COMPARE.read_png(path))

    def test_malformed_png_is_rejected(self) -> None:
        valid = _png(1, 1, bytes([0, 1, 2, 3]))
        malformed = {
            "bad signature": b"NOTPNG" + valid[6:],
            "truncated": valid[:12],
            "trailing data": valid + b"junk",
            "zero dimensions": _png(0, 1, b""),
            "oversized dimensions": _png(40000, 1, b""),
            "bad row filter": _png(1, 1, bytes([5, 1, 2, 3])),
            "unsupported color type": _png(1, 1, bytes([0, 1]), color_type=0),
        }
        corrupted = bytearray(valid)
        corrupted[20] ^= 0xFF
        malformed["corrupt CRC"] = bytes(corrupted)
        for case, content in malformed.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "case.png"
                path.write_bytes(content)
                with self.assertRaises(COMPARE.ImageFormatError):
                    COMPARE.read_png(path)


class BuildAllowlistRobustnessTests(unittest.TestCase):
    def test_every_pinned_url_is_accepted(self) -> None:
        for url in CI_BUILD.TRUSTED_DOWNLOAD_URLS:
            with self.subTest(url=url):
                self.assertEqual(url, CI_BUILD.trusted_download_url(url))
                self.assertEqual(url.rsplit("/", 1)[-1], CI_BUILD.download_filename(url))

    def test_url_lookalikes_are_rejected(self) -> None:
        rejected = (
            "",
            "http://github.com/godotengine/godot/releases/download/x/file.zip",
            "https://evil.example/godot.zip",
            "https://github.com@evil.example/godot.zip",
            "https://github.com:444/godot.zip",
            "https://GitHub.com/godotengine/godot/releases/download/x/file.zip",
            "https://github.com./godot.zip",
            "https://github.com%2eevil.example/godot.zip",
            "file:///etc/passwd",
            "https://github.com/godot.zip?next=https://evil.example",
            "https://github.com/godot.zip#fragment",
            CI_BUILD.TRUSTED_DOWNLOAD_URLS[0] + " ",
        )
        for url in rejected:
            with self.subTest(url=url):
                with self.assertRaises(CI_BUILD.IntegrityError):
                    CI_BUILD.trusted_download_url(url)


if __name__ == "__main__":
    unittest.main()

"""NEX Visual Truth deterministic synthetic PNG regression tests (stdlib)."""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import zlib

from nex_bench.visual_truth.compare import ImageFormatError, compare_png, read_png

ROOT = Path(__file__).resolve().parents[2]


def _chunk(name: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + name + body + struct.pack(">I", zlib.crc32(name + body) & 0xffffffff)


def make_png(w: int, h: int, rgb: bytes, color_type: int = 2, filter_method: int = 0) -> bytes:
    bpp = 3 if color_type == 2 else 4
    stride = w * bpp
    assert len(rgb) == h * stride
    payload = bytearray()
    for i in range(h):
        row = rgb[i * stride:(i + 1) * stride]
        payload.append(filter_method)
        if filter_method == 0:
            payload.extend(row)
        elif filter_method == 1:
            payload.extend((c - (row[j - bpp] if j >= bpp else 0)) & 255 for j, c in enumerate(row))
        else:
            raise ValueError("Synthetic helper supports filters 0 and 1")
    header = struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(payload)) + _chunk(b"IEND", b"")


class VisualTruthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def png(self, name, data):
        path = self.dir / name
        path.write_bytes(data)
        return path

    def test_identical_rgb_screenshots_pass(self):
        baseline = self.png("a.png", make_png(2, 1, bytes([2, 3, 5, 10, 11, 13])))
        candidate = self.png("b.png", baseline.read_bytes())
        report = compare_png(baseline, candidate)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["changed_pixels"], 0)
        self.assertEqual(report["mean_absolute_error_normalized"], 0)

    def test_detects_pixel_change_and_cli_failure(self):
        baseline = self.png("a.png", make_png(2, 1, bytes([0, 0, 0, 0, 0, 0])))
        candidate = self.png("b.png", make_png(2, 1, bytes([0, 0, 0, 255, 0, 0])))
        self.assertEqual(compare_png(baseline, candidate)["changed_ratio"], 0.5)
        cmd = [sys.executable, str(ROOT / "nex_bench/visual_truth/compare.py"), str(baseline), str(candidate)]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('"status": "FAIL"', result.stdout)

    def test_tolerance_allows_small_differences(self):
        first = self.png("a.png", make_png(1, 1, bytes([20, 20, 20])))
        second = self.png("b.png", make_png(1, 1, bytes([22, 20, 20])))
        self.assertEqual(compare_png(first, second, pixel_tolerance=2)["status"], "PASS")
        self.assertEqual(compare_png(first, second, pixel_tolerance=1)["status"], "FAIL")

    def test_sub_png_filter_roundtrips(self):
        payload = bytes([1, 30, 90, 200, 220, 90])
        path = self.png("sub.png", make_png(2, 1, payload, filter_method=1))
        self.assertEqual(read_png(path), (2, 1, payload))

    def test_rgba_transparent_composite_to_black(self):
        path = self.png("rgba.png", make_png(1, 1, bytes([250, 60, 30, 0]), color_type=6))
        self.assertEqual(read_png(path)[2], bytes([0, 0, 0]))

    def test_crc_tamper_fails_closed(self):
        good = bytearray(make_png(1, 1, bytes([3, 6, 9])))
        good[20] ^= 1
        with self.assertRaises(ImageFormatError):
            read_png(self.png("bad.png", bytes(good)))

    def test_size_mismatch_fails_closed(self):
        one = self.png("one.png", make_png(1, 1, bytes([0, 0, 0])))
        two = self.png("two.png", make_png(2, 1, bytes([0, 0, 0, 0, 0, 0])))
        with self.assertRaises(ImageFormatError):
            compare_png(one, two)

    def test_non_png_is_rejected(self):
        with self.assertRaises(ImageFormatError):
            read_png(self.png("bad.png", b"not a PNG"))

    def test_invalid_thresholds_rejected(self):
        one = self.png("one.png", make_png(1, 1, bytes([0, 0, 0])))
        with self.assertRaises(ValueError):
            compare_png(one, one, pixel_tolerance=-1)
        with self.assertRaises(ValueError):
            compare_png(one, one, max_changed_ratio=1.01)


if __name__ == "__main__":
    unittest.main()

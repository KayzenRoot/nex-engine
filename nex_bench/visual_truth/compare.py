"""NEX Visual Truth: deterministic, dependency-free RGB/RGBA PNG regression checks.

Not a GPU screenshot generator. Does not assert visual quality or real FPS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
import zlib

PNG_SIG = b"\x89PNG\r\n\x1a\n"
MAX_DIMENSION = 4096
MAX_COMPRESSED = 32 * 1024 * 1024
MAX_FILE_BYTES = 40 * 1024 * 1024


class ImageFormatError(ValueError):
    pass


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    d = (abs(p - a), abs(p - b), abs(p - c))
    return (a, b, c)[d.index(min(d))]


def read_png(path: Path) -> tuple[int, int, bytes]:
    """Read noninterlaced 8-bit RGB/RGBA PNG into normalized RGB bytes."""
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ImageFormatError("PNG file too large")
    content = path.read_bytes()
    if not content.startswith(PNG_SIG):
        raise ImageFormatError("Not a PNG file")
    pos = 8
    width = height = color_type = bpp = None
    compressed = bytearray()
    seen_ihdr = seen_iend = False
    while pos < len(content):
        if len(content) - pos < 12:
            raise ImageFormatError("Truncated chunk header")
        length = int.from_bytes(content[pos:pos + 4], "big")
        kind = content[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(content):
            raise ImageFormatError("Truncated PNG chunk")
        body = content[pos + 8:pos + 8 + length]
        expected_crc = int.from_bytes(content[pos + 8 + length:end], "big")
        if zlib.crc32(kind + body) & 0xffffffff != expected_crc:
            raise ImageFormatError("PNG CRC mismatch")
        if not seen_ihdr and kind != b"IHDR":
            raise ImageFormatError("IHDR must be first")
        if kind == b"IHDR":
            if seen_ihdr or length != 13:
                raise ImageFormatError("Duplicate or malformed IHDR")
            width, height, depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            if not (0 < width <= MAX_DIMENSION and 0 < height <= MAX_DIMENSION):
                raise ImageFormatError("Unsupported image dimensions")
            if depth != 8 or color_type not in (2, 6) or compression or filtering or interlace:
                raise ImageFormatError("Only 8-bit noninterlaced RGB/RGBA PNG is supported")
            bpp = 3 if color_type == 2 else 4
            seen_ihdr = True
        elif kind == b"IDAT":
            if seen_iend:
                raise ImageFormatError("IDAT after IEND")
            compressed.extend(body)
            if len(compressed) > MAX_COMPRESSED:
                raise ImageFormatError("Compressed PNG too large")
        elif kind == b"IEND":
            if length:
                raise ImageFormatError("IEND must be empty")
            seen_iend = True
            if end != len(content):
                raise ImageFormatError("Trailing PNG data")
            break
        elif kind[:1].isupper():
            raise ImageFormatError("Unsupported critical PNG chunk")
        pos = end
    if not seen_ihdr or not seen_iend or not compressed:
        raise ImageFormatError("Incomplete PNG")
    assert width is not None and height is not None and bpp is not None
    stride = width * bpp
    expected = height * (1 + stride)
    try:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(bytes(compressed), expected + 1)
        raw += decoder.flush(expected + 1 - len(raw))
    except (zlib.error, ValueError) as exc:
        raise ImageFormatError("Invalid PNG compressed data") from exc
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or len(raw) != expected:
        raise ImageFormatError("PNG size or zlib stream mismatch")
    output = bytearray()
    previous = bytearray(stride)
    for row_num in range(height):
        offset = row_num * (stride + 1)
        method = raw[offset]
        if method not in (0, 1, 2, 3, 4):
            raise ImageFormatError("Invalid PNG row filter")
        encoded = raw[offset + 1:offset + 1 + stride]
        decoded = bytearray(stride)
        for i, value in enumerate(encoded):
            left = decoded[i - bpp] if i >= bpp else 0
            top = previous[i]
            upper_left = previous[i - bpp] if i >= bpp else 0
            prediction = (0, left, top, (left + top) // 2, _paeth(left, top, upper_left))[method]
            decoded[i] = (value + prediction) & 0xff
        if bpp == 3:
            output.extend(decoded)
        else:
            for i in range(0, len(decoded), 4):
                alpha = decoded[i + 3]
                output.extend((decoded[i + k] * alpha + 127) // 255 for k in range(3))
        previous = decoded
    return width, height, bytes(output)


def compare_png(baseline: Path, candidate: Path, pixel_tolerance: int = 0,
                max_changed_ratio: float = 0.0) -> dict[str, object]:
    if not 0 <= pixel_tolerance <= 255 or not 0 <= max_changed_ratio <= 1:
        raise ValueError("pixel_tolerance must be 0..255 and max_changed_ratio 0..1")
    w1, h1, first = read_png(baseline)
    w2, h2, second = read_png(candidate)
    if (w1, h1) != (w2, h2):
        raise ImageFormatError("Capture dimensions do not match")
    count = w1 * h1
    changed = 0
    sum_error = 0
    worst = 0
    for i in range(0, len(first), 3):
        diffs = [abs(first[i + k] - second[i + k]) for k in range(3)]
        sum_error += sum(diffs)
        worst = max(worst, *diffs)
        if max(diffs) > pixel_tolerance:
            changed += 1
    ratio = changed / count
    return {
        "schema_version": "visual_truth.v1",
        "width_px": w1, "height_px": h1, "pixels": count,
        "changed_pixels": changed, "changed_ratio": ratio,
        "mean_absolute_error_normalized": sum_error / (count * 3 * 255),
        "max_channel_error_normalized": worst / 255,
        "pixel_tolerance": pixel_tolerance, "max_changed_ratio": max_changed_ratio,
        "status": "PASS" if ratio <= max_changed_ratio else "FAIL",
        "measurement": "PIXEL_DIFF_ONLY_NOT_PERCEPTUAL_OR_GPU_BENCHMARK",
    }


def _safe_cli_png(value: Path) -> Path:
    """Limit CLI input to PNG files within the invocation directory (no traversal)."""
    root = Path.cwd().resolve()
    if value.is_absolute() or ".." in value.parts or value.suffix.lower() != ".png":
        raise ImageFormatError("PNG input must be a relative .png under the working directory")
    resolved = (root / value).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ImageFormatError("PNG input escapes workspace or is not a regular file")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEX Visual Truth PNG comparison")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--pixel-tolerance", type=int, default=0)
    parser.add_argument("--max-changed-ratio", type=float, default=0.0)
    args = parser.parse_args(argv)
    try:
        report = compare_png(_safe_cli_png(args.baseline), _safe_cli_png(args.candidate),
                             args.pixel_tolerance, args.max_changed_ratio)
    except (ImageFormatError, ValueError, OSError) as exc:
        print(f"VISUAL_TRUTH_ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

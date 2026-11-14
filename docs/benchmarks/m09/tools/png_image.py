"""Minimal deterministic PNG reader and pixel comparator for NEX visual evidence.

Supports 8-bit non-interlaced grayscale, RGB, grayscale+alpha and RGBA PNGs,
which covers Godot's viewport captures. It performs no color management and no
resampling: the comparison is exact byte-level pixel data.
"""
from __future__ import annotations

import hashlib
import math
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS_BY_COLOR_TYPE = {0: 1, 2: 3, 4: 2, 6: 4}
ALLOWED_AUXILIARY_CHUNKS = {
    b"PLTE", b"tRNS", b"gAMA", b"sRGB", b"pHYs", b"iCCP",
    b"tEXt", b"zTXt", b"iTXt", b"bKGD", b"cHRM", b"tIME",
}


class PngError(ValueError):
    """Raised when a PNG is malformed or uses an unsupported layout."""


@dataclass(frozen=True)
class PngImage:
    width: int
    height: int
    channels: int
    pixels: bytes

    def __post_init__(self) -> None:
        expected = self.width * self.height * self.channels
        if self.width <= 0 or self.height <= 0:
            raise PngError("PNG dimensions must be positive")
        if len(self.pixels) != expected:
            raise PngError("PNG pixel buffer length does not match dimensions")


def _paeth(left: int, up: int, up_left: int) -> int:
    estimate = left + up - up_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_up_left = abs(estimate - up_left)
    if distance_left <= distance_up and distance_left <= distance_up_left:
        return left
    if distance_up <= distance_up_left:
        return up
    return up_left


def _unfilter(raw: bytes, width: int, height: int, channels: int) -> bytes:
    stride = width * channels
    if len(raw) != height * (stride + 1):
        raise PngError("PNG scanline data has an unexpected length")
    output = bytearray(height * stride)
    position = 0
    for row_index in range(height):
        filter_type = raw[position]
        position += 1
        row = bytearray(raw[position:position + stride])
        position += stride
        previous = output[(row_index - 1) * stride:row_index * stride] if row_index else b"\x00" * stride
        for index in range(stride):
            left = row[index - channels] if index >= channels else 0
            up = previous[index]
            up_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                continue
            if filter_type == 1:
                row[index] = (row[index] + left) & 0xFF
            elif filter_type == 2:
                row[index] = (row[index] + up) & 0xFF
            elif filter_type == 3:
                row[index] = (row[index] + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                row[index] = (row[index] + _paeth(left, up, up_left)) & 0xFF
            else:
                raise PngError("unsupported PNG filter type")
        output[row_index * stride:(row_index + 1) * stride] = row
    return bytes(output)


def read_png(path: Path) -> PngImage:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise PngError("missing PNG signature")
    offset = len(PNG_SIGNATURE)
    width = height = channels = None
    compressed = bytearray()
    seen_iend = False
    while offset < len(data):
        if offset + 8 > len(data):
            raise PngError("truncated PNG chunk header")
        length, kind = struct.unpack(">I4s", data[offset:offset + 8])
        offset += 8
        if offset + length + 4 > len(data):
            raise PngError("truncated PNG chunk payload")
        payload = data[offset:offset + length]
        offset += length
        expected_crc = struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            raise PngError("PNG chunk CRC mismatch")
        if kind == b"IHDR":
            if width is not None:
                raise PngError("duplicate PNG IHDR")
            if length != 13:
                raise PngError("invalid PNG IHDR length")
            width, height, depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if depth != 8 or color_type not in CHANNELS_BY_COLOR_TYPE:
                raise PngError("unsupported PNG bit depth or color type")
            if compression != 0 or filtering != 0 or interlace != 0:
                raise PngError("unsupported PNG compression, filtering or interlace")
            channels = CHANNELS_BY_COLOR_TYPE[color_type]
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            seen_iend = True
            break
        elif kind not in ALLOWED_AUXILIARY_CHUNKS:
            raise PngError("unsupported PNG chunk: " + kind.decode("latin-1"))
    if width is None or height is None or channels is None:
        raise PngError("PNG is missing IHDR")
    if not seen_iend:
        raise PngError("PNG is missing IEND")
    if not compressed:
        raise PngError("PNG is missing IDAT")
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise PngError("invalid PNG zlib stream") from exc
    return PngImage(width, height, channels, _unfilter(raw, width, height, channels))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(first: PngImage, second: PngImage, threshold: int = 2) -> dict[str, float | int | None]:
    if (first.width, first.height, first.channels) != (second.width, second.height, second.channels):
        raise PngError("images have different dimensions or channel layouts")
    total_abs = 0
    total_squared = 0
    max_abs = 0
    changed_pixels = 0
    stride = first.channels
    for pixel in range(0, len(first.pixels), stride):
        pixel_max = 0
        for channel in range(stride):
            difference = abs(first.pixels[pixel + channel] - second.pixels[pixel + channel])
            total_abs += difference
            total_squared += difference * difference
            if difference > pixel_max:
                pixel_max = difference
        if pixel_max > max_abs:
            max_abs = pixel_max
        if pixel_max > threshold:
            changed_pixels += 1
    pixels = first.width * first.height
    mean_abs = total_abs / (pixels * stride)
    mse = total_squared / (pixels * stride)
    psnr = None if mse == 0.0 else round(10.0 * math.log10((255.0 * 255.0) / mse), 3)
    return {
        "mean_abs_diff": round(mean_abs, 4),
        "max_abs_diff": max_abs,
        "changed_pixels": changed_pixels,
        "changed_pixels_pct": round(changed_pixels / pixels * 100.0, 3),
        "psnr_db": psnr,
    }

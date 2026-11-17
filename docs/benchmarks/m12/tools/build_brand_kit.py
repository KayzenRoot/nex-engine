#!/usr/bin/env python3
"""Build the NEX M12 brand kit: identity document, ICO/ICNS and report."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parents[1] / "tools"))
from runtime_report import render_json  # noqa: E402 - shared tool module

REPO = Path(__file__).resolve().parents[4]
BRAND = REPO / "assets" / "brand"
ICONS = BRAND / "icons"
APP_ICONS = BRAND / "app-icons"
OUTPUT = REPO / "docs" / "benchmarks" / "m12"
REPORT_JSON = OUTPUT / "brand-kit.v1.json"
REPORT_MD = OUTPUT / "BRAND-KIT.md"
IDENTITY = BRAND / "identity.v1.json"
ICO = APP_ICONS / "nex-engine.ico"
ICNS = APP_ICONS / "nex-engine.icns"
SUMS = BRAND / "SHA256SUMS.txt"
SOURCE_SHA = "c2c13c57b4de7a5114db2e2b79d37a7e026bfa62"
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)
ICNS_TYPES = {16: b"icp4", 32: b"icp5", 64: b"icp6", 128: b"ic07",
              256: b"ic08", 512: b"ic09", 1024: b"ic10"}
FORBIDDEN = {"script", "foreignObject", "image", "iframe", "object", "embed", "style"}
HEX = re.compile(r"^#[0-9a-f]{6}$")
BINARIES: dict[str, bytes] = {}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _svg(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def _validate_svg(path: Path, require_outlines: bool = False) -> None:
    root = _svg(path)
    if _local(root.tag) != "svg" or "viewBox" not in root.attrib:
        raise ValueError(f"{path.name} is not a valid SVG")
    for element in root.iter():
        if _local(element.tag) in FORBIDDEN:
            raise ValueError(f"{path.name} contains forbidden element {_local(element.tag)}")
        for key, value in element.attrib.items():
            attribute = _local(key).lower()
            if attribute.startswith("on"):
                raise ValueError(f"{path.name} contains an event handler")
            if attribute == "href" and (value.startswith("data:") or "://" in value):
                raise ValueError(f"{path.name} contains an external reference")
    if require_outlines:
        texts = [element for element in root.iter() if _local(element.tag) == "text"]
        if texts:
            raise ValueError(f"{path.name} must use outlined paths, not text")


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} is not a PNG")
    return struct.unpack(">II", data[16:24])


def _lum(hex_value: str) -> float:
    value = hex_value.lstrip("#")
    channels = [int(value[index:index + 2], 16) / 255.0 for index in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_lum(first), _lum(second)), reverse=True)
    return round((high + 0.05) / (low + 0.05), 2)


def _sums_bytes() -> bytes:
    lines = []
    for path in sorted(BRAND.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        lines.append(f"{_sha(path)} *{path.relative_to(BRAND).as_posix()}")
    separator = chr(10)
    return (separator.join(lines) + separator).encode("utf-8")


def _ico(images: dict[int, bytes]) -> bytes:
    header = struct.pack("<HHH", 0, 1, len(images))
    entries = b""
    payload = b""
    offset = 6 + 16 * len(images)
    for size in SIZES:
        png = images[size]
        dimension = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dimension, dimension, 0, 0, 1, 32, len(png), offset)
        payload += png
        offset += len(png)
    return header + entries + payload


def _icns(images: dict[int, bytes]) -> bytes:
    body = b""
    for size in (16, 32, 64, 128, 256, 512, 1024):
        png = images[size]
        body += ICNS_TYPES[size] + struct.pack(">I", 8 + len(png)) + png
    return b"icns" + struct.pack(">I", 8 + len(body)) + body


def _identity(palette: dict, logo_hashes: dict) -> dict[str, Any]:
    return {
        "schema_version": "identity.v1",
        "observation_id": "nex-brand-system-2026-11-17",
        "captured_at_utc": "2026-11-17T00:00:00Z",
        "palette": [{"token": item["id"], "hex": item["hex"], "role": item["role"]}
                    for item in palette["colors"]],
        "typography": {
            "font_family": "Segoe UI / system UI",
            "display_size_px": 48,
            "body_size_px": 16,
            "line_height_ratio": 1.5,
            "weights": [400, 600, 700],
        },
        "logo": {
            "mark_svg_uri": "assets/brand/logo-mark.svg",
            "mark_sha256": logo_hashes["mark"],
            "mark_view_box": [0, 0, 128, 128],
            "wordmark_svg_uri": "assets/brand/wordmark.svg",
            "wordmark_sha256": logo_hashes["wordmark"],
            "wordmark_view_box": [0, 0, 190, 100],
            "monochrome_sha256": logo_hashes["monochrome"],
            "clear_space_ratio": 0.25,
        },
        "spacing": {"base_px": 4, "scale": [4, 8, 12, 16, 24, 32, 48, 64],
                    "max_content_width_px": 1280},
        "accessibility": {"min_text_contrast_ratio": 7.0,
                          "min_large_text_contrast_ratio": 3.0,
                          "requires_focus_indicator": True, "min_focus_ring_px": 2},
        "provenance": {
            "base_sha": SOURCE_SHA,
            "head_sha": SOURCE_SHA,
            "godot_version": "4.7.2-stable",
            "hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "NVIDIA 617.14"},
            "capture_mode": "headless",
            "measurement_status": "MEASURED",
            "evidence_uri": "docs/benchmarks/m12/brand-kit.v1.json",
        },
    }


def build_report() -> dict[str, Any]:
    palette = json.loads((BRAND / "palette.v1.json").read_text(encoding="utf-8"))
    if palette.get("schema_version") != "nex_brand_palette.v1":
        raise ValueError("palette schema is invalid")
    colors = palette["colors"]
    if len(colors) != 5 or len({item["id"] for item in colors}) != 5:
        raise ValueError("palette must contain five unique tokens")
    for item in colors:
        if not HEX.match(item["hex"]):
            raise ValueError("palette hex is invalid")
    for name in ("logo-mark.svg", "logo-monochrome.svg"):
        _validate_svg(BRAND / name)
    for name in ("logo-primary.svg", "wordmark.svg"):
        _validate_svg(BRAND / name, require_outlines=True)
    icons = sorted(ICONS.glob("*.svg"))
    if len(icons) != 10:
        raise ValueError("brand icon set must contain 10 icons")
    for path in icons:
        root = _svg(path)
        if root.attrib.get("viewBox") != "0 0 24 24" or root.attrib.get("stroke") != "currentColor":
            raise ValueError(f"{path.name} does not follow the icon contract")
    images: dict[int, bytes] = {}
    for size in SIZES:
        path = APP_ICONS / f"nex-engine-{size}.png"
        if not path.is_file():
            raise ValueError(f"missing app icon {path.name}")
        if _png_size(path) != (size, size):
            raise ValueError(f"{path.name} has the wrong dimensions")
        images[size] = path.read_bytes()
    ico = _ico(images)
    icns = _icns(images)
    logo_hashes = {
        "mark": _sha(BRAND / "logo-mark.svg"),
        "wordmark": _sha(BRAND / "wordmark.svg"),
        "monochrome": _sha(BRAND / "logo-monochrome.svg"),
        "primary": _sha(BRAND / "logo-primary.svg"),
    }
    contrasts = {
        "mist_on_graphite": _contrast("#E8EEF7", "#0B0F14"),
        "cobalt_on_graphite": _contrast("#2F6BFF", "#0B0F14"),
        "cyan_on_graphite": _contrast("#35D0FF", "#0B0F14"),
        "amber_on_graphite": _contrast("#FFB020", "#0B0F14"),
        "graphite_on_mist": _contrast("#0B0F14", "#E8EEF7"),
    }
    if contrasts["mist_on_graphite"] < 7.0 or contrasts["cobalt_on_graphite"] < 3.0:
        raise ValueError("brand contrast does not meet the thresholds")
    identity = _identity(palette, logo_hashes)
    BINARIES["ico"] = ico
    BINARIES["icns"] = icns
    return {
        "schema_version": "m12_brand_kit.v1",
        "source_sha": SOURCE_SHA,
        "session_date": "2026-11-17",
        "palette": colors,
        "logo": logo_hashes,
        "icons": {"ui_icons": len(icons), "app_icon_sizes": list(SIZES),
                  "ico_bytes": len(ico), "icns_bytes": len(icns)},
        "contrast": contrasts,
        "identity": identity,
        "verdict": "BRAND_SYSTEM_READY_FOR_UI",
        "observations": [
            "the primary logo now uses an outlined NEX ENGINE wordmark with no font dependency",
            "9 app-icon PNG sizes are rendered from the original mark SVG",
            "ICO and ICNS containers are generated from the PNG sizes",
            "10 monochrome 24x24 UI icons follow the currentColor contract",
            "Mist on Graphite is 16.48:1 and Cobalt on Graphite is 4.27:1",
            "identity.v1 carries palette, logo hashes, spacing and accessibility thresholds",
        ],
        "limitations": [
            "no editor UI, launcher, installer or engine binary is modified",
            "distribution and trademark clearance remain Owner decisions",
            "the wordmark is an original geometric design, not a licensed typeface",
            "no screenshot, runtime or quality claim",
            "no third-party marks or assets are incorporated",
        ],
        "runs": 1,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NEX M12 · Brand kit",
        "",
        "**Status:** `BRAND_SYSTEM_READY_FOR_UI / DISTRIBUTION_TRADEMARK_PENDING / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **Engine:** Godot 4.7.2-stable",
        "",
        "## Logo",
        "",
        "| Asset | SHA-256 |",
        "|---|---|",
    ]
    for name, digest in report["logo"].items():
        lines.append(f"| {name} | `{digest}` |")
    lines.extend([
        "",
        "## Palette e contraste",
        "",
        "| Token | Hex | Role |",
        "|---|---|---|",
    ])
    for color in report["palette"]:
        lines.append(f"| {color['id']} | `{color['hex']}` | {color['role']} |")
    lines.extend(["", "| Par | Contraste |", "|---|---:|"])
    for name, ratio in report["contrast"].items():
        lines.append(f"| {name} | {ratio:.2f}:1 |")
    lines.extend([
        "",
        "## Ícones",
        "",
        f"- UI: **{report['icons']['ui_icons']}** ícones 24×24 com `currentColor`.",
        f"- App: **{len(report['icons']['app_icon_sizes'])}** PNGs; "
        f"ICO **{report['icons']['ico_bytes']} bytes**; ICNS **{report['icons']['icns_bytes']} bytes**.",
        "",
        "## Identidade",
        "",
        f"- `identity.v1`: texto ≥ **{report['identity']['accessibility']['min_text_contrast_ratio']}**:1, "
        f"large ≥ **{report['identity']['accessibility']['min_large_text_contrast_ratio']}**:1, "
        f"focus ring **{report['identity']['accessibility']['min_focus_ring_px']} px**.",
        f"- Wordmark: **outlined paths**, sem `<text>` ou dependência de fonte.",
        "",
        "## Observações",
        "",
    ])
    lines.extend(f"- {item}" for item in report["observations"])
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `docs/benchmarks/m12/tools/build_brand_kit.py`; não é aprovação de marca.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    report = build_report()
    rendered_json = render_json(report)
    rendered_md = render_markdown(report)
    identity_bytes = (json.dumps(report["identity"], indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if argv == ["--check"]:
        if not REPORT_JSON.is_file() or REPORT_JSON.read_text(encoding="utf-8") != rendered_json:
            print("M12_BRAND_KIT_CHECK_FAIL: JSON is stale")
            return 1
        if not REPORT_MD.is_file() or REPORT_MD.read_text(encoding="utf-8") != rendered_md:
            print("M12_BRAND_KIT_CHECK_FAIL: Markdown is stale")
            return 1
        if not IDENTITY.is_file() or IDENTITY.read_bytes() != identity_bytes:
            print("M12_BRAND_KIT_CHECK_FAIL: identity is stale")
            return 1
        if not ICO.is_file() or ICO.read_bytes() != BINARIES["ico"]:
            print("M12_BRAND_KIT_CHECK_FAIL: ICO is stale")
            return 1
        if not ICNS.is_file() or ICNS.read_bytes() != BINARIES["icns"]:
            print("M12_BRAND_KIT_CHECK_FAIL: ICNS is stale")
            return 1
        if not SUMS.is_file() or SUMS.read_bytes() != _sums_bytes():
            print("M12_BRAND_KIT_CHECK_FAIL: SHA256SUMS is stale")
            return 1
        print("M12_BRAND_KIT_CHECK_PASS: 9 sizes / 10 icons")
        return 0
    if argv:
        print("usage: builder [--check]")
        return 2
    OUTPUT.mkdir(parents=True, exist_ok=True)
    APP_ICONS.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(rendered_json, encoding="utf-8", newline="\n")
    REPORT_MD.write_text(rendered_md, encoding="utf-8", newline="\n")
    IDENTITY.write_bytes(identity_bytes)
    ICO.write_bytes(BINARIES["ico"])
    ICNS.write_bytes(BINARIES["icns"])
    SUMS.write_bytes(_sums_bytes())
    print("M12_BRAND_KIT_WRITE_PASS: 9 sizes / 10 icons")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

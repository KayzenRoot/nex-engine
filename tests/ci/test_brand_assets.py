"""Structural acceptance tests for the NEX M12-S01 brand master assets."""
from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRAND = REPO / "assets" / "brand"
ICONS = BRAND / "icons"
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
FORBIDDEN_TAGS = {"script", "foreignObject", "image", "iframe", "object", "embed", "style"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_svg(path: Path):
    return ET.parse(path).getroot()


def iter_elements(root):
    return root.iter()


class BrandSvgTests(unittest.TestCase):
    def test_all_svgs_parse_as_svg(self) -> None:
        files = sorted(BRAND.rglob("*.svg"))
        self.assertGreaterEqual(len(files), 13)
        for path in files:
            with self.subTest(path=path.name):
                root = parse_svg(path)
                self.assertEqual("svg", local_name(root.tag))
                self.assertIn("viewBox", root.attrib)

    def test_no_active_or_external_content(self) -> None:
        for path in sorted(BRAND.rglob("*.svg")):
            root = parse_svg(path)
            for element in iter_elements(root):
                with self.subTest(path=path.name, tag=local_name(element.tag)):
                    self.assertNotIn(local_name(element.tag), FORBIDDEN_TAGS)
                    for key, value in element.attrib.items():
                        attribute = local_name(key)
                        self.assertFalse(attribute.lower().startswith("on"), f"event handler in {path.name}")
                        if attribute == "href":
                            self.assertFalse(SCHEME.match(value), f"external reference in {path.name}")
                            self.assertFalse(value.startswith("data:"), f"embedded data in {path.name}")

    def test_icons_follow_the_contract(self) -> None:
        icons = sorted(ICONS.glob("*.svg"))
        self.assertEqual(10, len(icons))
        for path in icons:
            with self.subTest(path=path.name):
                root = parse_svg(path)
                self.assertEqual("0 0 24 24", root.attrib.get("viewBox"))
                self.assertEqual("currentColor", root.attrib.get("stroke"))
                self.assertTrue(root.attrib.get("aria-label"))
                self.assertFalse([e for e in root.iter() if local_name(e.tag) == "text"])

    def test_primary_logo_marks_the_wordmark_as_provisional(self) -> None:
        primary = parse_svg(BRAND / "logo-primary.svg")
        text_nodes = [element for element in primary.iter() if local_name(element.tag) == "text"]
        self.assertGreaterEqual(len(text_nodes), 2)
        for node in text_nodes:
            self.assertIn("font-family", node.attrib)
        guidelines = (BRAND / "BRAND-GUIDELINES.md").read_text(encoding="utf-8").lower()
        self.assertIn("provisional", guidelines)

    def test_monochrome_mark_uses_current_color(self) -> None:
        root = parse_svg(BRAND / "logo-monochrome.svg")
        fills = {element.attrib.get("fill") for element in root.iter() if "fill" in element.attrib}
        self.assertIn("currentColor", fills)


class BrandPaletteTests(unittest.TestCase):
    def test_palette_tokens_are_unique_and_well_formed(self) -> None:
        palette = json.loads((BRAND / "palette.v1.json").read_text(encoding="utf-8"))
        self.assertEqual("nex_brand_palette.v1", palette["schema_version"])
        colors = palette["colors"]
        self.assertEqual(5, len(colors))
        self.assertEqual(len(colors), len({color["id"] for color in colors}))
        self.assertEqual(len(colors), len({color["hex"].upper() for color in colors}))
        for color in colors:
            with self.subTest(color=color["id"]):
                self.assertRegex(color["hex"], HEX_COLOR)
                self.assertTrue(color["role"])


class BrandDocumentationTests(unittest.TestCase):
    def test_originality_statement_is_present(self) -> None:
        text = (BRAND / "BRAND-GUIDELINES.md").read_text(encoding="utf-8").lower()
        self.assertIn("not derived from the godot logo", text)
        master = (REPO / "docs" / "brand" / "BRAND-MASTER.md").read_text(encoding="utf-8").lower()
        self.assertIn("not_integrated", master)
        self.assertIn("pending owner decisions", master)


if __name__ == "__main__":
    unittest.main()

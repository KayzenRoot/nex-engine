#!/usr/bin/env python3
"""Build and verify the Windows reference export of the unified NEX visual lab.

The build is deliberately staged: the repository keeps standalone lab
project.godot files inside nex_bench/scenes/base and nex_bench/stress. Those
nested projects hide their files from the parent export, so the build copies
nex_bench to build/stage, removes the nested project markers and the standalone
entry points that are not part of the unified lab, then exports from the stage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "nex_bench"
PRESET = PROJECT / "export_presets.cfg"
ICON = PROJECT / "icon.ico"
BRAND_ICON = REPO / "assets" / "brand" / "app-icons" / "nex-engine.ico"
BUILD_DIR = REPO / "build"
STAGE = BUILD_DIR / "stage"
EXE = BUILD_DIR / "NEXEngine.exe"
EVIDENCE_DIR = REPO / "docs" / "benchmarks" / "build"
EVIDENCE_JSON = EVIDENCE_DIR / "reference-build.v1.json"
EVIDENCE_MD = EVIDENCE_DIR / "REFERENCE-BUILD.md"
CAPTURE_DIR = EVIDENCE_DIR / "evidence"
CAPTURE_SCRIPT = REPO / "scripts" / "capture-reference-gui.ps1"
GODOT_VERSION = "4.7.2.stable"
GODOT_COMMIT = "ed1daf0bf001b61586d9930840f2f1394092c079"
GODOT_CANDIDATES = (
    Path(r"C:\tools\Godot_v4.7.2-stable_win64_console.exe"),
    Path(r"C:\tools\Godot_v4.7.2-stable_win64.exe"),
)
NESTED_PROJECTS = ("scenes/base/project.godot", "stress/project.godot")
STANDALONE_ENTRY_POINTS = (
    "scenes/base/viewer.tscn",
    "scenes/base/viewer.gd",
    "stress/main.tscn",
)
CAPTURES = (
    "nex-mode-corridor.png",
    "nex-mode-arena.png",
    "nex-mode-dense-city.png",
    "nex-mode-density.png",
    "nex-mode-diagnostics.png",
)
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def _source_sha() -> str:
    return _git("rev-parse", "HEAD")


def _resolve_godot() -> Path:
    for candidate in GODOT_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise SystemExit(
        "REFERENCE_BUILD_BLOCKED: pinned Godot 4.7.2 console binary is missing; "
        r"expected C:\tools\Godot_v4.7.2-stable_win64_console.exe"
    )


def _godot_version(godot: Path) -> str:
    result = subprocess.run([str(godot), "--version"], capture_output=True, text=True, timeout=60)
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0 or GODOT_VERSION not in output or GODOT_COMMIT[:9] not in output:
        raise SystemExit(f"REFERENCE_BUILD_BLOCKED: unexpected Godot version: {output!r}")
    return output


def _templates_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise SystemExit("REFERENCE_BUILD_BLOCKED: APPDATA is required on Windows")
    path = Path(appdata) / "Godot" / "export_templates" / GODOT_VERSION
    release = path / "windows_release_x86_64.exe"
    if not (path / "version.txt").is_file() or not release.is_file():
        raise SystemExit(
            "REFERENCE_BUILD_BLOCKED: install the official Windows x86_64 templates in "
            f"{path} (version.txt and windows_release_x86_64.exe)"
        )
    return path


def _stage_project() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    shutil.copytree(PROJECT, STAGE, ignore=shutil.ignore_patterns(".godot", "build", "__pycache__"))
    removed: list[str] = []
    for relative in (*NESTED_PROJECTS, *STANDALONE_ENTRY_POINTS):
        path = STAGE / relative
        if path.is_file():
            path.unlink()
            removed.append(relative)
    for scene in ("scenes/base/corridor_static.tscn", "scenes/base/arena_combat.tscn",
                  "scenes/base/dense_city.tscn"):
        if not (STAGE / scene).is_file():
            raise SystemExit(f"REFERENCE_BUILD_BLOCKED: staged scene missing: {scene}")
    print("REFERENCE_BUILD_STAGE_OK: removed " + ", ".join(removed))


def _run_checked(command: list[str], timeout: int = 300) -> str:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    output = ANSI.sub("", result.stdout + result.stderr)
    if result.returncode != 0:
        raise SystemExit(f"REFERENCE_BUILD_BLOCKED: command failed ({result.returncode}): {' '.join(command)}\n{output[-4000:]}")
    return output


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"REFERENCE_BUILD_BLOCKED: not a PNG: {path.name}")
    return struct.unpack(">II", data[16:24])


def _capture_gui() -> list[dict[str, Any]]:
    if os.name != "nt":
        raise SystemExit("REFERENCE_BUILD_BLOCKED: GUI capture is Windows-only")
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    output = _run_checked(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(CAPTURE_SCRIPT), "-Exe", str(EXE), "-Output", str(CAPTURE_DIR)],
        timeout=180,
    )
    if "NEX_GUI_TESTED" not in output:
        raise SystemExit("REFERENCE_BUILD_BLOCKED: GUI test did not report NEX_GUI_TESTED\n" + output[-2000:])
    captures = []
    for name in CAPTURES:
        path = CAPTURE_DIR / name
        if not path.is_file():
            raise SystemExit(f"REFERENCE_BUILD_BLOCKED: GUI capture missing: {name}")
        width, height = _png_size(path)
        captures.append({"file": f"evidence/{name}", "bytes": path.stat().st_size,
                         "sha256": _sha(path), "width": width, "height": height})
    return captures


def _build(run_gui: bool) -> dict[str, Any]:
    godot = _resolve_godot()
    version = _godot_version(godot)
    templates = _templates_dir()
    _stage_project()
    smoke = _run_checked([str(godot), "--headless", "--path", str(STAGE),
                          "--rendering-method", "gl_compatibility", "--script", "res://smoke.gd"])
    if "NEX_NATIVE_IMPORT_SMOKE_PASS" not in smoke:
        raise SystemExit("REFERENCE_BUILD_BLOCKED: staged project smoke did not pass\n" + smoke[-4000:])
    EXE.unlink(missing_ok=True)
    export_log = _run_checked([str(godot), "--headless", "--path", str(STAGE),
                               "--export-release", "Windows Desktop", str(EXE)], timeout=600)
    if not EXE.is_file() or EXE.stat().st_size < 50_000_000:
        raise SystemExit("REFERENCE_BUILD_BLOCKED: exported executable is missing or too small")
    headless = _run_checked([str(EXE), "--headless", "--quit-after", "120"], timeout=180)
    if "ERROR:" in headless:
        raise SystemExit("REFERENCE_BUILD_BLOCKED: exported executable reported errors\n" + headless[-4000:])
    captures = _capture_gui() if run_gui else []
    shutil.rmtree(STAGE, ignore_errors=True)
    return {
        "schema_version": "nex_reference_build.v1",
        "captured_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_sha": _source_sha(),
        "godot": {"version": GODOT_VERSION, "commit": GODOT_COMMIT, "reported": version},
        "templates": {
            "version": (templates / "version.txt").read_text(encoding="utf-8").strip(),
            "windows_release_sha256": _sha(templates / "windows_release_x86_64.exe"),
        },
        "preset": {"name": "Windows Desktop", "platform": "Windows Desktop",
                   "architecture": "x86_64", "embedded_pck": True},
        "artifact": {"path": "build/NEXEngine.exe", "bytes": EXE.stat().st_size, "sha256": _sha(EXE)},
        "checks": {
            "staged_project_smoke": "PASS",
            "export": "PASS",
            "exported_headless": "PASS",
            "gui": "PASS" if run_gui else "NOT_RUN",
        },
        "gui_captures": captures,
        "verdict": "REFERENCE_BUILD_PASS" if run_gui else "REFERENCE_BUILD_PASS_HEADLESS_ONLY",
        "limitations": [
            "reference visual lab export only; not a game, engine release or store build",
            "no installer, code signing, auto-update or distribution license",
            "no FPS, GPU p95, VRAM, quality or PoE2 parity claim",
            "GUI screenshots are local evidence, not a benchmark",
            "the executable is not committed; rebuild it with --build",
            "audit remains ADMIN_SOLO / NOT_INDEPENDENT",
        ],
    }


def _preset_ok() -> list[str]:
    errors: list[str] = []
    if not PRESET.is_file():
        return ["export_presets.cfg is missing"]
    text = PRESET.read_text(encoding="utf-8")
    for token in ('name="Windows Desktop"', 'platform="Windows Desktop"',
                  'binary_format/architecture="x86_64"', 'binary_format/embed_pck=true',
                  'application/icon="res://icon.ico"'):
        if token not in text:
            errors.append(f"export preset missing {token}")
    if "custom_template/release=" in text and 'custom_template/release=""' not in text:
        errors.append("export preset must not use an unpinned custom template")
    if not ICON.is_file() or not BRAND_ICON.is_file():
        errors.append("build icon or brand icon is missing")
    elif _sha(ICON) != _sha(BRAND_ICON):
        errors.append("nex_bench/icon.ico does not match the M12 brand ICO")
    return errors


def _evidence_ok() -> list[str]:
    errors: list[str] = []
    if not EVIDENCE_JSON.is_file():
        return ["reference-build.v1.json is missing"]
    report = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    if report.get("schema_version") != "nex_reference_build.v1":
        errors.append("evidence schema is invalid")
    if report.get("verdict") not in {"REFERENCE_BUILD_PASS", "REFERENCE_BUILD_PASS_HEADLESS_ONLY"}:
        errors.append("evidence verdict is not a pass")
    artifact = report.get("artifact", {})
    if not re.fullmatch(r"[0-9a-f]{64}", str(artifact.get("sha256", ""))):
        errors.append("artifact SHA-256 is invalid")
    if int(artifact.get("bytes", 0)) < 50_000_000:
        errors.append("artifact size is implausibly small")
    checks = report.get("checks", {})
    for key in ("staged_project_smoke", "export", "exported_headless"):
        if checks.get(key) != "PASS":
            errors.append(f"check {key} did not pass")
    if checks.get("gui") not in {"PASS", "NOT_RUN"}:
        errors.append("GUI check is invalid")
    if checks.get("gui") == "PASS":
        captures = report.get("gui_captures", [])
        if len(captures) != len(CAPTURES):
            errors.append("GUI capture count is wrong")
        for capture in captures:
            path = EVIDENCE_DIR / str(capture.get("file", ""))
            if not path.is_file():
                errors.append(f"GUI capture missing: {capture.get('file')}")
                continue
            if _sha(path) != capture.get("sha256"):
                errors.append(f"GUI capture hash mismatch: {capture.get('file')}")
            if _png_size(path) != (capture.get("width"), capture.get("height")):
                errors.append(f"GUI capture dimensions mismatch: {capture.get('file')}")
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8")
    if "build/" not in ignored:
        errors.append(".gitignore must ignore build/")
    if _git("ls-files", "build/NEXEngine.exe"):
        errors.append("build/NEXEngine.exe must not be tracked")
    return errors


def _render_markdown(report: dict[str, Any]) -> str:
    artifact = report["artifact"]
    lines = [
        "# NEX reference build · Windows x86_64",
        "",
        "**Status:** `REFERENCE_BUILD_VERIFIED / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Source SHA:** `{report['source_sha']}` · **Godot:** {report['godot']['version']} "
        f"(`{report['godot']['commit'][:9]}`)",
        "",
        "## Artifact",
        "",
        f"- `{artifact['path']}` · **{artifact['bytes']} bytes**",
        f"- SHA-256: `{artifact['sha256']}`",
        "- O executável não é versionado; `build/` é ignorado.",
        "",
        "## Verificação",
        "",
        f"- Smoke do projeto staged: **{report['checks']['staged_project_smoke']}**",
        f"- Export release: **{report['checks']['export']}**",
        f"- Executável headless: **{report['checks']['exported_headless']}**",
        f"- GUI Windows: **{report['checks']['gui']}**",
        "",
    ]
    if report.get("gui_captures"):
        lines.extend(["## Capturas GUI", "", "| Arquivo | Dimensões | SHA-256 |", "|---|---|---|"])
        for capture in report["gui_captures"]:
            lines.append(f"| `{capture['file']}` | {capture['width']}×{capture['height']} | `{capture['sha256'][:16]}…` |")
        lines.append("")
    lines.extend(["## Limitações", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "Gerado por `scripts/build_reference_export.py`; o executável deve ser reconstruído localmente.", ""])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--gui", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        errors = _preset_ok() + _evidence_ok()
        if errors:
            for error in errors:
                print("REFERENCE_BUILD_CHECK_FAIL: " + error)
            return 1
        print("REFERENCE_BUILD_CHECK_PASS: preset, icon, evidence and captures")
        return 0
    if args.build:
        report = _build(args.gui)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        EVIDENCE_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                                 encoding="utf-8", newline="\n")
        EVIDENCE_MD.write_text(_render_markdown(report), encoding="utf-8", newline="\n")
        print(f"REFERENCE_BUILD_PASS: {report['artifact']['bytes']} bytes / {report['artifact']['sha256'][:16]}…")
        return 0
    print("usage: build_reference_export.py --check | --build [--gui]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

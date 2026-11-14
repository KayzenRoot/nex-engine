"""Shared helpers for the NEX M09 benchmark builders."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def load_json(path: Path) -> Any:
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)

    def constant(token):
        raise ValueError(f"non-finite JSON: {token}")

    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=constant)


def safe_output(base: Path, path: Path) -> Path:
    resolved_base = base.resolve()
    candidate = path.resolve()
    if candidate.parent != resolved_base:
        raise ValueError("output path escapes the benchmark directory")
    return candidate


def write_report(report: dict[str, Any], base: Path, json_path: Path, md_path: Path,
                 render_json: Callable[[dict[str, Any]], str],
                 render_md: Callable[[dict[str, Any]], str]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    with open(safe_output(base, json_path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_json(report))
    with open(safe_output(base, md_path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_md(report))


def run_cli(build: Callable[[], dict[str, Any]],
            render_json: Callable[[dict[str, Any]], str],
            render_md: Callable[[dict[str, Any]], str],
            base: Path, json_path: Path, md_path: Path, argv: list[str], prefix: str) -> int:
    report = build()
    rendered_json = render_json(report)
    rendered_md = render_md(report)
    if argv == ["--check"]:
        if not json_path.is_file() or not md_path.is_file():
            print(f"{prefix}_CHECK_FAIL: outputs missing")
            return 1
        if json_path.read_text(encoding="utf-8") != rendered_json:
            print(f"{prefix}_CHECK_FAIL: JSON is stale")
            return 1
        if md_path.read_text(encoding="utf-8") != rendered_md:
            print(f"{prefix}_CHECK_FAIL: Markdown is stale")
            return 1
        run_count = report.get("runs", [])
        count = run_count if isinstance(run_count, int) else len(run_count)
        print(f"{prefix}_CHECK_PASS: {count} runs")
        return 0
    if argv:
        print("usage: builder [--check]")
        return 2
    write_report(report, base, json_path, md_path, render_json, render_md)
    run_count = report.get("runs", [])
    count = run_count if isinstance(run_count, int) else len(run_count)
    print(f"{prefix}_WRITE_PASS: {count} runs")
    return 0

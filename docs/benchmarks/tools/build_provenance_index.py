#!/usr/bin/env python3
"""Build a provenance index from the canonical checkpoint.

The index is a navigation aid: it lists every checkpoint block that records a
protected PR and merge SHA, its issue numbers, verdict/status and audit label.
It does not replace the checkpoint, which remains the authority.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "m09" / "tools"))
from common import load_json, run_cli  # noqa: E402 - shared local tool module

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKPOINT = REPO_ROOT / ".engineering" / "CHECKPOINT.json"
OUTPUT_DIR = REPO_ROOT / "docs" / "benchmarks"
REPORT_JSON = OUTPUT_DIR / "provenance-index.v1.json"
REPORT_MD = OUTPUT_DIR / "PROVENANCE-INDEX.md"

REPORT_SCHEMA = "nex_provenance_index.v1"
ISSUE_KEYS = ("issue", "secondaryIssue", "m01Issue", "m02Issue")


def _issues(value: dict[str, Any]) -> list[int]:
    issues = [value[key] for key in ISSUE_KEYS if isinstance(value.get(key), int)]
    if isinstance(value.get("issues"), list):
        issues.extend(item for item in value["issues"] if isinstance(item, int))
    return list(dict.fromkeys(issues))


def build_report() -> dict[str, Any]:
    checkpoint = load_json(CHECKPOINT)
    entries = []
    for key, value in checkpoint.items():
        if not isinstance(value, dict):
            continue
        pr = value.get("pr")
        merge = value.get("protectedMergeSha")
        if not isinstance(pr, int) or not isinstance(merge, str):
            continue
        entries.append({
            "block": key,
            "id": value.get("id", key),
            "pr": pr,
            "protectedMergeSha": merge,
            "issues": _issues(value),
            "verdict": value.get("verdict") or value.get("status") or "",
            "audit": value.get("audit", ""),
        })
    entries.sort(key=lambda entry: entry["pr"])
    labels = sorted({entry["audit"] for entry in entries if entry["audit"]})
    return {
        "schema_version": REPORT_SCHEMA,
        "source": ".engineering/CHECKPOINT.json",
        "session_date": "2026-11-14",
        "entries": entries,
        "summary": {
            "entries": len(entries),
            "min_pr": entries[0]["pr"] if entries else None,
            "max_pr": entries[-1]["pr"] if entries else None,
            "unique_merge_shas": len({entry["protectedMergeSha"] for entry in entries}),
            "audit_labels": labels,
        },
        "verdict": "PROVENANCE_INDEX_DERIVED_FROM_CHECKPOINT",
        "limitations": [
            "derived from the canonical checkpoint; it does not prove independent review",
            "audit remains ADMIN_SOLO / NOT_INDEPENDENT",
            "the checkpoint is the authority; this index is a navigation aid",
            "entries without a protected PR and merge SHA are not listed",
        ],
        "runs": len(entries),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# NEX Engine · Provenance index",
        "",
        "**Status:** `PROVENANCE_INDEX_DERIVED_FROM_CHECKPOINT / ADMIN_SOLO_NOT_INDEPENDENT`",
        "",
        f"**Fonte:** `{report['source']}` · **Entradas:** {summary['entries']} · "
        f"**PRs:** {summary['min_pr']}–{summary['max_pr']}",
        "",
        "| Bloco | ID | PR | Merge SHA | Issues | Veredito/Status | Auditoria |",
        "|---|---|---:|---|---|---|---|",
    ]
    for entry in report["entries"]:
        issues = ",".join(str(issue) for issue in entry["issues"]) or "—"
        lines.append(
            f"| {entry['block']} | {entry['id']} | {entry['pr']} | `{entry['protectedMergeSha']}` | "
            f"{issues} | {entry['verdict'] or '—'} | {entry['audit'] or '—'} |"
        )
    lines.extend(["", "## Limitações", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(["", "Índice gerado por `docs/benchmarks/tools/build_provenance_index.py`; o checkpoint é a autoridade.", ""])
    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    return run_cli(build_report, render_json, render_markdown, OUTPUT_DIR, REPORT_JSON, REPORT_MD, argv, "PROVENANCE_INDEX")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

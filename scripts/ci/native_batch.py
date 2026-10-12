#!/usr/bin/env python3
"""Dispatch M00 native verification after five owner-accepted module PR merges.

An accepted module PR has the owner-controlled label nex-native-module.
The most recent successful workflow_dispatch native run on main is the anchor.
Unknown API state stops this job; it never silently skips necessary validation.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

BASELINE_SHA = "0c6cdbfc13bd0c1c8e80d293f7da7f2302027861"
MODULE_LABEL = "nex-native-module"
BATCH_SIZE = 5
WORKFLOW = "nex-m00-smoke.yml"
MAX_COMMITS = 250

@dataclass(frozen=True)
class Decision:
    anchor: str
    head: str
    accepted_modules: tuple[str, ...]
    run_full: bool

    def to_dict(self):
        return {
            "anchor": self.anchor, "head": self.head,
            "accepted_module_prs": list(self.accepted_modules),
            "module_count": len(self.accepted_modules),
            "batch_size": BATCH_SIZE, "run_full": self.run_full
        }

def validate_sha(sha: str) -> str:
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Expected lowercase 40-character Git commit SHA")
    return sha

def accepted_module_pr(sha: str, pull_requests: list[dict]) -> str | None:
    for pr in pull_requests:
        if (pr.get("merged_at") and pr.get("merge_commit_sha") == sha
            and any(item.get("name") == MODULE_LABEL for item in pr.get("labels", []))):
            number = pr.get("number")
            if isinstance(number, int) and number > 0:
                return f"#{number}"
    return None

def compute_decision(anchor: str, head: str, commits: list[dict], prs_by_sha: dict[str, list[dict]]) -> Decision:
    validate_sha(anchor)
    validate_sha(head)
    found = []
    for commit in commits:
        sha = validate_sha(commit["sha"])
        if sha not in prs_by_sha:
            raise ValueError(f"Missing PR association lookup: {sha}")
        module_pr = accepted_module_pr(sha, prs_by_sha[sha])
        if module_pr is not None:
            found.append(module_pr)
    return Decision(anchor, head, tuple(found), len(found) >= BATCH_SIZE)

class GitHub:
    def __init__(self, token: str, api_url: str = "https://api.github.com"):
        if not token:
            raise ValueError("Missing GITHUB_TOKEN")
        self.token = token
        if api_url != "https://api.github.com":
            raise ValueError("GitHub API must be the pinned HTTPS host")
        self.api_url = api_url

    def request(self, method: str, path: str, payload: dict | None = None):
        # GitHub compare uses <base>...<head>, a legitimate path segment.
        # Reject actual navigation segments without rejecting that ellipsis.
        path_only = path.split("?", 1)[0]
        segments = path_only.split("/")
        if (
            not path.startswith("/repos/")
            or "//" in path_only
            or "\\" in path
            or "%" in path_only
            or any(segment in (".", "..") for segment in segments)
        ):
            raise ValueError("Invalid GitHub API path")
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(
            self.api_url + path, data=data, method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "nex-native-batch-sentinel"
            }
        )
        try:
            with urlopen(req, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"GitHub API failed ({method} {path}): {error}") from error

def request_object(api: GitHub, method: str, path: str) -> dict:
    response = api.request(method, path)
    if not isinstance(response, dict):
        raise RuntimeError("GitHub API returned malformed object response")
    return response


def workflow_runs(api: GitHub, repository: str, success_only: bool = False) -> list[dict]:
    """Read paginated main-branch native dispatches; reject incomplete data."""
    output: list[dict] = []
    filter_status = "&status=success" if success_only else ""
    for page in range(1, 11):
        path = (
            f"/repos/{repository}/actions/workflows/{WORKFLOW}/runs"
            f"?branch=main&event=workflow_dispatch{filter_status}&per_page=100&page={page}"
        )
        result = request_object(api, "GET", path)
        runs = result.get("workflow_runs")
        if not isinstance(runs, list) or any(not isinstance(item, dict) for item in runs):
            raise RuntimeError("GitHub workflow runs were missing or malformed")
        output.extend(runs)
        if len(runs) < 100:
            return output
    raise RuntimeError("Too many native runs to establish a complete anchor; steward review required")


def latest_anchor(api: GitHub, repository: str) -> str:
    matching = [
        run for run in workflow_runs(api, repository, success_only=True)
        if run.get("event") == "workflow_dispatch"
        and run.get("head_branch") == "main"
        and run.get("status") == "completed"
        and run.get("conclusion") == "success"
    ]
    if not matching:
        return BASELINE_SHA
    if any(not isinstance(item.get("created_at"), str) or not item["created_at"] for item in matching):
        raise RuntimeError("Completed native runs lack a trustworthy created_at timestamp")
    return validate_sha(max(matching, key=lambda item: item["created_at"])["head_sha"])


def native_run_already_active(api: GitHub, repository: str, head: str) -> bool:
    """Avoid canceling the current full native run on any protected-main SHA."""
    validate_sha(head)
    active = {"queued", "requested", "waiting", "in_progress", "pending"}
    return any(run.get("status") in active for run in workflow_runs(api, repository))


def compare_commits(api: GitHub, repository: str, anchor: str, head: str) -> list[dict]:
    if anchor == head:
        return []
    commits = []
    page = 1
    while True:
        path = f"/repos/{repository}/compare/{anchor}...{head}?per_page=100&page={page}"
        result = request_object(api, "GET", path)
        if result.get("status") not in ("ahead", "identical"):
            raise RuntimeError("Full-build anchor is not an ancestor of protected main")
        total = result.get("total_commits")
        if type(total) is not int or total < 1:
            raise RuntimeError("Malformed or missing compare commit count")
        if total > MAX_COMMITS:
            raise RuntimeError("History exceeds MAX_COMMITS; requires steward rebaseline")
        current = result.get("commits")
        if not isinstance(current, list) or any(not isinstance(c, dict) for c in current):
            raise RuntimeError("GitHub comparison contains malformed commits")
        commits.extend(current)
        if len(commits) >= total:
            break
        if not current or page > 3:
            raise RuntimeError("Incomplete GitHub comparison")
        page += 1
    if len(commits) != total:
        raise RuntimeError("Incomplete compare history")
    return commits

def evaluate(api: GitHub, repository: str, head: str) -> Decision:
    validate_sha(head)
    anchor = latest_anchor(api, repository)
    commits = compare_commits(api, repository, anchor, head)
    associated = {}
    for item in commits:
        sha = validate_sha(item["sha"])
        pulls = api.request("GET", f"/repos/{repository}/commits/{sha}/pulls?per_page=100")
        if not isinstance(pulls, list):
            raise RuntimeError("PR association API returned malformed response")
        associated[sha] = pulls
    return compute_decision(anchor, head, commits, associated)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repository", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    repository = args.repository
    if (repository.count("/") != 1 or not all(
        part.replace("-", "").replace("_", "").isalnum()
        for part in repository.split("/"))):
        raise ValueError("Invalid repository identifier")
    if repository != os.environ.get("GITHUB_REPOSITORY"):
        raise RuntimeError("Repository identity mismatch")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise RuntimeError("Dispatch may run only from protected main")
    api = GitHub(os.environ.get("GITHUB_TOKEN", ""))
    decision = evaluate(api, repository, args.head)
    print(json.dumps(decision.to_dict(), sort_keys=True))
    if decision.run_full and not args.dry_run:
        if native_run_already_active(api, repository, args.head):
            print("Full native build already active on protected main; no competing dispatch.")
        else:
            api.request("POST", f"/repos/{repository}/actions/workflows/{WORKFLOW}/dispatches",
                        {"ref": "main", "inputs": {"verification_reason": "five-module-batch"}})
            print("Native source verification dispatched for five accepted module merges.")
    elif decision.run_full:
        print("DRY_RUN: would dispatch a full source verification.")
    else:
        print("Fast Lane: fewer than five accepted modules, no full native build.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError) as error:
        print(f"BLOCKED_NATIVE_BATCH: {error}", file=sys.stderr)
        raise SystemExit(2)

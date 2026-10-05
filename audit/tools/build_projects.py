#!/usr/bin/env python3
"""Build runs/projects.json from the ws-run*/data/manifest.csv files.

One record per (run, project code); the repository URL is normalised into
host / owner-path / repo plus an optional branch (from a /tree/<branch> URL).
"""
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
RUNS = ["ws-run1", "ws-run2"]


def parse_repo(url):
    url = url.strip()
    if not url:
        return None
    u = urlparse(url)
    parts = [p for p in u.path.split("/") if p]
    branch = None
    if "tree" in parts:
        i = parts.index("tree")
        branch = "/".join(parts[i + 1:]) or None
        parts = parts[:i]
    if parts and parts[-1] == "-":  # gitlab /-/tree/...
        parts = parts[:-1]
    parts[-1] = re.sub(r"\.git$", "", parts[-1])
    return {
        "host": u.netloc.lower(),
        "path": "/".join(parts),
        "branch": branch,
        "url_as_listed": url,
    }


def main():
    out = []
    for run in RUNS:
        with (ROOT / run / "data" / "manifest.csv").open(newline="") as f:
            for row in csv.DictReader(f):
                out.append({
                    "run": run,
                    "code": row["CODE"],
                    "project": row["PROJECT"],
                    "slot_size": row["SLOT_SIZE"],
                    "visibility": row["VISIBILITY"],
                    "details": row["PROJECT_DETAILS"],
                    "top": row["TOP"],
                    "sha256": row["SHA256"],
                    "layout": row["LAYOUT"],
                    "repo": parse_repo(row["REPOSITORY"]),
                })
    json.dump(out, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

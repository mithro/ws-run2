#!/usr/bin/env python3
"""Query GitHub for every github.com repo in projects.json.

Writes github_state.json: canonical name (after renames/transfers), whether
the authenticated user has starred it, which of the user's repos are forks
of it, its fork parent / network root, detected licence and size.
"""
import json
import subprocess
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]

FIELDS = """
  nameWithOwner url isFork isArchived isPrivate diskUsage viewerHasStarred
  description homepageUrl createdAt pushedAt stargazerCount forkCount
  defaultBranchRef { name target { oid } }
  licenseInfo { spdxId name }
  parent { nameWithOwner }
  myForks: forks(affiliations: [OWNER], first: 10) { nodes { nameWithOwner } }
  releases(first: 1) { totalCount }
  repositoryTopics(first: 20) { nodes { topic { name } } }
"""


def main():
    projects = json.load((RUNS / "projects.json").open())
    repos = sorted({p["repo"]["path"] for p in projects
                    if p["repo"] and p["repo"]["host"] == "github.com"})
    parts = []
    for i, path in enumerate(repos):
        owner, name = path.split("/", 1)
        parts.append('r%d: repository(owner: %s, name: %s) {%s}'
                     % (i, json.dumps(owner), json.dumps(name), FIELDS))
    query = "query { viewer { login } " + " ".join(parts) + " }"
    res = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query],
                         capture_output=True, text=True)
    if not res.stdout:
        sys.exit("gh failed: " + res.stderr)
    body = json.loads(res.stdout)
    data = body.get("data") or {}
    out = {"viewer": data.get("viewer", {}).get("login"),
           "errors": body.get("errors", []), "repos": {}}
    for i, path in enumerate(repos):
        out["repos"][path] = data.get("r%d" % i)
    json.dump(out, (RUNS / "github_state.json").open("w"), indent=1)
    print("viewer:", out["viewer"], "errors:", len(out["errors"]))
    for e in out["errors"]:
        print("  ERROR", e.get("path"), e.get("message"))
    fmt = "%-62s %-5s %-34s %-12s %8s %s"
    print(fmt % ("listed (-> canonical)", "star", "my forks", "license", "KB", "parent"))
    for path, r in out["repos"].items():
        if r is None:
            print(fmt % (path, "?", "MISSING", "", "", ""))
            continue
        name = path if r["nameWithOwner"] == path else path + " -> " + r["nameWithOwner"]
        print(fmt % (name, "yes" if r["viewerHasStarred"] else "NO",
                     ",".join(n["nameWithOwner"] for n in r["myForks"]["nodes"]) or "NONE",
                     (r["licenseInfo"] or {}).get("spdxId") or "-",
                     r["diskUsage"], (r["parent"] or {}).get("nameWithOwner") or ""))


if __name__ == "__main__":
    main()

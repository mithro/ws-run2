#!/usr/bin/env python3
"""Star every github.com project repo and fork it to the authenticated user.

Reads github_state.json (run github_state.py first).  Skips forking repos
whose fork network the user already has a different fork in: GitHub allows
one fork per network per account and silently returns the existing one.
"""
import json
import subprocess
import time
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]


def gh(*args):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main():
    state = json.load((RUNS / "github_state.json").open())
    me = state["viewer"]
    # network roots the user already has a fork of (root -> existing fork)
    taken = {}
    for listed, r in state["repos"].items():
        root = (r["parent"] or {}).get("nameWithOwner") or r["nameWithOwner"]
        for f in r["myForks"]["nodes"]:
            taken[root] = f["nameWithOwner"]
    rc, out, err = gh("repos/%s/gf180mcu-project-template" % me, "--jq", ".parent.full_name")
    if rc == 0 and out:
        taken[out] = "%s/gf180mcu-project-template" % me

    for listed, r in state["repos"].items():
        full = r["nameWithOwner"]
        if not r["viewerHasStarred"]:
            rc, out, err = gh("-X", "PUT", "user/starred/" + full)
            print("STAR %s %s %s" % ("ok" if rc == 0 else "FAILED", full, err), flush=True)
        else:
            print("STAR already %s" % full, flush=True)

        if r["myForks"]["nodes"]:
            print("FORK already %s -> %s" % (full, r["myForks"]["nodes"][0]["nameWithOwner"]), flush=True)
            continue
        root = (r["parent"] or {}).get("nameWithOwner") or full
        if root in taken:
            print("FORK blocked %s (network %s already forked as %s)" % (full, root, taken[root]), flush=True)
            continue
        rc, out, err = gh("-X", "POST", "repos/%s/forks" % full, "--jq",
                          '[.full_name, (.parent.full_name // ""), (.source.full_name // "")] | @tsv')
        if rc != 0:
            print("FORK FAILED %s %s %s" % (full, out, err), flush=True)
        else:
            new, parent, source = (out.split("\t") + ["", ""])[:3]
            ok = parent.lower() == full.lower()
            print("FORK %s %s -> %s (parent=%s source=%s)" % ("ok" if ok else "MISMATCH", full, new, parent, source), flush=True)
            if ok:
                taken[root] = new
        time.sleep(3)


if __name__ == "__main__":
    main()

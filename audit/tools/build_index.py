#!/usr/bin/env python3
"""Build runs/README.md: one index over every project's summary.md and the audit.

Inputs: projects.json, audit.json, the digest lines (digests.tsv, overridden by
digests_layout.tsv for projects checked against the taped-out layout; see
digests.py) and the "### Verdict:" line of each summary.md, which must agree
with the digest.
"""
import json
import re
from pathlib import Path

from digests import load_digests

RUNS = Path(__file__).resolve().parents[1]
ORDER = {"High": 0, "Medium": 1, "Low": 2, "None": 3, "Unknown": 4}


def main():
    projects = json.load((RUNS / "projects.json").open())
    audit = {(a["run"], a["code"]): a for a in json.load((RUNS / "audit.json").open())}
    dig, layout_checked = load_digests()
    rows = []
    for p in projects:
        key = "%s/%s" % (p["run"], p["code"])
        text = (RUNS / key / "summary.md").read_text()
        verdict = re.search(r"^### Verdict: (\w+)", text, re.M).group(1)
        d = dig.get(key)
        if d:
            assert d["verdict"] == verdict, (key, d["verdict"], verdict)
        rows.append((p, key, verdict, d, audit[(p["run"], p["code"])]))

    out = ["# wafer.space GF180MCU run 1 (G801) and run 2 (G802): project index", "",
           "Each project directory `<run>/<CODE>/` holds the full clone (`repo/`), release assets",
           "(`releases/`), the platform record (`project.json`) and an analysis (`summary.md`).",
           "The licence and README audit is in [AUDIT.md](AUDIT.md).", "",
           "Verdict = value for GF180MCU characterisation and PDK development, as judged in each",
           "`summary.md`. Statements marked inferred there are inferred here too.",
           "\"Layout checked\" = the summary has been checked against the layout that was taped out",
           "(%d of %d projects so far); the others are written from the repository alone." % (
               len(layout_checked), len(rows)), ""]
    counts = {}
    for r in rows:
        counts[r[2]] = counts.get(r[2], 0) + 1
    out += ["| Verdict | Projects |", "|---|---|"]
    out += ["| %s | %d |" % (v, counts[v]) for v in sorted(counts, key=ORDER.get)]
    out.append("")

    out += ["## Projects worth measuring (High and Medium)", "",
            "| Project | Verdict | What it is | Authors | Test structures / measurable circuits | Candidate PDK additions | Caveats |",
            "|---|---|---|---|---|---|---|"]
    for p, key, verdict, d, a in sorted(rows, key=lambda r: (ORDER[r[2]], r[1])):
        if verdict in ("High", "Medium"):
            out.append("| [%s](%s/summary.md) | %s | %s | %s | %s | %s | %s |" % (
                key, key, verdict, d["what"], d["authors"], d["char"], d["pdk"], d["flags"]))
    out.append("")

    for run in sorted({p["run"] for p in projects}):
        out += ["## %s: all projects" % run, "",
                "| Code | Project | Slot | Verdict | What the repo contains | Authors | LICENSE | README | Layout checked | Summary |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for p, key, verdict, d, a in rows:
            if p["run"] != run:
                continue
            if a["status"] == "cloned":
                lic = ", ".join(sorted({x["spdx"] for x in a["license"]["files"]})) or "none"
                readme = a["readme"]["verdict"]
            else:
                lic = readme = "n/a"
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | [summary](%s/summary.md) |" % (
                p["code"], p["project"].replace("|", "/"), p["slot_size"], verdict,
                d["what"] if d else "No repository listed", d["authors"] if d else "not stated",
                lic, readme, "yes" if key in layout_checked else "no", key))
        out.append("")
    (RUNS / "README.md").write_text("\n".join(out))
    print("rows", len(rows), counts)


if __name__ == "__main__":
    main()

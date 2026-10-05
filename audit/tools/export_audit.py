#!/usr/bin/env python3
"""Copy one run's audit data into the `audit/` directory of that run's repository.

The workspace (`runs/`) holds both runs plus the full clones. Each run
repository's `audit` branch gets only that run's reports:

    audit/README.md            index of this run's projects with verdicts
    audit/AUDIT.md             licence and README audit for this run
    audit/audit.json           the same audit, machine readable
    audit/platform_licenses.csv  licence claimed on platform.wafer.space
    audit/<CODE>/summary.md    analysis of the project
    audit/<CODE>/project.json  manifest row
    audit/<CODE>/clone.json    which commit of the project repo was analysed
    audit/<CODE>/layout.json   measurements of the taped-out layout (if made)
    audit/<CODE>/images/       renders of the taped-out layout (if made)
    audit/tools/               the scripts that produced all of this

Usage: export_audit.py <run> <checkout of the run repository>
"""
import csv
import json
import re
import shutil
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]
ORDER = {"High": 0, "Medium": 1, "Low": 2, "None": 3, "Unknown": 4}
TITLES = {"ws-run1": "wafer.space GF180MCU run 1 (G801)", "ws-run2": "wafer.space GF180MCU run 2 (G802)"}


def audit_section(run):
    """The table for one run out of the combined AUDIT.md."""
    lines = (RUNS / "AUDIT.md").read_text().split("\n")
    start = lines.index("## %s" % run) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return [line for line in lines[start:end]]


def write_index(run, projects, audit, out_dir):
    dig = {}
    for row in csv.reader((RUNS / "digests.tsv").open(), delimiter="\t", quoting=csv.QUOTE_NONE):
        dig[row[0]] = dict(zip(("verdict", "what", "authors", "char", "pdk", "flags"), row[1:]))
    rows = []
    for p in projects:
        key = "%s/%s" % (run, p["code"])
        text = (RUNS / key / "summary.md").read_text()
        verdict = re.search(r"^### Verdict: (\w+)", text, re.M).group(1)
        rows.append((p, verdict, dig.get(key), audit[p["code"]]))

    out = ["# %s: project audit" % TITLES[run], "",
           "One directory per public project on this run. Each has an analysis (`summary.md`) of the",
           "project's repository and of the layout that was actually taped out, the manifest row",
           "(`project.json`), the commit that was analysed (`clone.json`) and, where a layout was",
           "extracted from the reticle, measurements (`layout.json`) and renders (`images/`).", "",
           "The licence and README audit is in [AUDIT.md](AUDIT.md).", "",
           "Verdict = value for GF180MCU characterisation and PDK development, as judged in each",
           "`summary.md`.", ""]
    counts = {}
    for r in rows:
        counts[r[1]] = counts.get(r[1], 0) + 1
    out += ["| Verdict | Projects |", "|---|---|"]
    out += ["| %s | %d |" % (v, counts[v]) for v in sorted(counts, key=ORDER.get)]
    out.append("")

    out += ["## Projects worth measuring (High and Medium)", "",
            "| Project | Verdict | What it is | Authors | Test structures / measurable circuits | Candidate PDK additions | Caveats |",
            "|---|---|---|---|---|---|---|"]
    for p, verdict, d, a in sorted(rows, key=lambda r: (ORDER[r[1]], r[0]["code"])):
        if verdict in ("High", "Medium") and d:
            out.append("| [%s](%s/summary.md) | %s | %s | %s | %s | %s | %s |" % (
                p["code"], p["code"], verdict, d["what"], d["authors"], d["char"], d["pdk"], d["flags"]))
    out.append("")

    out += ["## All projects", "",
            "| Code | Project | Slot | Verdict | What it contains | Authors | LICENSE | README | Summary |",
            "|---|---|---|---|---|---|---|---|---|"]
    for p, verdict, d, a in rows:
        if a["status"] == "cloned":
            lic = ", ".join(sorted({x["spdx"] for x in a["license"]["files"]})) or "none"
            readme = a["readme"]["verdict"]
        else:
            lic = readme = "n/a"
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | [summary](%s/summary.md) |" % (
            p["code"], p["project"].replace("|", "/"), p["slot_size"], verdict,
            d["what"] if d else "No repository listed", d["authors"] if d else "not stated",
            lic, readme, p["code"]))
    out.append("")
    (out_dir / "README.md").write_text("\n".join(out))
    return counts


def main():
    run, checkout = sys.argv[1], Path(sys.argv[2])
    out_dir = checkout / "audit"
    out_dir.mkdir(exist_ok=True)
    projects = [p for p in json.load((RUNS / "projects.json").open()) if p["run"] == run]
    audit_rows = [a for a in json.load((RUNS / "audit.json").open()) if a["run"] == run]
    audit = {a["code"]: a for a in audit_rows}

    counts = write_index(run, projects, audit, out_dir)
    (out_dir / "AUDIT.md").write_text("\n".join(
        ["# %s: repository audit" % TITLES[run], "",
         "Checks, for every public project with a repository, whether the repository has a LICENSE",
         "file that matches the licence claimed on platform.wafer.space, and whether it has a real",
         "top-level README.md (not the project template's). Generated by `tools/audit.py`.", ""]
        + audit_section(run)))
    (out_dir / "audit.json").write_text(json.dumps(audit_rows, indent=1) + "\n")

    # Licence claims: keep the claim itself, not the platform's internal identifiers.
    with (RUNS / "platform_licenses.csv").open() as f, (out_dir / "platform_licenses.csv").open("w", newline="") as g:
        writer = csv.writer(g, lineterminator="\n")
        writer.writerow(["CODE", "LICENSE", "OTHER_SPDX", "PROJECT_NAME", "REPOSITORY_URL"])
        for row in csv.DictReader(f):
            if row["RUN"] == run:
                writer.writerow([row["CODE"], row["LICENSE"], row["OTHER_SPDX"], row["PROJECT_NAME"],
                                 row["REPOSITORY_URL"]])

    copied = 0
    for p in projects:
        src, dst = RUNS / run / p["code"], out_dir / p["code"]
        dst.mkdir(exist_ok=True)
        for name in ("summary.md", "project.json", "layout.json"):
            if (src / name).exists():
                shutil.copy2(src / name, dst / name)
                copied += 1
        if (src / "clone_status.json").exists():
            status = json.load((src / "clone_status.json").open())
            for key in ("mirror", "seconds"):  # local paths and timings mean nothing elsewhere
                status.pop(key, None)
            (dst / "clone.json").write_text(json.dumps(status, indent=1) + "\n")
        if (src / "images").is_dir():
            if (dst / "images").exists():
                shutil.rmtree(dst / "images")
            shutil.copytree(src / "images", dst / "images")

    tools = out_dir / "tools"
    if tools.exists():
        shutil.rmtree(tools)
    shutil.copytree(RUNS / "tools", tools, ignore=shutil.ignore_patterns("__pycache__", ".venv", "*.pyc"))
    print(run, "projects", len(projects), "files", copied, counts)


if __name__ == "__main__":
    main()

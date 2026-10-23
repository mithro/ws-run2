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

A summary whose layout check is unfinished (it has a "## Taped-out layout"
section or an images/ directory, but no line in digests_layout.tsv) is not
exported: the checkout keeps its previous summary.md and images/, and a warning
is printed. One-off scratch scripts in tools/ (UNPUBLISHED_TOOLS) are not copied.

Usage: export_audit.py <run> <checkout of the run repository>
"""
import csv
import json
import re
import shutil
import sys
from pathlib import Path

from digests import load_digests

RUNS = Path(__file__).resolve().parents[1]
ORDER = {"High": 0, "Medium": 1, "Low": 2, "None": 3, "Unknown": 4}
TITLES = {"ws-run1": "wafer.space GF180MCU run 1 (G801)", "ws-run2": "wafer.space GF180MCU run 2 (G802)"}
# Progress monitor and probe written for one session of the layout pass; not part of the method.
UNPUBLISHED_TOOLS = ("analysis_progress.sh", "layout_probe.py")


def audit_section(run):
    """The table for one run out of the combined AUDIT.md."""
    lines = (RUNS / "AUDIT.md").read_text().split("\n")
    start = lines.index("## %s" % run) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return [line for line in lines[start:end]]


def unfinished_layout_check(run, code, layout_checked):
    """True when a layout check of the project was started (layout section or renders) but not recorded."""
    if "%s/%s" % (run, code) in layout_checked:
        return False
    src = RUNS / run / code
    started = re.search(r"^## Taped-out layout", (src / "summary.md").read_text(), re.M) is not None
    return started or (src / "images").is_dir()


def write_index(run, projects, audit, out_dir, dig, layout_checked):
    rows = []
    for p in projects:
        key = "%s/%s" % (run, p["code"])
        # The summary that is actually exported: the checkout's copy when the new one is held back.
        src = out_dir / p["code"] if unfinished_layout_check(run, p["code"], layout_checked) else RUNS / key
        text = (src / "summary.md").read_text()
        verdict = re.search(r"^### Verdict: (\w+)", text, re.M).group(1)
        d = dig.get(key)
        if d:
            assert d["verdict"] == verdict, (key, d["verdict"], verdict)
        rows.append((p, verdict, d, audit[p["code"]]))

    checked = sum(1 for p in projects if "%s/%s" % (run, p["code"]) in layout_checked)
    out = ["# %s: project audit" % TITLES[run], "",
           "One directory per public project on this run. Each has an analysis (`summary.md`) of the",
           "project's repository, the manifest row (`project.json`), the commit that was analysed",
           "(`clone.json`) and measurements of the layout extracted from the reticle (`layout.json`).",
           "%d of the %d summaries have also been checked against that taped-out layout and carry" % (
               checked, len(projects)),
           "renders of it (`images/`); they are marked in the \"Layout checked\" column.", "",
           "`tools/` documents how all of this was made. The scripts run in the original workspace,",
           "which also holds the project clones, the reticle layouts and the digest files; they do",
           "not run from this checkout.", "",
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
            "| Code | Project | Slot | Verdict | What it contains | Authors | LICENSE | README | Layout checked | Summary |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for p, verdict, d, a in rows:
        if a["status"] == "cloned":
            lic = ", ".join(sorted({x["spdx"] for x in a["license"]["files"]})) or "none"
            readme = a["readme"]["verdict"]
        else:
            lic = readme = "n/a"
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | [summary](%s/summary.md) |" % (
            p["code"], p["project"].replace("|", "/"), p["slot_size"], verdict,
            d["what"] if d else "No repository listed", d["authors"] if d else "not stated",
            lic, readme, "yes" if "%s/%s" % (run, p["code"]) in layout_checked else "no", p["code"]))
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

    dig, layout_checked = load_digests()
    counts = write_index(run, projects, audit, out_dir, dig, layout_checked)
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
        hold_back = unfinished_layout_check(run, p["code"], layout_checked)
        if hold_back:
            print("WARNING: %s/%s layout check unfinished; keeping the checkout's summary.md and images/"
                  % (run, p["code"]), file=sys.stderr)
        for name in ("project.json", "layout.json") if hold_back else ("summary.md", "project.json", "layout.json"):
            if (src / name).exists():
                shutil.copy2(src / name, dst / name)
                copied += 1
        if (src / "clone_status.json").exists():
            status = json.load((src / "clone_status.json").open())
            for key in ("mirror", "seconds"):  # local paths and timings mean nothing elsewhere
                status.pop(key, None)
            (dst / "clone.json").write_text(json.dumps(status, indent=1) + "\n")
        if not hold_back:
            if (dst / "images").exists():  # replace, or remove renders whose source is gone
                shutil.rmtree(dst / "images")
            if (src / "images").is_dir():
                shutil.copytree(src / "images", dst / "images")

    tools = out_dir / "tools"
    if tools.exists():
        shutil.rmtree(tools)
    shutil.copytree(RUNS / "tools", tools,
                    ignore=shutil.ignore_patterns("__pycache__", ".venv", "*.pyc", *UNPUBLISHED_TOOLS))
    print(run, "projects", len(projects), "files", copied, counts)


if __name__ == "__main__":
    main()

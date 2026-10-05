#!/usr/bin/env python3
"""Audit every cloned project repo: LICENSE file and top-level README.

LICENSE: finds top-level licence files, classifies their text to an SPDX id
and compares with the licence claimed on platform.wafer.space, read from
platform_licenses.csv (columns: RUN,CODE,LICENSE) when that file exists.

README: compares the top-level README against every historical version of
the known project templates' READMEs (taken from the github-backup mirrors)
and flags ones that are missing, tiny, or still essentially the template.

Writes audit.json and AUDIT.md.
"""
import csv
import difflib
import json
import re
import subprocess
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]
BACKUP = Path("/backups/github/github.com")

TEMPLATES = [
    "wafer-space/gf180mcu-project-template",
    "egorxe/gf180mcu-caravel-template",
]

# (spdx id, regex that must match the normalised licence text); first hit wins
LICENSE_SIGNATURES = [
    ("CERN-OHL-S-2.0", r"cern open hardware licence version 2 - strongly reciprocal"),
    ("CERN-OHL-W-2.0", r"cern open hardware licence version 2 - weakly reciprocal"),
    ("CERN-OHL-P-2.0", r"cern open hardware licence version 2 - permissive"),
    ("SHL-2.1", r"solderpad hardware license v2\.1"),
    ("SHL-2.0", r"solderpad hardware license v2\.0"),
    ("Apache-2.0", r"apache license,? version 2\.0"),
    ("AGPL-3.0", r"gnu affero general public license version 3"),
    ("LGPL-3.0", r"gnu lesser general public license version 3"),
    ("LGPL-2.1", r"gnu lesser general public license version 2\.1"),
    ("GPL-3.0", r"gnu general public license version 3"),
    ("GPL-2.0", r"gnu general public license version 2"),
    ("MPL-2.0", r"mozilla public license,? version 2\.0"),
    ("CC0-1.0", r"cc0 1\.0 universal"),
    ("CC-BY-SA-4.0", r"attribution-sharealike 4\.0 international"),
    ("CC-BY-4.0", r"attribution 4\.0 international"),
    ("BSD-3-Clause", r"redistribution and use in source and binary forms.*neither the name"),
    ("BSD-2-Clause", r"redistribution and use in source and binary forms"),
    ("ISC", r"permission to use, copy, modify, and(/or)? distribute this software for any purpose"),
    ("MIT", r"permission is hereby granted, free of charge, to any person obtaining a copy"),
    ("Unlicense", r"this is free and unencumbered software released into the public domain"),
]

LICENSE_NAME = re.compile(r"^(licen[sc]e|copying|unlicense|copyright)([-._].*)?$", re.I)
README_NAME = re.compile(r"^readme(\.(md|rst|txt|markdown|adoc|org))?$", re.I)


def norm(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def classify_license(text):
    n = norm(text)
    # the GNU licences name the version on a separate line from the title
    n = re.sub(r"(gnu (?:affero |lesser )?general public license),? version", r"\1 version", n)
    for spdx, pat in LICENSE_SIGNATURES:
        if re.search(pat, n):
            return spdx
    return "unrecognised"


def template_readmes():
    """Every distinct README blob in the templates' history -> (repo, text)."""
    out = []
    for name in TEMPLATES:
        mirror = BACKUP / (name + ".git")
        if not mirror.is_dir():
            continue
        revs = subprocess.run(["git", "-C", str(mirror), "log", "--all", "--format=%H", "--", "README.md"],
                              capture_output=True, text=True).stdout.split()
        seen = set()
        for rev in revs:
            blob = subprocess.run(["git", "-C", str(mirror), "rev-parse", rev + ":README.md"],
                                  capture_output=True, text=True).stdout.strip()
            if not blob or blob in seen:
                continue
            seen.add(blob)
            text = subprocess.run(["git", "-C", str(mirror), "cat-file", "-p", blob],
                                  capture_output=True, text=True, errors="replace").stdout
            out.append((name, text))
    return out


def readme_check(repo, templates):
    files = sorted(f for f in repo.iterdir() if f.is_file() and README_NAME.match(f.name))
    res = {"files": [f.name for f in files]}
    md = [f for f in files if f.name == "README.md"]
    if not files:
        res.update(verdict="MISSING", note="no top-level README")
        return res
    f = md[0] if md else files[0]
    text = f.read_text(errors="replace")
    words = len(re.findall(r"\w+", re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)", " ", text)))
    best, best_src = 0.0, None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for src, t in templates:
        tl = [l.strip() for l in t.splitlines() if l.strip()]
        ratio = difflib.SequenceMatcher(None, lines, tl, autojunk=False).ratio()
        if ratio > best:
            best, best_src = ratio, src
    # share of this README's lines that appear verbatim in some template version
    tset = {l for _, t in templates for l in (x.strip() for x in t.splitlines()) if l}
    own = [l for l in lines if l not in tset]
    own_words = len(re.findall(r"\w+", " ".join(own)))
    res.update(file=f.name, words=words, own_words=own_words,
               template_similarity=round(best, 2), closest_template=best_src)
    tmpl = "%.0f%% identical to the %s README" % (best * 100, best_src)
    if "To make it easy for you to get started with GitLab" in text:
        res.update(verdict="TEMPLATE", note="GitLab's default new-project README with only the title changed")
    elif not md:
        res.update(verdict="NOT-MD", note="README present but not README.md (%s)" % f.name)
    elif best >= 0.6 and own_words < 40:
        res.update(verdict="TEMPLATE", note="%s; %d words of own text" % (tmpl, own_words))
    elif best >= 0.6 and own_words < 200:
        res.update(verdict="TEMPLATE+NOTE", note="%s plus %d words of own text" % (tmpl, own_words))
    elif words < 40:
        res.update(verdict="STUB", note="only %d words" % words)
    elif words < 120:
        res.update(verdict="THIN", note="original but only %d words" % words)
    elif best >= 0.6:
        res.update(verdict="OK", note="%d words of own text on top of the template README" % own_words)
    else:
        res.update(verdict="OK", note="%d words" % words)
    return res


def license_check(repo, claimed):
    files = sorted(f for f in repo.iterdir() if f.is_file() and LICENSE_NAME.match(f.name))
    found = [{"file": f.name, "spdx": classify_license(f.read_text(errors="replace"))} for f in files]
    lic_dir = repo / "LICENSES"
    if lic_dir.is_dir():
        found += [{"file": "LICENSES/" + f.name, "spdx": f.stem} for f in sorted(lic_dir.iterdir()) if f.is_file()]
    res = {"files": found, "claimed": claimed}
    ids = {x["spdx"] for x in found}
    res["spdx_headers"] = []
    def fam(x):  # GPL-3.0-only / GPL-3.0-or-later / GPL-3.0 are one licence text
        return re.sub(r"-(only|or-later)$", "", x).lower()
    if not found:
        r = subprocess.run(["git", "grep", "-h", "-o", "-I", "-E", r"SPDX-License-Identifier: *[A-Za-z0-9.+-]+", "HEAD"],
                           cwd=repo, capture_output=True, text=True, errors="replace")
        hdr = sorted({l.split(":", 1)[1].strip() for l in r.stdout.splitlines()})
        res["spdx_headers"] = hdr
        res["verdict"] = "MISSING"
        if hdr:
            agree = claimed and fam(claimed) in {fam(h) for h in hdr}
            res["verdict"] += " (SPDX headers in sources: %s%s)" % (
                ", ".join(hdr), "; agrees with claim" if agree else "")
    elif claimed is None:
        res["verdict"] = "PRESENT (claim unknown)"
    elif claimed.lower() == "proprietary":
        res["verdict"] = "MISMATCH (claimed proprietary, repo has an open licence)"
    elif fam(claimed) in {fam(i) for i in ids}:
        res["verdict"] = "MATCH" if len(ids) == 1 else "MATCH (one of several licences in repo)"
    else:
        res["verdict"] = "MISMATCH"
    return res


def main():
    projects = json.load((RUNS / "projects.json").open())
    gh = json.load((RUNS / "github_state.json").open())["repos"]
    claims = {}
    cf = RUNS / "platform_licenses.csv"
    if cf.exists():
        for row in csv.DictReader(cf.open()):
            claims[(row["RUN"], row["CODE"])] = row["LICENSE"].strip() or None
    templates = template_readmes()
    notes = {}
    nf = RUNS / "audit_notes.csv"
    if nf.exists():
        for row in csv.DictReader(nf.open()):
            notes[(row["RUN"], row["CODE"])] = row["NOTE"]
    out = []
    for p in projects:
        d = RUNS / p["run"] / p["code"]
        rec = {"run": p["run"], "code": p["code"], "project": p["project"],
               "repo_url": (p["repo"] or {}).get("url_as_listed"),
               "claimed": claims.get((p["run"], p["code"]))}
        repo = d / "repo"
        if not p["repo"]:
            rec["status"] = "no repository listed"
        elif not (repo / ".git").exists():
            rec["status"] = "clone missing"
        else:
            rec["status"] = "cloned"
            st = json.load((d / "clone_status.json").open())
            rec["head"] = st.get("head", "")[:12]
            rec["branch"] = st.get("branch")
            g = gh.get(p["repo"]["path"]) if p["repo"]["host"] == "github.com" else None
            rec["github_detected_license"] = ((g or {}).get("licenseInfo") or {}).get("spdxId")
            rec["license"] = license_check(repo, claims.get((p["run"], p["code"])))
            rec["readme"] = readme_check(repo, templates)
        rec["note"] = notes.get((p["run"], p["code"]), "")
        out.append(rec)
    json.dump(out, (RUNS / "audit.json").open("w"), indent=1)

    lines = ["# wafer.space run 1 + run 2 repository audit", "",
             "Generated by `tools/audit.py` from the clones under `runs/<run>/<CODE>/repo`.", ""]
    if not claims:
        lines += ["> **Claimed licence not available.** `platform_licenses.csv` is absent, so the",
                  "> LICENSE column only reports what is in the repository, not whether it matches",
                  "> the licence declared on platform.wafer.space.", ""]
    for run in sorted({p["run"] for p in projects}):
        lines += ["## %s" % run, "",
                  "| Code | Project | Repo | Claimed | LICENSE file(s) | LICENSE | README | README note | Other notes |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r in (x for x in out if x["run"] == run):
            if r["status"] != "cloned":
                lines.append("| %s | %s | %s | %s | | n/a | n/a | %s | %s |" % (
                    r["code"], r["project"], r["repo_url"] or "—", r["claimed"] or "?", r["status"], r["note"]))
                continue
            lic, rd = r["license"], r["readme"]
            files = ", ".join("`%s` (%s)" % (x["file"], x["spdx"]) for x in lic["files"]) or "—"
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["code"], r["project"].replace("|", "/"), r["repo_url"], lic["claimed"] or "?",
                files, lic["verdict"], rd["verdict"], rd.get("note", ""), r["note"]))
        lines.append("")
    (RUNS / "AUDIT.md").write_text("\n".join(lines))
    for r in out:
        if r["status"] == "cloned":
            print("%-8s %-5s LICENSE=%-24s %-40s README=%-16s %s" % (
                r["run"], r["code"], r["license"]["verdict"],
                ",".join(x["spdx"] for x in r["license"]["files"])[:40],
                r["readme"]["verdict"], r["readme"].get("note", "")))
        else:
            print("%-8s %-5s %s" % (r["run"], r["code"], r["status"]))


if __name__ == "__main__":
    main()

"""Cheap per-repo file scan for the experiments inventory (no builds)."""
import json, re, subprocess, sys, os, csv
from collections import Counter
RUNS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERRIDE = {("ws-run1","CHES"):"origin/chess", ("ws-run1","OCD1"):"origin/caravel_picorv32",
            ("ws-run2","SCUP"):"origin/dev", ("ws-run1","HZ80"):"origin/halfv_slot_mcu9tv50",
            ("ws-run2","HZ80"):"origin/halfv_slot_mcu9tv50", ("ws-run2","QZ80"):"origin/quarter_slot_mcu9t5v0",
            ("ws-run1","TTPG"):"origin/powergate", ("ws-run1","OCD2"):"e2539ed"}
def git(repo, *a):
    r = subprocess.run(["git","-C",repo,*a], capture_output=True, text=True)
    return r.stdout, r.returncode, r.stderr
def grep(repo, ref, pat, paths=None):
    out, rc, err = git(repo, "grep", "-I", "-l", "-i", "-E", pat, ref, "--", *(paths or ["."]))
    return [l.split(":",1)[1] for l in out.splitlines() if ":" in l]
rows = []
for p in json.load(open(f"{RUNS}/projects.json")):
    run, code = p["run"], p["code"]
    repo = f"{RUNS}/{run}/{code}/repo"
    row = {"run":run, "code":code}
    if not os.path.isdir(repo):
        row["ref"] = ""; rows.append(row); continue
    ref = OVERRIDE.get((run,code), "HEAD")
    out, rc, err = git(repo, "ls-tree", "-r", "--name-only", ref)
    if rc: row["err"] = err.strip(); rows.append(row); continue
    files = out.splitlines()
    ext = Counter(os.path.splitext(f)[1].lower() for f in files)
    low = [f.lower() for f in files]
    row["ref"] = ref
    row["nfiles"] = len(files)
    row["ext"] = {e: ext[e] for e in [".v",".sv",".vhd",".vhdl",".py",".sch",".sym",".spice",".spi",".cir",".sp",".mag",".gds",".oas",".lef",".lib",".def",".yaml",".json",".tcl",".scala"] if ext[e]}
    row["gz_gds"] = sum(1 for f in low if f.endswith((".gds.gz",".gds.xz",".oas.gz")))
    row["librelane"] = bool(grep(repo, ref, r"librelane", ["*Makefile*","*.yaml","*.json","*.nix","*.md","*.toml","*.py","*.tcl"]))
    row["openlane"] = bool(grep(repo, ref, r"openlane", ["*Makefile*","*.yaml","*.json","*.md","*.tcl","*.nix"]))
    row["caravel"] = bool(grep(repo, ref, r"caravel", ["*Makefile*","*.yaml","*.json","*.v","*.md"]))
    row["tt"] = any("tt_um_" in f for f in low) or bool(grep(repo, ref, r"tinytapeout|tt_um_", ["*.yaml","*.md"]))
    row["fabulous"] = bool(grep(repo, ref, r"fabulous", ["*.md","*.yaml","*.py","*.csv"]))
    row["featherlane"] = bool(grep(repo, ref, r"featherlane", ["*.md","*.py","*Makefile*"]))
    row["glayout"] = bool(grep(repo, ref, r"glayout|gdsfactory", ["*.py"]))
    row["klayout_py"] = bool(grep(repo, ref, r"import (klayout|pya)\b|klayout\.db", ["*.py"]))
    row["amaranth"] = bool(grep(repo, ref, r"from amaranth|import amaranth|chisel3|spinalhdl", ["*.py","*.scala"]))
    row["cocotb"] = len(grep(repo, ref, r"import cocotb|from cocotb", ["*.py"]))
    row["spice_tb"] = len(grep(repo, ref, r"^\s*\.(control|tran|dc|ac|meas)\b", ["*.spice","*.spi","*.cir","*.sp","*.net","*.sch"]))
    row["sv_tb"] = len([f for f in low if re.search(r"(^|/)(tb_|test_|.*_tb\.)[^/]*\.(s?v|vhdl?)$", f)])
    row["verilator"] = bool(grep(repo, ref, r"verilator", ["*Makefile*","*.mk","*.sh"]))
    row["sby_formal"] = sum(1 for f in low if f.endswith(".sby"))
    row["ci"] = sorted({f.split("/")[2] for f in files if f.startswith(".github/workflows/")})
    row["drc_lvs_reports"] = sum(1 for f in low if re.search(r"(drc|lvs).*\.(rpt|log|lyrdb|xml|txt)$", f))
    row["nix"] = any(f in ("flake.nix","shell.nix") for f in files)
    rows.append(row)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
print("wrote", len(rows))

#!/usr/bin/env python3
"""Inventory every test asset in the run 1 / run 2 design repos, without running anything.

    test_inventory.py <out.csv>

Reads each design commit with `git ls-tree` / `git cat-file` (no checkout), plus the checked-out
submodules of the clone. One CSV row per test asset: SPICE and xschem testbenches, cocotb tests,
HDL testbenches, formal checks, gate-level simulation setup, Liberty files, silicon data and
bring-up material, CI workflows.
"""
import csv
import difflib
import json
import os
import re
import subprocess
import sys
from collections import Counter

RUNS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Mirror of the wafer.space project template (github-backup layout); override with $TEMPLATE_REPO.
TEMPLATE = os.environ.get("TEMPLATE_REPO", "/backups/github/github.com/wafer-space/gf180mcu-project-template.git")
# Commit the design was built from, where it is not the clone's HEAD (see runs/audit_notes.csv).
OVERRIDE = {("ws-run1", "CHES"): "origin/chess", ("ws-run1", "OCD1"): "origin/caravel_picorv32",
            ("ws-run2", "SCUP"): "origin/dev", ("ws-run1", "HZ80"): "origin/halfv_slot_mcu9tv50",
            ("ws-run2", "HZ80"): "origin/halfv_slot_mcu9tv50", ("ws-run2", "QZ80"): "origin/quarter_slot_mcu9t5v0",
            ("ws-run1", "TTPG"): "origin/powergate", ("ws-run1", "OCD2"): "e2539ed"}
MAX_BYTES = 4_000_000

SPICE_EXT = (".spice", ".spi", ".cir", ".sp", ".net", ".ngspice", ".xyce")
HDL_EXT = (".v", ".sv", ".vhd", ".vhdl")
ANALYSES = ["op", "dc", "ac", "tran", "noise", "pz", "sens", "tf", "disto", "pss", "hb", "four"]
RE_ANALYSIS = re.compile(r"^\s*\.?(%s)\b" % "|".join(ANALYSES), re.I | re.M)
RE_DOT_ANALYSIS = re.compile(r"(?:^|\n|\")\s*\.(%s)\b" % "|".join(ANALYSES), re.I)
RE_CONTROL_ANALYSIS = re.compile(r"^\s*(%s)\s" % "|".join(ANALYSES), re.I | re.M)
RE_MEAS = re.compile(r"^\s*\.?meas(?:ure)?\s+\w+\s+(\w+)", re.I | re.M)
RE_INCLUDE = re.compile(r"^\s*\.(lib|include|inc)\s+(\S+)(?:\s+(\w+))?", re.I | re.M)
RE_XSCHEM_SYM = re.compile(r"^C \{([^}]+?)\.sym\}", re.M)
# GF180MCU primitive devices, as used in netlists and xschem symbol names.
DEVICE_PATTERNS = {
    "nfet_03v3": r"\bnfet_03v3(?:_dss)?\b", "pfet_03v3": r"\bpfet_03v3(?:_dss)?\b",
    "nfet_05v0": r"\bnfet_05v0(?:_dss)?\b", "pfet_05v0": r"\bpfet_05v0(?:_dss)?\b",
    "nfet_06v0": r"\bnfet_06v0(?:_dss)?\b", "pfet_06v0": r"\bpfet_06v0(?:_dss)?\b",
    "nfet_06v0_nvt": r"\bnfet_06v0_nvt\b",
    "cap_mim": r"\bcap_mim_\w+", "cap_mos": r"\bcap_[np]mos_\w+",
    "ppolyf_u_1k": r"\bppolyf_u_1k(?:_6p0)?\b", "ppolyf_u_2k/3k": r"\bppolyf_u_[23]k(?:_6p0)?\b",
    "ppolyf_u": r"\bppolyf_u\b", "npolyf_u": r"\bnpolyf_u\b", "ppolyf_s": r"\bppolyf_s\b", "npolyf_s": r"\bnpolyf_s\b",
    "diff_res": r"\b[np]plus_[us]\b|\bnwell\b(?=\s*[\s(])", "metal_res": r"\brm[1-5t]\b",
    "npn_vertical(DNWELL)": r"\bvnpn_\w+|\bnpn_\d\dp\d\dx\d\dp\d\d\b", "pnp_vertical": r"\bvpnp_\w+|\bpnp_\d\dp\d\dx\d\dp\d\d\b",
    "dnwell_diode": r"\bdnwp[ws]\w*|\bnw_dw\w*|\bnp_\dp\d_dw\b|\bpn_\dp\d_dw\b",
    "diode": r"\b(?:np|pn)_[36]p[03]\b|\bdiode_[np]d2[np]w\w*",
    "schottky": r"\bsc_diode\b|\bschottky\w*", "efuse": r"\befuse\w*",
}
DEVICE_RE = {k: re.compile(v, re.I) for k, v in DEVICE_PATTERNS.items()}
# Device groups the experiments change.
CHANGED = {"MIM": ["cap_mim"], "HRES": ["ppolyf_u_1k", "ppolyf_u_2k/3k"],
           "DNWELL": ["npn_vertical(DNWELL)", "dnwell_diode"], "3V3": ["nfet_03v3", "pfet_03v3"]}
SILICON_PATH = re.compile(r"(^|/)(measure\w*|measurements?|bring[-_]?up\w*|silicon\w*|lab[-_]?\w*|"
                          r"characteri[sz]\w*|test[-_]?results?|chip[-_]?test\w*|board\w*|pcb\w*|firmware|fw)(/|$|\.)", re.I)
VENDORED = re.compile(r"libs\.tech|libs\.ref|(^|/)pdk/|gf180mcu[A-D]/", re.I)
SILICON_NOISE = re.compile(r"embench|riscv-formal|datasheet|^ip/|^librelane/|/fpga/|^fpga/|hdl/riscboy/board/|gerber|/bom\.", re.I)
SILICON_TEXT = re.compile(r"measured (on|in|from) (the )?(silicon|chip|die)|silicon (results?|measurements?|bring.?up|validation)|"
                          r"first silicon|bring.?up (results?|report|status)|measurement results?|chips? (arrived|came back)|"
                          r"tested (on|in) silicon|working silicon", re.I)
DATA_EXT = (".csv", ".tsv", ".ipynb", ".dat", ".xlsx", ".npz", ".h5", ".json", ".txt", ".png", ".pdf", ".py", ".c", ".md")


class Repo:
    def __init__(self, path, ref):
        self.path, self.ref = path, ref
        self.proc = subprocess.Popen(["git", "-C", path, "cat-file", "--batch"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)

    def files(self):
        r = subprocess.run(["git", "-C", self.path, "ls-tree", "-r", "-l", self.ref], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr)
        out = []
        for line in r.stdout.splitlines():
            meta, name = line.split("\t", 1)
            mode, typ, sha, size = meta.split()
            if typ == "blob":
                out.append((name, sha, int(size)))
        return out

    def read(self, sha):
        self.proc.stdin.write((sha + "\n").encode())
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().split()
        size = int(header[2])
        data = self.proc.stdout.read(size)
        self.proc.stdout.read(1)
        return data.decode("utf-8", "replace")

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def template_blobs():
    """All historical versions of the template's cocotb testbench, for stub detection."""
    texts = []
    r = subprocess.run(["git", "-C", TEMPLATE, "log", "--all", "--format=%H", "--", "cocotb/chip_top_tb.py"],
                       capture_output=True, text=True)
    for commit in r.stdout.split():
        s = subprocess.run(["git", "-C", TEMPLATE, "show", "%s:cocotb/chip_top_tb.py" % commit],
                           capture_output=True, text=True)
        if s.returncode == 0:
            texts.append(s.stdout)
    return texts


def devices_in(text):
    return {k for k, rx in DEVICE_RE.items() if rx.search(text)}


def changed_flags(devs, extra=()):
    flags = [g for g, keys in CHANGED.items() if any(k in devs for k in keys)]
    return sorted(set(flags) | set(extra))


def spice_info(text):
    an = Counter(m.group(1).lower() for m in RE_DOT_ANALYSIS.finditer("\n" + text))
    if re.search(r"^\s*\.control\b", text, re.I | re.M) or "code_shown" in text or "code.sym" in text:
        an.update(m.group(1).lower() for m in RE_CONTROL_ANALYSIS.finditer(text))
    stat = []
    if re.search(r"agauss|aunif|\bgauss\(|\bunif\(|monte.?carlo|mc_runs|setseed|\.lib\s+\S+\s+(statistical|mc_\w+)", text, re.I):
        stat.append("MC/statistical")
    corners = sorted({c.lower() for c in re.findall(r"\.lib\s+\S+\s+(typical|ff|ss|fs|sf|fnfp|snsp|fnsp|snfp|"
                                                    r"res_typical|res_ff|res_ss|mimcap_\w+|bjt_\w+|moscap_\w+|"
                                                    r"diode_\w+|statistical|mc_\w+)\b", text, re.I)})
    if re.search(r"\b(foreach|repeat|alter|\.step|\.data|dowhile|while)\b", text, re.I):
        stat.append("sweep/loop")
    if re.search(r"\btemp\b|\.temp\b|set\s+temp", text, re.I):
        stat.append("temperature")
    meas = sorted({m.group(1) for m in RE_MEAS.finditer(text)})
    sim = []
    if re.search(r"xyce|\.print\s+tran\s+format|\.options\s+timeint", text, re.I):
        sim.append("Xyce")
    if re.search(r"\.control\b|ngspice|\bwrdata\b|\bplot\b|\bmeas\b", text, re.I) or not sim:
        sim.append("ngspice")
    if re.search(r"\b(PASS|FAIL)(ED)?\b|\bassert\b|\bif\s*\(?.*(>|<)", text):
        criteria = "pass/fail logic"
    elif meas:
        criteria = "measures only"
    else:
        criteria = "plot/print only"
    models = []
    for kind, path, section in (m.groups() for m in RE_INCLUDE.finditer(text)):
        base = os.path.basename(path.strip("'\""))
        if re.search(r"sm141064|design\.ngspice|design\.xyce|gf180|\.lib\.spice|ngspice", path, re.I):
            models.append(base + (":" + section if section else ""))
    pdk = sorted(set(re.findall(r"gf180mcu[A-D]\b", text)))
    pdk += sorted(set(re.findall(r"open_pdks[-_/]?([0-9a-f]{7,40}|\d+\.\d+\.\d+)", text)))
    return {"analyses": ",".join(sorted(an)), "variation": ",".join(sorted(set(stat + corners))),
            "measures": ",".join(meas[:12]) + ("..." if len(meas) > 12 else ""), "criteria": criteria,
            "simulator": "+".join(sim), "models": ",".join(sorted(set(models)))[:200], "pdk": ",".join(pdk)}


def hdl_tb_info(text):
    self_check = bool(re.search(r"\$error|\$fatal|\bassert\b|\bPASS(ED)?\b|\bFAIL(ED)?\b|mismatch|report\s+\"", text, re.I))
    return "self-checking" if self_check else "stimulus/waveform only"


def scan(run, code, ref, template_texts, std_libs):
    repo_path = f"{RUNS}/{run}/{code}/repo"
    rows = []
    sources = [(repo_path, ref, "")]
    # Submodules as checked out at the clone's HEAD (only meaningful when ref is HEAD).
    sm = subprocess.run(["git", "-C", repo_path, "submodule", "status", "--recursive"], capture_output=True, text=True)
    for line in sm.stdout.splitlines():
        parts = line[1:].split()
        if len(parts) >= 2 and os.path.isdir(os.path.join(repo_path, parts[1])) and line[0] != "-":
            sources.append((os.path.join(repo_path, parts[1]), "HEAD", parts[1] + "/"))
    design_3v3 = "mcu7t3v3" in std_libs
    for root, r, prefix in sources:
        repo = Repo(root, r)
        try:
            files = repo.files()
        except RuntimeError as e:
            rows.append({"path": prefix, "asset": "error", "notes": str(e).strip()[:200]})
            continue
        names = {n for n, _, _ in files}
        by_base = {}
        for n, sha, size in files:
            by_base.setdefault(os.path.basename(n), []).append((n, sha, size))
        cache = {}

        def text_of(sha, size):
            if size > MAX_BYTES:
                return ""
            if sha not in cache:
                cache[sha] = repo.read(sha)
            return cache[sha]

        def hier_devices(n, sha, size, depth=0, seen=None):
            """Devices in this file plus in local xschem children / included netlists."""
            seen = seen if seen is not None else set()
            if n in seen or depth > 10:
                return set()
            seen.add(n)
            t = text_of(sha, size)
            devs = devices_in(t)
            children = []
            if n.endswith(".sch"):
                for sym in RE_XSCHEM_SYM.findall(t):
                    children += by_base.get(os.path.basename(sym) + ".sch", [])
            else:
                for _, path, _ in (m.groups() for m in RE_INCLUDE.finditer(t)):
                    b = os.path.basename(path.strip("'\""))
                    if not re.search(r"sm141064|design\.ngspice", b):
                        children += by_base.get(b, [])
            for cn, csha, csize in children[:40]:
                devs |= hier_devices(cn, csha, csize, depth + 1, seen)
            return devs

        for n, sha, size in files:
            low = n.lower()
            path = prefix + n
            base = os.path.basename(low)
            row = None
            if low.endswith(SPICE_EXT) or low.endswith(".sch"):
                t = text_of(sha, size)
                if not t:
                    continue
                if low.endswith(".sch"):
                    is_tb = bool(RE_DOT_ANALYSIS.search("\n" + t) or re.search(r"^\s*\.control\b", t, re.I | re.M))
                else:
                    is_tb = bool(RE_DOT_ANALYSIS.search("\n" + t) or re.search(r"^\s*\.control\b", t, re.I | re.M))
                if not is_tb:
                    continue
                info = spice_info(t)
                devs = hier_devices(n, sha, size)
                kind = "xschem-tb" if low.endswith(".sch") else "spice-tb"
                if VENDORED.search(path):
                    kind = "vendored PDK " + kind
                flags = ",".join(changed_flags(devs))
                if re.search(r"sky130", info["models"] + path, re.I):
                    kind += " (sky130, not GF180)"
                    info["pdk"] = "sky130"
                    devs, flags = set(), ""
                row = {"asset": kind, **info, "devices": ",".join(sorted(devs)), "changed_devices": flags}
            elif low.endswith(".py"):
                t = text_of(sha, size)
                if not re.search(r"import cocotb|from cocotb", t):
                    continue
                ntests = len(re.findall(r"@cocotb\.test", t))
                nassert = len(re.findall(r"\bassert\b", t))
                best = max((difflib.SequenceMatcher(None, t, tt).quick_ratio() for tt in template_texts), default=0)
                if best >= 0.95:
                    kind = "template stub (unchanged)"
                elif best >= 0.75:
                    kind = "template stub (lightly edited)"
                elif base == "chip_top_tb.py":
                    kind = "template file, rewritten"
                else:
                    kind = "own test"
                gl = bool(re.search(r"\bGL\b|gate.?level|\.nl\.v|\.pnl\.v|sdf", t, re.I))
                row = {"asset": "cocotb", "simulator": "cocotb", "criteria": "%d asserts" % nassert,
                       "analyses": "%d @cocotb.test" % ntests, "variation": "GL option" if gl else "",
                       "stub": kind, "changed_devices": "3V3(cells)" if design_3v3 else ""}
            elif low.endswith(HDL_EXT) and re.search(r"(^|/)(tb|test|tests|testbench|sim)(/|_)|_tb\.|_test\.|^tb", low):
                t = text_of(sha, size)
                if not t or re.search(r"\bmodule\b", t) is None and not low.endswith((".vhd", ".vhdl")):
                    continue
                if not re.search(r"initial|\$finish|wait for|process", t):
                    continue
                gl = bool(re.search(r"\$sdf_annotate|`ifdef\s+GL|USE_POWER_PINS|gl_", t))
                row = {"asset": "hdl-tb", "criteria": hdl_tb_info(t), "variation": "GL/SDF" if gl else "",
                       "simulator": "VHDL" if low.endswith((".vhd", ".vhdl")) else "Verilog/SV",
                       "changed_devices": "3V3(cells)" if design_3v3 else ""}
            elif low.endswith(".sby") or (low.endswith((".sv", ".v")) and "formal" in low):
                row = {"asset": "formal", "simulator": "SymbiYosys" if low.endswith(".sby") else "",
                       "criteria": "formal properties"}
            elif low.endswith(".sdf") or low.endswith(".sdf.gz") or re.search(r"\.(nl|pnl)\.v(\.gz)?$", low):
                row = {"asset": "gl-netlist/sdf", "notes": "%d bytes" % size}
            elif low.endswith(".lib") or low.endswith(".lib.gz"):
                t = text_of(sha, size) if low.endswith(".lib") else ""
                if low.endswith(".lib") and not re.search(r"^\s*library\s*\(", t, re.M):
                    continue
                lib = re.search(r"library\s*\(\s*\"?([\w.-]+)", t)
                corner = re.search(r"(tt|ff|ss|typ|fast|slow)\w*", base)
                libname = lib.group(1) if lib else base
                ncells = len(re.findall(r"^\s*cell\s*\(", t, re.M))
                if VENDORED.search(path) or re.search(r"gf180mcu_(fd|as|ocd)_(sc|ip|io)", libname + " " + low):
                    lkind = "library liberty (vendored)"
                elif ncells <= 1:
                    lkind = "macro timing model (flow output)"
                else:
                    lkind = "custom cell library liberty"
                row = {"asset": "liberty", "stub": lkind, "notes": "%s, %d cells" % (libname, ncells),
                       "variation": corner.group(0) if corner else ""}
            elif low.startswith(".github/workflows/"):
                t = text_of(sha, size)
                steps = sorted(set(re.findall(r"(make\s+[\w-]+|cocotb|librelane|precheck|ngspice|xyce|verilator|"
                                              r"iverilog|klayout|magic|pytest|sby)", t, re.I)))
                row = {"asset": "ci", "notes": ",".join(steps)[:200]}
            elif SILICON_PATH.search(path.lower()) and low.endswith(DATA_EXT) and not SILICON_NOISE.search(path.lower()):
                row = {"asset": "silicon/bring-up (by path)", "notes": "%d bytes" % size}
            elif low.endswith((".md", ".txt", ".rst", "readme")) and size < MAX_BYTES and not VENDORED.search(path):
                t = text_of(sha, size)
                m = SILICON_TEXT.search(t)
                if m:
                    row = {"asset": "silicon/bring-up (by text)", "notes": t[max(0, m.start() - 60):m.end() + 80].replace("\n", " ")}
            if row:
                row["path"] = path
                rows.append(row)
        repo.close()
    return rows


def main():
    out = sys.argv[1]
    template_texts = template_blobs()
    fields = ["run", "code", "design_ref", "asset", "path", "simulator", "analyses", "variation", "measures",
              "criteria", "stub", "models", "pdk", "devices", "changed_devices", "notes"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for p in json.load(open(f"{RUNS}/projects.json")):
            run, code = p["run"], p["code"]
            if not os.path.isdir(f"{RUNS}/{run}/{code}/repo"):
                print(run, code, "no repo", flush=True)
                continue
            ref = OVERRIDE.get((run, code), "HEAD")
            lj = json.load(open(f"{RUNS}/{run}/{code}/layout.json"))
            libs = {c["library"] for c in lj["standard_cells"] if c["kind"] == "logic"}
            rows = scan(run, code, ref, template_texts, libs)
            for r in rows:
                w.writerow({"run": run, "code": code, "design_ref": ref, **{k: r.get(k, "") for k in fields[3:]}})
            print(run, code, ref, len(rows), Counter(r["asset"] for r in rows), flush=True)


if __name__ == "__main__":
    main()

"""Build the experiments inventory CSV from the runs audit data plus hand classification."""
import csv, json, os, sys
RUNS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = "LibreLane (wafer.space gf180mcu-project-template, Nix)"
TT = "Tiny Tapeout GF flow (per-tile LibreLane macros prebuilt as .oas, assembled by TT tooling)"
OCD = "Magic + Open Circuit Design scripts (Caravel openframe style), not LibreLane"
# code -> (kind, flow, sources, reproducible, note)
M = {
 "ws-run1/2975": ("digital", T, "RTL (VHDL/SV) + config", "likely", "RO-PUF macros are hand-placed std cells"),
 "ws-run1/AS03": ("mixed", T+" + xschem/Magic DACs", "RTL + config + DAC schematics/layout", "partial", "custom Avalon DFF cells and asig_5p0_fixed pad; no final GDS in repo"),
 "ws-run1/BRWN": ("unknown (small digital + 7 analog pads)", "unknown", "GDS-only (layout from reticle)", "no", "no repository; unverified lead github.com/Evansika959/FA25_engn2912e_class_tapeout_top"),
 "ws-run1/BTAP": ("digital", T, "RTL + config", "likely", "28 foundry SRAMs"),
 "ws-run1/CAFE": ("digital", T, "RTL + config", "partial", "macro outputs not committed"),
 "ws-run1/CHES": ("digital", T, "RTL + config (branch chess)", "likely", "default branch is the bare template"),
 "ws-run1/GD02": ("digital", T, "RTL + config (branch develop)", "likely", ""),
 "ws-run1/GD03": ("digital", T, "RTL + config (branch develop)", "likely", ""),
 "ws-run1/GD04": ("digital", T+" + Difetto scan insertion", "RTL + config (branch develop)", "partial", "needs Difetto DFT tool"),
 "ws-run1/HZ80": ("digital", T, "RTL + config (branch halfv_slot_mcu9tv50)", "likely", "slot branch inferred"),
 "ws-run1/ISHI": ("analog (full custom)", "hand-assembled full-custom layout (KLayout/Magic); per-cell GDS", "per-circuit GDS + LibreLane run JSON; no schematics", "no (manual layout)", "re-targeting means re-layout; 3 op-amps lost Dualgate at integration"),
 "ws-run1/JKU1": ("digital", T, "RTL + config", "likely", "LICENSE changed to SHL-2.1 after tape-out"),
 "ws-run1/JKU2": ("digital", T, "RTL + config", "likely", "digital half of an ADC only"),
 "ws-run1/KIAN": ("digital", T, "RTL + config", "likely", "21 foundry SRAMs"),
 "ws-run1/MOLE": ("digital", "FABulous eFPGA + "+T, "RTL + tile macros + config", "partial", "tape-out GDS only in release"),
 "ws-run1/MOS2": ("analog (full custom)", "xschem + Magic/KLayout (+gLayout) manual, Chipathon 2025 shared die", "schematics, SPICE, GDS (branch update-for-ws)", "no (manual layout)", "six teams' blocks; MIM users"),
 "ws-run1/MOSB": ("digital (9-track)", "unknown", "GDS-only (layout from reticle)", "no", "no repository; unverified lead github.com/mosbiuschip"),
 "ws-run1/OCD1": ("mixed", OCD, "RTL + Magic layout (branch caravel_picorv32)", "partial", "no LICENSE on that branch; POR + trimmable ring osc"),
 "ws-run1/OCD2": ("mixed (SRAM break-out)", OCD, "Magic layout + SPICE (commit e2539ed)", "partial", "run 1 chip only in git history"),
 "ws-run1/RBOY": ("digital", T, "RTL + config", "likely", "HEAD later than submission"),
 "ws-run1/RZ80": ("digital", T, "RTL + config", "likely", ""),
 "ws-run1/RZML": ("digital", "LibreLane (sources in another repo)", "GDS-only in listed repo", "no (from listed repo)", "sources at github.com/rejunity/ws0-lgn-fxnist (Apache-2.0)"),
 "ws-run1/TQVA": ("digital", T, "RTL + config", "likely", ""),
 "ws-run1/TQVB": ("digital", T, "RTL + config", "likely", "same repo/commit as TQVA"),
 "ws-run1/TQVC": ("digital", T, "RTL + config", "likely", "same repo/commit as TQVA"),
 "ws-run1/TRID": ("analog (full custom test structures)", "xschem + KLayout manual", "schematics + GDS (manufactured GDS hash matches)", "no (manual layout)", "MIM caps, 3.3 V and 6 V single transistors, guarded pads"),
 "ws-run1/TTP2": ("digital (52 TT tiles)", TT, "per-tile Verilog stubs + hardened .oas/.lef", "partial", "tile sources live in each TT project repo"),
 "ws-run1/TTPG": ("digital (52 TT tiles + power gates)", TT, "as TTP2 (branch powergate)", "partial", ""),
 "ws-run1/TZ01": ("mixed", T+" (Caravel-style) + eFuse compiler macros", "RTL + config + macro GDS/LIB", "partial", "no transistor-level eFuse sources in repo"),
 "ws-run1/WSLG": ("digital + artwork", T, "RTL + config", "likely", "custom dynamic DFF"),
 "ws-run2/0000": ("analog (full custom)", "xschem + Magic manual", "schematics, SPICE, Magic, GDS", "no (manual layout)", "floating-gate pFETs, Schottky charge pumps; no LICENSE"),
 "ws-run2/AMM1": ("digital", T, "RTL + config", "likely", ""),
 "ws-run2/AS04": ("mixed", T+" + FeatherLane + xschem/Magic DACs", "RTL + config + DAC sources", "partial", "Avalon 3.3 V library not vendored; pinned PDK commit 404"),
 "ws-run2/AS16": ("digital", T, "RTL + config", "likely", ""),
 "ws-run2/BTX1": ("digital (3.3 V, 19 ocd SRAMs)", "unknown", "GDS-only (layout from reticle)", "no", "no repository"),
 "ws-run2/CAB1": ("mixed", T+" (Caravel-style) + Magic analog macros", "RTL + config + macro GDS", "partial", "flash_ip is a portless blackbox"),
 "ws-run2/CAFE": ("digital", T, "RTL + config", "partial", "nested submodules declared without tree entries"),
 "ws-run2/CLON": ("digital", T, "RTL + config", "likely", ""),
 "ws-run2/DCO0": ("digital (std-cell DCO/TDC)", T+" + ngspice", "RTL + config + SPICE sweeps", "likely", "possible pad mismatch (unverified)"),
 "ws-run2/DPK1": ("digital", T, "RTL + config (branch bio180)", "likely", "licence changed in last commit"),
 "ws-run2/DPK2": ("digital", T, "RTL + config (branch ws2-x8)", "likely", ""),
 "ws-run2/EURO": ("digital + artwork", T, "RTL + config", "likely", ""),
 "ws-run2/FC01": ("unknown (no library cells in layout)", "unknown", "GDS-only (layout from reticle)", "no", "no repository"),
 "ws-run2/FS01": ("mixed (generated SRAM)", T+" + PDKMaster/c4m-flexmem (external, Python)", "generator config only; nothing generated committed", "partial", "needs external c4m repos"),
 "ws-run2/FS02": ("mixed (generated SRAM)", T+" + PDKMaster/c4m-flexmem (external, Python)", "as FS01", "partial", "uses SRAM design rules"),
 "ws-run2/FS03": ("mixed (generated SRAM)", T+" + PDKMaster/c4m-flexmem (external, Python)", "as FS01", "partial", "5 V devices"),
 "ws-run2/GD04": ("digital", T+" + Difetto scan insertion", "same repo/commit as run 1 GD04", "partial", ""),
 "ws-run2/HZ80": ("digital", T, "same as run 1 HZ80", "likely", ""),
 "ws-run2/ISHI": ("analog (full custom)", "hand-assembled full-custom layout", "LibreLane run JSON only; cell layouts from run 1 repo", "no (manual layout)", "same cells as run 1"),
 "ws-run2/KIAN": ("digital", T, "RTL + config", "likely", "3.3 V AS cells + ocd SRAM/IO"),
 "ws-run2/MEME": ("artwork + passive resistor array", "manual (layout only)", "OAS-only", "no", "~192 p+ poly resistors on analog pads"),
 "ws-run2/MOLE": ("digital", "FABulous eFPGA + "+T, "RTL + tile macros + config", "partial", "final views only in release"),
 "ws-run2/NAX1": ("mixed", T+" (Caravel-style) + Magic analog macros", "RTL + config + macro GDS + PEX", "partial", "XTAL driver, pulse-shrinking TDCs"),
 "ws-run2/OCD3": ("mixed (SRAM break-out + POR)", OCD, "Magic layout + xschem + SPICE", "partial", "3.3 V self-biased POR"),
 "ws-run2/PSOC": ("digital", T, "RTL + config + full run checked in", "likely", "repo moved to burnettlab/"),
 "ws-run2/QZ80": ("digital", T, "RTL + config (branch quarter_slot_mcu9t5v0)", "likely", ""),
 "ws-run2/RLCM": ("analog (RF passives)", "manual (GDS only)", "GDS-only", "no", "inductors, transformers, MIM-B caps; no LICENSE"),
 "ws-run2/SALU": ("digital", "Chisel -> "+T, "Chisel + RTL + config", "likely", ""),
 "ws-run2/SCML": ("digital", T, "RTL + config", "likely", "platform says proprietary, repo has an open licence"),
 "ws-run2/SCMT": ("digital", T, "RTL + config", "likely", ""),
 "ws-run2/SCTP": ("digital", T, "RTL + config", "partial", "stale .gitmodules entries"),
 "ws-run2/SCUP": ("digital (+std-cell ADPLLs)", T, "RTL + config (branch dev)", "partial", "ADPLL sources in a submodule"),
 "ws-run2/T0P3": ("mixed (32 TT tiles, 16 analog)", TT, "per-tile stubs + hardened .oas/.lef", "partial", "analog tiles need their own repos (xschem/Magic)"),
 "ws-run2/T26A": ("digital (93 TT tiles, 1 analog)", TT, "per-tile stubs + hardened .oas/.lef", "partial", ""),
 "ws-run2/T26B": ("mixed (88 TT tiles incl. custom SRAM)", TT, "per-tile stubs + hardened .oas/.lef", "partial", ""),
 "ws-run2/TQVA": ("digital", T, "same as run 1 TQVA", "likely", ""),
 "ws-run2/TQVC": ("digital", T, "same as run 1 TQVC", "likely", ""),
 "ws-run2/TQVD": ("mixed (digital + R-2R DAC)", T, "RTL + config + DAC macro", "likely", "setup violation at slow 3.0 V corner"),
 "ws-run2/TQVE": ("digital (3.3 V, 10 ocd SRAMs)", "unknown", "GDS-only (layout from reticle)", "no", "no repository; sibling of TQVD"),
 "ws-run2/WSLG": ("digital + artwork", T, "same as run 1 WSLG", "likely", ""),
}
projects = json.load(open(f"{RUNS}/projects.json"))
audit = {(a["run"], a["code"]): a for a in json.load(open(f"{RUNS}/audit.json"))}
plat = {(r["RUN"], r["CODE"]): r for r in csv.DictReader(open(f"{RUNS}/platform_licenses.csv"))}
scan = {(r["run"], r["code"]): r for r in json.load(open(sys.argv[1]))}
verdict = {}
for f in ["digests.tsv", "digests_layout.tsv"]:
    for line in open(f"{RUNS}/{f}"):
        t = line.rstrip("\n").split("\t")
        if len(t) >= 7:
            verdict[t[0]] = t[1]
rows = []
for p in projects:
    k = (p["run"], p["code"]); key = "/".join(k)
    a, s, j = audit[k], scan[k], json.load(open(f"{RUNS}/{key}/layout.json"))
    pl = plat.get(k, {})
    lic = a.get("license") or {}
    repo_lic = ";".join(sorted({f["spdx"] for f in lic.get("files", [])})) or "none"
    libs = sorted({c["library"] for c in j["standard_cells"] if c["kind"] == "logic"})
    kind, flow, src, rep, note = M[key]
    tests = []
    if s.get("cocotb"): tests.append("cocotb:%d" % s["cocotb"])
    if s.get("spice_tb"): tests.append("spice-analyses:%d" % s["spice_tb"])
    if s.get("sv_tb"): tests.append("hdl-tb:%d" % s["sv_tb"])
    if s.get("ci"): tests.append("CI:" + "+".join(s["ci"]))
    rows.append({
        "run": p["run"], "code": p["code"], "project": p["project"], "slot": p["slot_size"],
        "repo_url": (p.get("repo") or {}).get("url_as_listed", "") or "",
        "design_ref": s.get("ref", ""), "head": a.get("head") or "",
        "licence_platform": pl.get("LICENSE", "") + ("/" + pl["OTHER_SPDX"] if pl.get("OTHER_SPDX") and pl["OTHER_SPDX"] != pl.get("LICENSE") else ""),
        "licence_repo": repo_lic, "licence_check": lic.get("verdict", "no repo"),
        "kind": kind, "flow": flow, "sources": src, "reproducible": rep,
        "stdcell_libs": " ".join(libs) or "none",
        "sram_macros": sum(m["placements"] for m in j["sram_macros"]),
        "io_libs": " ".join(sorted({c["cell"].split("__")[0] for c in j["io_cells"]})) or "none",
        "tests_found": " ".join(tests) or "none",
        "char_verdict": verdict.get(key, "unknown"), "note": note,
    })
out = sys.argv[2]
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote", len(rows), out)

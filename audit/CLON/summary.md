# CLON: Cloneless2 (ws-run2)

| | |
|---|---|
| Repository | https://github.com/ThorbenMoos/Cloneless2 @ a63883b (main, last commit 2026-07-30; release v1 2026-07-27, Zenodo DOI 10.5281/zenodo.21623566) |
| Slot | 1x1 (DIE_AREA 0 0 3932 5122 um) |
| Top cell | chip_top |
| Licence in repo | GPL-3.0 (LICENSE file; no SPDX headers) |
| README | OK (1518 words, own text) |

## What the repo actually contains

Second tapeout in the Cloneless series: same VHDL-to-Verilog (ghdl synth) plus LibreLane flow as Cloneless1, 5 V 7-track stdcells (gf180mcu_fd_sc_mcu7t5v0), 4 MHz clock, wafer.space padring plus a new `trigger_PAD` bidirectional IO cell (chip_top.sv). `ID = G802CLON` in the Makefile, PDK commit d658698, precheck tag 1.7.3. No SRAM, no analog or custom-drawn macros.

Blocks (`src/Cloneless.vhd`):
- mid-pSquare masked block cipher, now with glitch+transition-robust pipelining (formal verification flow referenced from Cloneless_artifacts).
- Two hard-coded shared keys (const_key1, const_key2) for fixed-vs-fixed SCA, plus a third key option with 32 BF-PUF bits mixed in (`mps_ipm_controller.vhd`: 2x bf_puf, 16 bits, 4 parallel, cycles1=5, cycles2=511, factor 7 majority).
- 4x ES-TRNG (RO pairs 11/23, 11/31, 23/47, 23/59) with a buffer-based tapped delay chain (replaces Cloneless1's carry4 emulation).
- Raw-access PUF core: ROPUF1/2 (RO length 11 and 23, windows 127/255 cycles) and BFPUF1/2 (butterfly, cycles1/cycles2 = 5/255 and 10/1023); 8 bits each.
- Trivium PRNG, config/IO registers.

Hardened macros (`macros/`): `butterfly`, `ringoscillator_11/23/31/47/59`, `tappeddelaychain`; instance counts in chip_top.yaml: butterfly x48, ringoscillator_11 x18, _23 x21, _31 x1, _47 x3, _59 x1 (44 ROs), tappeddelaychain x6. Verification as in Cloneless1 (GHDL/iverilog testbenches, gate-level sim, wafer.space precheck). No final GDS in repo (download link, 53 MB zip, not fetched), no silicon results in this repo (Cloneless1 measurement results are summarised in the Cloneless1 README only).

## Authors and affiliations

| Who | Role | Affiliation | Source |
|---|---|---|---|
| Thorben Moos (git "Thorben", ThorbenMoos) | sole author, 13 commits | GitHub bio "Cryptography and Security Researcher", blog thorbenmoos.de; commit email @rub.de (hint only) | git shortlog, `gh api users/ThorbenMoos` |
| PBS Foundation | funding | Project SOVereign | README Acknowledgement |

## Value for GF180MCU characterisation and PDK development

### Verdict: Medium

Contains 48 butterfly (cross-coupled latch) cells and 44 ring oscillators, purpose-described as technology characterisation, readable as raw bits. Digital pins only, and the butterfly design's behaviour is explicitly unverified.

### Test structures and measurable circuits

| Structure | What it exercises | Access | Where |
|---|---|---|---|
| Butterfly PUF cell: two `gf180mcu_fd_sc_mcu7t5v0__latrsnq_1` latches, enable tied high, each latch D fed from the other's Q; `bf_en_n` low sets one latch and resets the other, release lets the loop resolve to a state set by the two latches' relative delay/mismatch (resolution mechanism inferred from `butterfly.vhd`; README says the assumptions are "to be verified in silicon") | Latch-to-latch D to Q delay and drive mismatch (local Vth/L variation), metastability resolution vs settling window (255/1023 cycles) | 2 raw 8-bit BF-PUF slices over data bus (select via config register); 32 further cells inside the key path (not readable) | `src/butterfly.vhd`, `latch.vhd`, `bf_puf_cell.vhd`, `macros/butterfly` |
| RO-PUF: pair of identical ring oscillators (inv_1 chain + nand2_1), 16-bit counters, compare after N cycles | Frequency mismatch of identical rings (inverter delay mismatch) | raw bits via interface, comparison bit only | `src/ro_puf_cell.vhd`, `ro_cnt.vhd`, macros/ringoscillator_* |
| ES-TRNG: RO pair + 4-buffer (buf_1) tapped delay chain sampled by FFs | Jitter and buffer delay resolution | raw TRNG readable | `src/tappeddelaychain.vhd`, `trng.vhd`, macros/tappeddelaychain |

PUF type answer: two PUFs, both digital and built from stock GF180MCU cells only: (1) ring-oscillator PUF, identical to Cloneless1's; (2) butterfly PUF from two latrsnq_1 cells (the Makefile `cell_replacement` target maps VHDL `latch` to latrsnq_1, `buff` to buf_1, `inv` to inv_1, `nand2` to nand2_1, all with `(* keep *)`). Not arbiter, not SRAM, not a custom analog cell, no custom devices.

Placement: macro-level manual placement. Each butterfly cell is a separate hardened macro and chip_top.yaml fixes every instance at explicit coordinates on a grid (`510+75*n` um, matching the 75 um PDN pitch; instances spaced 2-4 grid steps, i.e. 150-300 um apart). Inside each macro the layout is OpenROAD auto place and route (FP_CORE_UTIL 30), so the two latches' placement and routing is automatic and its symmetry is not guaranteed (the README says the "automated routing and placement relies on assumptions regarding low-level cell properties"). All instances are copies of one layout, so cell-to-cell differences are variation, but any systematic latch asymmetry from routing would show as a bias towards 0 or 1 across all cells, which is itself measurable. No SPICE or post-layout simulation comparison data in the repo.

Side-channel/tamper countermeasures depending on layout: masking/transition-robust pipelining are RTL/gate-level; I found no layout shielding or matched routing in the flow config (no shield or dummy-wire options). The new IO `trigger` pin and the second fixed key are for measurement convenience. Tamper-evidence is claimed from delay-based PUFs (RO and butterfly): invasive probing changes delay/loading and so changes key material; to be validated experimentally.

### Candidate PDK additions

Nothing found. The latrsnq_1-based cross-coupled latch could in principle become a characterised "butterfly" test structure, but it uses an existing cell.

### What would be needed to use it

Same as Cloneless1: packaged part on authors' PCB with FPGA controller (Cloneless_artifacts repo, not cloned); raw PUF output is only 8 bits per PUF per run so many repeated measurements and dies are required to get bias and reliability statistics. A SPICE model of the latrsnq_1 loop at 5 V would be needed to relate bias to device mismatch.

## What changed from Cloneless1

- Cipher: now provably glitch+transition-robust probing secure (pipelining of [7], formal verification flow); second redundancy/key set: two fixed keys (const_key1/2) instead of one.
- New PUF family: butterfly PUF (48 macro instances, latrsnq_1) added; RO-PUF tuned (RO lengths 11/23 rather than 23-59, shorter windows) and used raw only; the key PUF is now butterfly instead of RO (2x bf_puf, factor 7).
- ES-TRNG: carry4-emulated tapped delay chain (mux2_1/xor2_1) replaced by a 4-buffer (buf_1) chain, for finer resolution; RO lengths 11/23/31/47/59 (new 11).
- RO macro count dropped from 140 (23x20, 31x19, 47x84, 59x17) to 44; the dominant RO-PUF in the key path went away.
- New `trigger` output IO cell for SCA; padring/template updated to run 2 (shuttle_id, qrcode_id, project_id, marker macros).
- Flow: Cloneless2 README describes 12-13 h full reproduction including precheck.

## Notes and caveats

- GDS not in repo; layout checks and macro symmetry not inspected.
- The README says the butterfly cell's behaviour in silicon is unverified, so the PUF may not function as intended.
- No measured data is in the repo.

# OCD3: 3.3V SRAM test 2 (ws-run2)

| | |
|---|---|
| Repository | https://github.com/RTimothyEdwards/gf180mcu_ocd_sram_test @ 6d4f609 (main, last commit 2026-07-04) |
| Slot | 1x0p5 |
| Top cell | gf180mcu_ocd_sram2_top |
| Licence in repo | No LICENSE file; Apache-2.0 SPDX headers in sources (Open Circuit Design, LLC; some files derived from Efabless Caravel) |
| README | Missing at top level; the documentation is `doc/README` (pinout, build, bench test setup) |

## What the repo actually contains

One repository holds two generations of the same break-out test chip for the 3.3 V SRAM library `gf180mcu_ocd_ip_sram`. Each SRAM macro has its control, address and data pins wired straight to pads, with no logic in between except an 8-bit 2:1 output multiplexer.

**This chip (OCD3, run 2).** Top cell `gf180mcu_ocd_sram2_top`, submitted to G802, and the design at HEAD. Relative to run 1 it swaps the second 256-byte macro for the new `gf180mcu_ocd_ip_sram__sram64x8m8wm1` (address A0-A5 only; shares the Q51-60 output group with the 256-byte macro through pad 69) and replaces the 5 V POR with the new `por_3v3_selfbiased` in `ip/simple_por_3v3_regulated/`, whose enable is driven from the `rst_n` pad and whose `porb` output is on pad 4. It also adds the wafer.space COB alignment markers and project/shuttle code cells. All test results in `doc/README` are from the run-1 chip; the README states the same test setup "should be valid for both versions". No run-2 silicon data is in the repo.

**Which files belong to which chip**

| | Run 1 chip (OCD2, `gf180mcu_ocd_sram_top`) | Run 2 chip (OCD3, `gf180mcu_ocd_sram2_top`) |
|---|---|---|
| Where | git history only; last complete state at commit e2539ed | HEAD (6d4f609) |
| Top layout | `magic/gf180mcu_ocd_sram_top.mag`, `magic/gf180mcu_ocd_sram_test.mag` | `magic/gf180mcu_ocd_sram2_top.mag`, `magic/gf180mcu_ocd_sram_test2.mag` |
| GDS | `gds/gf180mcu_ocd_sram_top.gds.gz`, `gds/gf180mcu_ocd_sram_filled.gds.gz` | `gds/gf180mcu_ocd_sram2_top.gds.gz` (18.6 MB), `gds/gf180mcu_ocd_sram2_filled.gds.gz` (24 MB) |
| Netlist (LVS source) | `verilog/gf180mcu_ocd_sram_test.v` | `verilog/gf180mcu_ocd_sram_test2.v` |
| Extracted netlist | `magic/gf180mcu_ocd_sram_test.spice` | `netlist/layout/gf180mcu_ocd_sram_test2.spice` |
| SRAM macros | `sram1024x8m8wm1`, `sram512x8m8wm1`, 2x `sram256x8m8wm1` | `sram1024x8m8wm1`, `sram512x8m8wm1`, `sram256x8m8wm1`, `sram64x8m8wm1` |
| POR | `ip/simple_por/` (`simple_por`, 5 V devices, powered from DVDD, output through `lvlshift_down`) | `ip/simple_por_3v3_regulated/` (`por_3v3_selfbiased`, 3.3 V devices, powered from VDD) |
| DRC report | `validate/sram_top_drc_klayout.lyrdb` (0 items) | `validate/sram2_top_drc_klayout.lyrdb` (0 items) |
| LVS | `validate/comp.out` at e2539ed: "Circuits match uniquely" | `validate/comp.out` at HEAD: "Circuits match uniquely" |
| wafer.space cells | `magic/wafer_space/gf180mcu_ws_ip__id.mag` | `..._marker`, `..._project_id`, `..._shuttle_id`, `..._qrcode_id` (COB alignment markers, added in 6d4f609) |

The run-1 files were renamed/replaced in commit 1bbbd1b (2026-07-04, "Updating from chip version 1 to chip version 2"). Shared by both and present at HEAD: `verilog/chip_half_frame.v` + `magic/chip_half_frame.mag` (padframe), `verilog/ocd_mux_array.v` + `magic/ocd_mux_array.mag` (8x `gf180mcu_as_sc_mcu7t3v3__mux2_4`, hand placed), `constant_block`, `gf180mcu_ocd_io__fill10x`, `lvlshift_down`, `ip/simple_por/` (still in the tree but not instantiated in the run-2 netlist), `scripts/`, `validate/`, and `doc/` (README, `hashes.txt`, layout picture `gf180mcu_ocd_sram_test.png`, `chip_photo.jpg`, `4bit_count_bench_test.png`).

Build: hand-assembled in magic, no synthesis or P&R flow. `scripts/run_gen_gds.sh` writes GDS from magic, `scripts/run_fill_gds.sh` runs the KLayout fill script, `validate/run_lvs.sh` runs netgen against the PDK SPICE libraries for `gf180mcu_ocd_io`, `gf180mcu_as_sc_mcu7t3v3` and each SRAM macro (full transistor-level comparison since commit 959e10b), `validate/run_drc.sh` runs the KLayout deck.

Padframe (`doc/README`): a wafer.space half-height frame re-drawn with `gf180mcu_ocd_io` cells; every other DVDD/DVSS pair replaced by VDD/VSS (3.3 V) pads; 24 mA drive pads replaced by selectable-drive pads; analog pads unused; each bidirectional pad is hard-programmed as input or output through local loopback constants from `constant_block` inside the 10 um filler cells. Pads are 5 V (DVDD), core 3.3 V (VDD).

Where the library under test lives: nowhere in this repo and there are no submodules. The LVS script reads `${PDK_ROOT}/gf180mcuD/libs.ref/gf180mcu_ocd_ip_sram/spice/*.spice`, so the macros come from the open_pdks installation. The commit log refers to "the SRAM macro repository" / "SRAM library (gf180mcu_ocd_ip_sram)" without a URL.

Silicon data in the repo (all from the run-1 chip): `doc/chip_photo.jpg` (COB bench setup), `doc/4bit_count_bench_test.png` (Digilent WaveForms capture dated 2026-06-30 showing Q[3:0] of a 256-byte macro reading back a 0-15 count; about 16 values per 0.65 us read off the screenshot, i.e. roughly a 25 MHz read rate, my estimate), the bench wiring table in `doc/README`, and the commit message of 1bbbd1b: the first chip "has been tested on silicon" and the original PoR "although functional, has a 14 to 16 second delay period when the chip is operated at a 3.3V external supply".

Not present: SRAM SPICE simulations, timing characterisation data, a working digital testbench (`verilog/README`: "Currently the testbench does not run because 'inout' ports are not allowed to be driven by registers"), or the tester driver code ("will be committed to the repository when it is available").

## Authors and affiliations

| Person / organisation | Role | Affiliation | Source |
|---|---|---|---|
| R. Timothy Edwards (GitHub `RTimothyEdwards`) | Sole committer (12 commits); layout, POR designs, verification, bench test | Open Circuit Design, LLC | git log; "Written by Tim Edwards" headers; "SPDX-FileCopyrightText: 2025 Open Circuit Design, LLC"; GitHub profile company "Open Circuit Design" |
| Efabless Corporation | Origin of padframe/POR concept (caravel-gf180mcu) | Efabless | file headers citing https://github.com/efabless/caravel-gf180mcu/ |
| "rebelmike" | COB breakout board used for testing (https://codeberg.org/rebelmike/ws-breakout) | not stated | `doc/README` |
| Avalon Semiconductor | 3.3 V standard cells used for the mux and POR buffers | not stated | cell names; POR README |

## Value for GF180MCU characterisation and PDK development

### Verdict: High

A purpose-built memory test chip: new 3.3 V SRAM macros with every pin on a pad, plus a power-on-reset test circuit with a pad output, clean LVS/DRC, a documented pinout and bench setup, and (for the run-1 chip) first silicon results.

### Test structures and measurable circuits

| Structure | What it exercises | Access (pad numbers from `doc/README`, counter-clockwise from lower left) | Where |
|---|---|---|---|
| `gf180mcu_ocd_ip_sram__sram1024x8m8wm1`, `__sram512x8m8wm1`, `__sram256x8m8wm1` (both chips); second `__sram256x8m8wm1` (run 1 only); `__sram64x8m8wm1` (run 2 only) | 3.3 V 6T bit-cell read/write margins, minimum operating VDD, data retention voltage, access time (clock to Q), setup/hold on A/D/WEN, per-bit write mask, standby current per macro via CEN | Shared CLK (1), GWEN (3), A0-A7 (14..7), A8 (70), A9 (68), D0-D7 (24..21, 18..15), WEN0-7 (40..37, 34..31), one CEN per macro (27-30), Q on two 8-bit groups (43-50 and 51-54, 57-60), output select inputs 67 and 69 | `verilog/gf180mcu_ocd_sram_test2.v` (run 2), `verilog/gf180mcu_ocd_sram_test.v` at e2539ed (run 1) |
| `ocd_mux_array` x2 | `gf180mcu_as_sc_mcu7t3v3__mux2_4` in the Q path (adds a fixed delay to access-time measurements) | select pads 67, 69 | `verilog/ocd_mux_array.v`, `magic/ocd_mux_array.mag` |
| `gf180mcu_ocd_io` pads | Input pads `__in_c`/`__in_s` and `__bi_a` fixed as input or as high-drive output; 5 V pad ring with 3.3 V core | all signal pads | `verilog/chip_half_frame.v` |
| Run 1 POR: `simple_por` | `nfet_06v0`/`pfet_06v0` cascoded step-down mirrors, `ppolyf_u_1k_6p0` 2000 um and 200 um x 1 um resistors, 9x `cap_mim_2f0_m4m5_noshield` 10x10 um, Schmitt trigger; delay versus DVDD | POR output on pad 4 through `lvlshift_down` (5 V to 3.3 V) | `ip/simple_por/netlist/simple_por.spice`, `*_tb*.spice` |
| Run 2 POR: `por_3v3_selfbiased` | `nfet_03v3`/`pfet_03v3` (L=0.28 um) self-biased amplifier regulating an internal 1.2 V bias, two `ppolyf_u_1k` 2500 um x 1 um resistors, `cap_mim_2f0_m4m5_noshield` 10x10 um m=36 timing cap and m=4 compensation, `diode_nd2ps_03v3` on `ena`, Schmitt inverter, `gf180mcu_as_sc_mcu7t3v3` buffers; spec 40 ms delay at 3.3 V, 20 ms at 1.8 V | `porb` on pad 4; `ena` from the `rst_n` pad (2), which has a pull-up | `ip/simple_por_3v3_regulated/` (xschem `.sch`, magic, schematic and extracted netlists, LVS output) |

Simulation data for comparison: POR testbench decks only (`ip/simple_por/netlist/*_tb*.spice`, `ip/simple_por_3v3_regulated/xschem/simple_por_tb.sch`, `simple_por_tb2.sch`, `schmitt_tb.sch`); no stored waveforms or numbers apart from the specifications quoted in `ip/simple_por_3v3_regulated/doc/README`. No SRAM simulation data in this repo; `.lib` timing for the macros is in the PDK install.

Functional notes from `doc/README` that a tester needs: CEN must be high at power-on and then driven low; a write is a CLK pulse with GWEN low; reading needs a further CLK pulse with GWEN high; "can also test the core at 1.8V".

### Candidate PDK additions

- `gf180mcu_ocd_ip_sram` macros at 64, 256, 512 and 1024 bytes x 8 bit, 3.3 V. The 1024-byte macro was created during this project (commit 6667b43: "the circuitry exists for a 10-bit address, so I created a 1kB SRAM macro and added it to the library"); the 64-byte macro was added for run 2 so that it "(possibly?) barely fits in a single Tiny Tapeout slot".
- `por_3v3_selfbiased`: a complete 3.3 V POR macro (GDS, LEF, xschem, magic, LVS-clean netlists) with documented limits (not 5 V tolerant; trips at about 1.5 V on supplies slower than 0.1 s; could be improved with a bandgap reference).
- `simple_por`: 5 V POR macro, now with a silicon data point (14-16 s delay when run from 3.3 V).
- `gf180mcu_ocd_io` dual-voltage padframe and the loopback-constant filler cell `gf180mcu_ocd_io__fill10x`.
- PDK/library issues recorded in commit messages: antenna violations on SRAM macro inputs fixed by adding tie-down diodes to the macros (6667b43); DRC rule PP.8 (minimum enclosed area) violated in the SRAM core (b63e370); IO corner cell shorting DVSS and VSS in LVS (46f8f5f); case mismatch of VDD/VSS labels in the SRAM library (959e10b); a KLayout DRC rule giving false positives on the wafer.space project/shuttle code text, "needs to be fixed but is not a blocker" (6d4f609); and the 12-item magic/PDK device-generator list in `ip/simple_por/mag/README` (ppolyf and MiM models and rules).

### What would be needed to use it

Chip-on-board or packaged parts on the wafer.space COB breakout (70-pin mezzanine; mapping table in `doc/README`). Supplies: 5 V (DVDD) and 3.3 V (VDD); the author also ran the pad ring at 3.3 V to match a 3.3 V logic analyser. Equipment: pattern generator / logic analyser (one Digilent Analog Discovery 2 covers 4 data and 6 address bits; full coverage needs two, or an FPGA board), variable core supply and a source-meter for retention and standby current, oscilloscope for POR timing. Missing: tester scripts, a shmoo or march-test plan, expected timing numbers, and the SRAM library sources themselves.

## Notes and caveats

- OCD2 and OCD3 point at the same repository and commit. HEAD contains only the run-2 chip; the run-1 chip has to be checked out from history (e2539ed or earlier).
- Run 1 has two candidate GDS files: the December 2025 one (uncompressed sha256 `7e63cafc...`, commits 739641d to 29708bd, where the log says the GDS "is still the GDS that was taped out") and a 2026-01-02 rebuild with the mask-level PP.8 fix (`94ad68c5...`, commit b63e370). The repo does not say whether the January file replaced the submission. The platform sha256 for OCD2 (`ed49ce0e...`) matches neither.
- Run 2: uncompressed `gds/gf180mcu_ocd_sram2_filled.gds.gz` hashes to `e6310800...`, matching `doc/hashes.txt`, but not the platform sha256 (`ade917d9...`; the platform file is an `.oas`, so a re-export is likely, inferred).
- The run-1 `doc/README` text for select pins 67/69 ("512 byte 1 or 2") was stale relative to the run-1 netlist, which has one 1024-byte and one 512-byte macro on that mux.
- The behavioural model `ip/simple_por_3v3_regulated/verilog/por_3v3_selfbiased.v` has ports `por, porb, porb_u` and no `ena`, while the schematic and the chip netlist use `ena, por, porb, por_unbuf`. The directory is named `simple_por_3v3_regulated` and also holds an unused `por_3v3_regulated.sch`.
- `ip/simple_por_3v3_regulated/validate/sram_top_drc_klayout.lyrdb` (block-level DRC) contains 3 items; I did not decode them. The chip-level report has none.
- The upstream location of `gf180mcu_ocd_ip_sram`, `gf180mcu_ocd_io` and `gf180mcu_as_sc_mcu7t3v3` is not given; versions are those in the author's `/usr/share/pdk/gf180mcuD`.

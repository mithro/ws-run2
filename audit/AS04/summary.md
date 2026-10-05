# AS04: AS04 Multi-Project die using 3.3V SCL (ws-run2)

| | |
|---|---|
| Repository | https://github.com/AvalonSemiconductors/ws-submission-2026 @ a8d7552 (main, last commit 2026-08-16; "Final version" 6705fd8 2026-07-15) |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 (LICENSE) |
| README | THIN (49 words; docs in docs/source/, site avalonsemiconductors.github.io/WS2026) |

## What the repo actually contains

Successor to AS03 on the Avalon 3.3 V library. Makefile: SCL=`gf180mcu_as_sc_mcu7t3v3`, PAD=`gf180mcu_ocd_io` (level-shifting pads; VDD 3.3 V +/-10 %, DVDD separate), SRAM option `gf180mcu_ocd_ip_sram`, PDK via ciel, PDK_COMMIT d658698 (wafer-space gf180mcu fork, `--include-libraries all`). 5-bit `design_sel` mux, 46 bidir pads and 4 analog pads in 1x1. The library is not vendored (only a spice copy, `macros/Analog/r2r_dac/gf180mcu_as_sc_mcu7t3v3.spice`, 74 subckts: and/ao/aoi/buff/clkbuff/dfsrtp/dfxtn/dfxtp/dlybuff/fill/hcf_7/inv/invz/maj3/mux2/nand/nor/xor/tap...).

Sub-designs (address from `docs/source/multiplexer.rst`):

- 00000/00001 6502 core (6510/6502 pinout), macro AS65x.
- 00010/00011 RV32IMA (6510/6502 pinout), macro 65RV32.
- 00100 C64 PLA replica (C64PLA); 00101 SID replica (SID); 00110 SID 2 FM synth (FMSynth).
- 00111 Retro GPIO chip (3 DACs); 01000 Retro DRAM controller.
- 01001 "Halt and Catch Fire (do not select)".
- 01010 MCPU32 Dynamic DFF Tester: 32-bit 4-instruction CPU (MCPU extended to 32 bits) using only dynamic DFFs, macro MCPU32 (`excluded.cells` removes static dfxtp/dfsrtp/dlxf, so the dynamic flop must be used; inferred to be `dfxtpd_2`).
- 01011 NTSC test generator 2 (composite luma+chroma via DAC), macro NTSCTest.
- 01100 Hellorld + Diceroll + blinker, nanoprocessor, simple 8-bit CPU, secret-message stub, all in macro Combined.
- 11101 FeatherLane MCPU32 and 11110 FeatherLane RV32I: two layouts made by the external FeatherLane flow (codeberg.org/TholinVali/FeatherLane), checked in as `FeatherLaneStuff/fl_*.gds/lef/lib/mag/v` with blackbox Verilog and a SIM model. Cell names are prefixed `fl_gf180mcu_as_sc_mcu7t3v3__` (`dfxtpd_2` x177, mux2, clkbuff, diode, tap, filltype_*), so FeatherLane writes its own placement of this library.
- 11111 all pads high-Z.
- Art: `art/` (palette_1, td, avali, expie, whisper, tholin; own gds/lef/lib).

Analog: `macros/Analog/r2r_dac`: 12-bit buffered R-2R DAC, 4 instances (dac_0..3) onto analog_PAD[0..3]. Extracted spice uses `nfet_03v3` (23), `pfet_03v3` (25), `ppolyf_u_1k` (31, r_width 1u): 3.3 V devices, a retune of the AS03 DAC. xschem `opamp_chonky`, `r2r_dac_bench.sch` (tran 1n 3u). The mag view has `nfet_03v3`/`pfet_03v3`/`ppolyf_u_1k` generated cells. Analog pad: `macros/Analog/pad/apad` (gds/lef/lib/mag/verilog, ports WEH and ASIG5V).

Verification: cocotb benches with committed `results.xml` (MCPU32 passes the ISA check; built on the author's machine) for 65RV32, C64PLA, Combined, DRAM, FLMCPU32, GPIO, MCPU32, NTSC, SID. Not present: final layout, DRC/LVS/STA reports, silicon data.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Tholin | all designs, library, FeatherLane (5 commits) | Avalon Semiconductors; Codeberg user TholinVali (per README link) | repo owner; GitHub profile of 89Mods = Tholin, Germany |
| Leo Moser | wafer.space template (98 commits) | not stated | git log, AUTHORS.md |
| Tim Ansell, TrevorPeyton | template commits | not stated | git log |

## Value for GF180MCU characterisation and PDK development

### Verdict: High

Design 01010 is purpose-built characterisation: its doc states the minimum clock for dynamic DFFs "for this specific process and SCL is to be determined using this layout". The die is also, in effect, the first silicon of the whole 3.3 V Avalon library, which its own README calls WiP, and has 3.3 V DACs on pad-accessible analog outputs.

### Test structures and measurable circuits

| Structure | Exercises | Access | Where |
|---|---|---|---|
| MCPU32 dynamic DFF tester | dynamic-DFF retention and minimum clock; as_sc `dfxtpd` timing | clock pads and functional pass/fail through GPIO/test outputs; sweep clock | `macros/MCPU32`, `docs/source/dynmcpu32.rst` |
| as_sc library across 9 macros + 2 FeatherLane layouts | 3.3 V cell delay and max clock (RV32, 6502, SID, GPIO, DRAM) | pad pass/fail vs clock and VDD | `macros/*/config.yaml` |
| 4x 12-bit R-2R DAC (3.3 V) | `ppolyf_u_1k` matching/INL, `nfet_03v3`/`pfet_03v3` opamp, 1 kohm drive | analog pads 0..3; NTSC mirrors digital composite on bidir[22:11]; GPIO DAC registers | `macros/Analog/r2r_dac`, `apad` |
| Level-shifting ocd IO pads | `gf180mcu_ocd_io` at 3.3 V | bidir pads | `librelane` |

Simulation to compare: extracted spice and xschem bench; liberty from the PDK (not in repo); no stored waveforms.

### Candidate PDK additions

- The `gf180mcu_as_sc_mcu7t3v3` library (cells including a dynamic DFF, dlxf latches, hcf_7, dlybuff); the PDK fork's magicrc and the template Makefile already reference it.
- The `apad` analog pad and the 3.3 V DAC macro.
- The FeatherLane flow and its layouts.
- Template note: the Makefile marks `gf180mcu_osu_sc_gp9t3v3` and `gp12t3v3` as "(broken)".

### What would be needed to use it

Packaged or bare-die test with 3.3 V core and separate DVDD, a clock generator able to go very low (for dynamic DFF retention) and fast, a scope/ADC. No test plan in the repo.

## Notes and caveats

- The library is not vendored; PDK commit d658698 returned 404 on GitHub wafer-space/gf180mcu when checked, and the default branch lacks the library under libs.ref.
- FeatherLane source is on Codeberg, not in the repo.
- `docs/source/gpio.rst` still says the DACs are "tuned for 5V" (stale copy from AS03).
- "dfxtpd = dynamic" is inferred; its spice is not in the shipped spice file.
- This die and AS03 together are the de facto silicon validation of Avalon's libraries; the repo has no measured data.

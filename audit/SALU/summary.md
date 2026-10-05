# SALU: Simple ALU (ws-run2)

| | |
|---|---|
| Repository | https://github.com/StackDoubleFlow/alu_silicon @ 15ae8bf (main, last commit 2026-07-14) |
| Slot | 0p5x0p5 |
| Top cell | chip_top |
| Licence in repo | MIT (LICENSE added in 0aba293) |
| README | TEMPLATE (identical to the wafer-space template README) |

## What the repo actually contains
Template (2026-07-04 state) plus one design commit. `chisel/src/main/scala/ALU.scala` (Chisel via mill) generates `src/chisel/ALU.sv`: 8-bit ALU, registered output, ops add/sub/sll/srl/sra/or/and/xor. `chip_core.sv`: `bidir_in[7:0]` src1, `[15:8]` src2, `[18:16]` control, `bidir_out[26:19]` result; reset `~rst_n`. Flow: LibreLane 5 V default (gf180mcu_fd_sc_mcu7t5v0, gf180mcu_fd_io), PDK commit d658698, 25 MHz; SRAM macro entries removed; no SRAM or analog. `cocotb/chip_top_tb.py` (278 lines) tests the ops. No signoff reports in tree. Release v1.0 has `design.gds.gz` (9.7 MB, not unpacked).

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| StackDoubleFlow | ALU design (3 commits) | not stated (profile: Illinois, USA) | `git shortlog`, `gh api` |
| Leo Moser et al. | template | wafer.space template | git log, AUTHORS.md |

## Value for GF180MCU characterisation and PDK development
### Verdict: Low
Tiny synthesised ALU on stock 5 V cells; yield data point only.
### Test structures and measurable circuits
Nothing built for characterisation; pad-to-pad delay is measurable but no SDF/timing results are checked in.
### Candidate PDK additions
Nothing found.
### What would be needed to use it
Packaged test driving 19 input pads and reading 8 outputs at 25 MHz; no test plan.
## Notes and caveats
README is unmodified template; the platform text matches the sources.

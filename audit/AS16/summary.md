# AS16: AS16 CPU (ws-run2)

| | |
|---|---|
| Repository | https://github.com/SUD0NET/as16 @ 0cfc5a5 (main, last commit 2026-07-17; first commit 2026-07-12) |
| Slot | 1x0p5 (platform; Makefile default is 1x1) |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | OK (413 own words on top of the template README) |

## What the repo actually contains

`src/as16.v` (102 lines): a 16-bit RISC CPU with predication (3 predicate bits against C and Z), a 16 x 16-bit register file (R0 = 0, R15 = PC), a 6-state FSM (FETCH0, FETCH1, EA_ED, RDMEM, EXEC, WRMEM), 8 ALU ops (LD, ADD, AND, OR, XOR, ROR, ADC, STO), and 16- or 32-bit instructions. Memory is external only: datain on bidir[15:0], dataout on bidir[15:0] (oe = !rnw), address on bidir[31:16], rnw on bidir[32].

The flow is the wafer.space template: 5 V `gf180mcu_fd_sc_mcu7t5v0`, `gf180mcu_fd_io`, `gf180mcu_fd_ip_sram`. `chip_core.sv` also instantiates two `gf180mcu_fd_ip_sram__sram512x8m8wm1` with CEN=1 and A=0 tied off and `(* keep *)`; they are not connected to the CPU. No analog use.

Not present: final layout, reports, silicon data. The cocotb bench is the template one (a 1-line change adds `as16.v` to the sources) and has no CPU test.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Adnan Saad (GitHub SUD0NET, "Retro Software Programmer") | sole author of the CPU (11 commits) | Year 10 student, Sydney Technical High School per the platform description; not stated in the repo | project.json; GitHub bio |
| Leo Moser | template | not stated | AUTHORS.md |

## Value for GF180MCU characterisation and PDK development

### Verdict: Low

Ordinary synthesised digital on stock 5 V cells; useful as a yield and functional data point.

### Test structures and measurable circuits

Nothing found. A max-clock figure for a small synthesised CPU is possible, but there are no timing numbers in the repo. The two SRAM macros are inactive, so they give no bit-cell data.

### Candidate PDK additions

Nothing found.

### What would be needed to use it

An external 16-bit memory plus clock and reset to run any program; there is no test program in the repo.

## Notes and caveats

- Slot is 1x0p5 on the platform versus a Makefile default of 1x1 (the CI matrix covers slots).
- The SRAM macros are dead weight (inferred from the tie-offs).
- "My first ever tapeout" and the Year 10 claim come only from the platform description.

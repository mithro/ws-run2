# KIAN: KianV: A 32-bit RISC-V Linux SoC taped out on GF180MCU Run 2 (ws-run2)

| | |
|---|---|
| Repository | https://github.com/splinedrive/gf180mcu-kianv-rv32ima-sv32-ws02 @ 0b383ba (main, last commit 2026-07-14) |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | THIN (original but only 61 words) |

## What the repo actually contains

The same KianV RV32IMA SV32 Linux/XV6 SoC as run 1, ported to the 3.3 V flow: `gf180mcu_as_sc_mcu7t3v3` standard cells, 21 `gf180mcu_ocd_ip_sram__sram512x8m8wm1` macros and `gf180mcu_ocd_io` pads.

The git history is template pulls plus one migration commit (81a2e77). There are no final views, metrics or releases in the repo, so there is no timing evidence.

### Changes from run 1

| | Run 1 | Run 2 |
|---|---|---|
| Standard cells | `gf180mcu_fd_sc_mcu9t5v0` | `gf180mcu_as_sc_mcu7t3v3` |
| SRAM | foundry 512x8 (5 V) | ocd 512x8 (3.3 V); wrapper is a one-line change |
| Pads | `gf180mcu_fd_io` | `gf180mcu_ocd_io` |
| Power pads | 8 DVDD / 10 DVSS, shorted to core | 6 DVDD / 8 DVSS plus 2 VDD / 2 VSS, separate |
| Clock tree | | adds an explicit `clkbuff_12` clock buffer (`clk_core_clock_buffer`) |
| Config | inline macros | `macros_3v3.yaml` |

Unchanged: 33 ns clock target, 3932 x 5122 um die, 54 bidir pads. The run 2 repo has no final GDS and no `fpga/` directory.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Hirosh Dabui (GitHub splinedrive) | CPU and SoC (9 commits) | GitHub bio: "M.Sc.CE., Technical University of Berlin", Berlin | GitHub profile |
| Leo Moser (mole99) | project template | not stated | git log |

## Value for GF180MCU characterisation and PDK development

### Verdict: Low

Ordinary synthesised digital. Its value is as a large functional test of the new 3.3 V standard cells, 3.3 V SRAM macros and ocd IO, and as the second half of a like-for-like comparison with the run 1 chip (same RTL, same 33 ns target).

### Test structures and measurable circuits

Nothing purpose-built. 21 ocd 3.3 V SRAM macros are exercised functionally as caches.

### Candidate PDK additions

Nothing found.

### What would be needed to use it

A board with SDRAM and SPI flash, with separate core and IO supplies. No test plan in the repo.

## Notes and caveats

- No layout, reports or release in the repo.

# AMM1: raybox-zero wafer.space run 2 half height (ws-run2)

| | |
|---|---|
| Repository | https://github.com/algofoogle/gf180ws2-raybox-zero @ f5bbcef (main, last commit 2026-07-15) |
| Slot | 1x0p5 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 (LICENSE) |
| README | OK (978 words, substantive) |

## What the repo actually contains

Anton Maurovic's raybox-zero ray-casting "3D" renderer (a 32x32 map, 4 doors, 8 textures plus door texture, Q11.11 fixed point, demo mode, debug overlay) hardened on the wafer.space project template with LibreLane 3. The RTL is the submodule `src/raybox-zero` (HEAD 8d827a0, initialised and present) plus `src/chip_core.sv`, `src/rbz_options.v` (feature switches: map overlay, debug overlay, leak-fixed, SPI POV regs, map rect, doors, wait-states config) and the template `chip_top.sv`.
- Cells: `gf180mcu_fd_sc_mcu7t5v0` (5 V), `gf180mcu_fd_io` pads, no SRAM macros (texture memory is flops / optional external QSPI ROM; the PNL has no `sram` instances) and no analog blocks. Flow: `SYNTH_STRATEGY: "DELAY 2"`, `CLOCK_PERIOD: 40` (25 MHz), hold margins 0.40/0.35 with hold buffers allowed up to 70 % (the submitted PNL has about 11,400 `dlyb_1` cells).
- IO: bidir[7:0] inputs (SPI and QSPI controls), bidir[23:16] RGB222 + hsync/vsync in Tiny VGA PMOD order (`registered_vga_output` selectable by `i_reg`), bidir[15:8] QSPI texture ROM pins (Leo Moser PMOD), bidir[27:24] hblank/vblank/hmax/vmax debug, bidir[37:28] vpos, bidir[38+] unused inputs. Pads set to CMOS input, fast slew, no pulls.
- Verification: cocotb testbench `cocotb/chip_top_tb.py` with a W25Q128JV flash model and texture ROM hex files in `cocotb/texture_rom/`; RTL sim and gate-level sim flows. No DRC/LVS/STA reports are in the repo.
- Layouts: `wafer.space/` holds bz2 GDS and powered netlists for commit 4ab47b1 (1x0p5 build) and a 0p5x1 variant (added in the last commit). The platform layout is the 1x0p5 one.
- Docs: `doc/render.png`, `doc/3dscreens.png` only.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Anton Maurovic (algofoogle) | project author and raybox-zero author (13+1 commits) | not stated (GitHub profile: Adelaide, Australia; no company) | `git shortlog`, README, gh api |
| Leo Moser | template author (AUTHORS.md) | not stated | AUTHORS.md |

## Value for GF180MCU characterisation and PDK development

### Verdict: Low
Ordinary synthesised digital logic on stock cells with a VGA digital output. It is a yield/functional data point and a real-time visible demo; there are no dedicated test structures.

### Test structures and measurable circuits
No purpose-built structures. Measurable behaviour: the whole design runs from a 25 MHz pad clock, produces a 25 MHz-class VGA pixel stream (RGB222 + syncs on bidir pads 16..23, which is a pixel-clock-rate digital output, not a timing-critical PHY). Maximum working clock versus supply, and failure of the long reciprocal paths (see timing hack) would be a coarse indicator of real delay versus STA margins. No simulation data intended for comparison with silicon is in the repo beyond RTL/GL test benches.

### Candidate PDK additions
Nothing found. Documented flow issues (not PDK defects per se): (1) a `set_false_path -through` on the 22 `rcp_fsm.operand*` nets in `librelane/chip_top.sdc` because the reciprocal chained-multiplier paths are really multicycle but the author could not express that through Yosys/ABC restructuring, which leaves surrounding logic unchecked; (2) the first hardening gave gate-level iverilog X on synchronous resets because the mapped logic used `D = ~(~q | q)` patterns (non-async-reset DFFs), worked around by `SYNTH_STRATEGY "DELAY 2"`.

### What would be needed to use it
Packaged part, 25 MHz clock source, SPI host and a VGA monitor or capture board; nothing for characterisation.

## Notes and caveats
- The timing false path means STA does not cover the reciprocal path; a silicon speed test of the chip would measure the real limit but is not a controlled measurement.
- Two layouts exist in the repo (1x0p5 and 0p5x1); the 0p5x1 one is not what was submitted.
- I could not run anything, so counts such as hold buffers come from the PNL text in `wafer.space/`.

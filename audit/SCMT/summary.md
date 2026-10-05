# SCMT: microTheia (ws-run2)

| | |
|---|---|
| Repository | https://github.com/dhgaddy/microTheia @ ef69ed4 (main, last commit 2026-07-30); README clone path is dolphin-530/microTheia |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | OK (1086 words) |

## What the repo actually contains
Event-based vision SoC: SPI slave (`third_party/verilog_spi`, submodule jasonwaseq/verilog_spi @ d2698c0), EVT2 decoder, input FIFO, voxel binning (320x320 to 16x16 grid, 16 time bins, double-buffered feature RAM), MAC engine for four programmable class weights, argmax/threshold classifier, boot FSM, selectable debug mux. Flow: LibreLane, **3.3 V** (as_sc_mcu7t3v3, ocd_io), 64 MHz (period 15.625 ns), PL density 41 %, PDK commit f6eeac7. Macros: gf180mcu_ocd_ip_sram 1024x8 (32 instances listed), 256x8 (9), none of 512x8. git LFS: 55 files (EVT2 test streams, `weights/*.mem`), none missing. `docs/` has architecture, RTL reference, simulation, limitations. README embeds a timing-closure screenshot ("positive setup and hold slack in all tested corners"; max-cap and max-slew violations explained as pad/clock-buffer limits against the 0.2 pF global limit), "Full pass LVS and DRC". Gate-level sim passes four gesture classes (about 7 h per run). No `final/` or signoff files in the repo; GDS only as release assets (v1.0 2026-07-04, v1.1 2026-07-15).

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| Marco Frank, Jason Waseq, Marc Romero, Liam Ditscheiner | RTL/flow | not stated | AUTHORS.md, git |
| Dalton Gaddy (dhgaddy) | repo owner | UC Santa Cruz (GitHub bio "CE B.S. @UCSC"; ucsc.edu email also hint) | `gh api`, git |
| course | not stated | | |

## Value for GF180MCU characterisation and PDK development
### Verdict: Low
Synthesised digital with many SRAM macros at 3.3 V; no test structures. The 64 MHz target and the many SRAMs make it a decent timing-closure data point.
### Test structures and measurable circuits
Nothing dedicated; debug mux (`docs/debug_mux_pinout.txt`, `docs/pin_chart.csv`) exposes 32 internal bits per page. No simulation reports checked in to compare with.
### Candidate PDK additions
`sim/gf180mcu_as_sc_mcu7t3v3_missing_cells.v` (stubs for cells missing in the shipped Verilog model). Authors document that the SRAM Verilog timing models are not consistently present in the open PDK, so SDF back-annotation silently falls back to zero delay (`make sim-sdf`).
### What would be needed to use it
Packaged test with an SPI master (Prophesee/EVT2 camera or MCU), weights loaded after every power cycle (BOOT_REQ sequence).
## Notes and caveats
Two release GDS versions; HEAD is after v1.1. The in-repo layout was not inspected (LFS contains test data only).

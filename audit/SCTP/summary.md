# SCTP: SlugTPU (ws-run2)

| | |
|---|---|
| Repository | https://github.com/SlugTPU/gf180mcu-slugtpu @ e906c15 (main, last commit 2026-07-13) |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | OK (1061 own words on top of the template) |

## What the repo actually contains
Quantised-inference TPU: 8x8 INT8 systolic array (`src/sysray`, double-buffered weights, 32-bit accumulators), scalar post-processing pipeline (bias, ReLU, zero-point, fixed-point scale and saturate), CISC-style ISA (Dram2Sram, Sram2Dram, Matmul, ...), control unit, wishbone interconnect (`src/dram`), SDR SDRAM controller for a Micron MT48LC16M16A2 (32 MiB, off-chip), SPI-to-wishbone host bridge ("spibone"), debug mux, `TPU_ACTIVE` on bidir pad 38. Flow: LibreLane + slang, **3.3 V** (as_sc_mcu7t3v3, ocd_io), PDK commit 140b0494, CLOCK_PERIOD 17 ns at HEAD (an `mxu` sub-flow uses 25 MHz). **17 gf180mcu_ocd_ip_sram__sram1024x8m8wm1 macros** in `macros_3v3.yaml` (README still describes 256x8 macros and 2 KiB + 2 KiB). Many cocotb unit tests and assembled-program tests; the Micron SDRAM model is not in the repo for copyright reasons. A KiCad breakout board (`kicad/`) with a TSOP54 SDRAM and an ESP32-C3-MINI-1 footprint. No `final/` or signoff files; no releases.

The two submodules in `.gitmodules` (`ip/gf180mcu_ocd_ip_sram`, `ip/gf180mcu_as_sc_mcu7t3v3`) have no gitlink in HEAD. They were added 2026-03-14 and 2026-05-06 and removed from the tree 2026-06-08 ("remove old manual submodule import of 3v3 libraries"); the `.gitmodules` file was left behind. Branches 3v3-everything, integration, lint_fix, spi_rework still carry gitlinks (ocd_ip_sram @ 2c2a601, as_sc_mcu7t3v3 @ 9444996). At HEAD the libraries come from the PDK that `make clone-pdk` installs via ciel (`ciel enable 140b0494...`, `--include-libraries all`): `macros_3v3.yaml` uses `pdk_dir::libs.ref/gf180mcu_ocd_ip_sram/...` and the SCL config uses `libs.ref/gf180mcu_as_sc_mcu7t3v3`. The clone-status errors for those submodules are expected and harmless.

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| yanghuaxuan (Huaxuan Yang) | most commits (about 300) | not stated | git |
| Shreyas Gupta, Adi-0 (Aditya Kumar), Angelina Nguyen | design | Angelina Nguyen has ucsc.edu email (hint) | git |
| course | **UC Santa Cruz CSE 127A/B Capstone Course (2026)** | | README |
| Leo Moser | template | wafer.space | AUTHORS.md |

## Value for GF180MCU characterisation and PDK development
### Verdict: Low
Synthesised digital with 17 SRAM macros; functional/yield and timing data point only.
### Test structures and measurable circuits
Nothing dedicated; debug mux (`src/debug_mux.sv`) and `TPU_ACTIVE`. No sim results in repo.
### Candidate PDK additions
Nothing found; no PDK problems documented.
### What would be needed to use it
Packaged test with the custom PCB and an SDRAM, SPI host, assembled test programs (`cocotb/general_test`).
## Notes and caveats
Stale `.gitmodules`; README out of date on SRAM size; no hardening results in the tree.

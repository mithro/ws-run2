# PSOC: Simplest possible PicoSoC implementation using wafer.space flow (ws-run2)

| | |
|---|---|
| Repository | https://github.com/burnettlab/picosoc-on-waferspace @ a5283bc (main, last commit 2026-07-13); platform lists d-burnett/picosoc-on-waferspace |
| Slot | 1x0p5 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | THIN (98 words, original) |

## What the repo actually contains
PicoRV32 SoC on the wafer.space template: `ip/picorv32.v` (RV32IC, barrel shifter, counters, IRQ; no MUL/DIV), `src/spimemio.v` (QSPI flash), `src/simpleuart.v`, `src/simple_sram.v`, template-derived `chip_core.sv` (a leftover template counter XORed onto data pads remains; a `chip_core.sv~` backup is committed). README credits the template, JBFSF/SensorSoC, YosysHQ/picorv32 and lawrie/pico_ram_soc. Stated pinout: power, ground, clock, reset, serial tx/rx, QSPI (6 pins). Wishbone, I2C open-drain IO, bandgap, regulators and a radio are plans only; nothing is in the repo.
- Flow: LibreLane, **5 V** (gf180mcu_fd_sc_mcu7t5v0, gf180mcu_fd_io), PDK commit 140b0494, 25 MHz.
- **Eight gf180mcu_fd_ip_sram__sram512x8m8wm1 (5 V) macros**, 4 KiB as 1024 x 32 (`macros_5v.yaml`, `simple_sram.v`).
- A complete run is checked in (`final/`, 534 MB: GDS 99 MB, SDF/SPEF for 9 corners, `metrics.json`, netlists) plus `chip_top.gds.zip`.
- `final/metrics.json`: 42,204 stdcells (1.18 mm^2), 13 macros (1.80 mm^2), die 9.95 mm^2, util 59.5 %. KLayout and Magic DRC, antenna, density, XOR and all LVS counts 0; IR drop worst 0.127 mV. **Setup timing fails: overall WS -6.26 ns, nom_ss_125C_4v50 -4.31 ns (TNS -205 ns); TT +14.4 ns, FF +21.2 ns.** Hold is positive. Not mentioned in the README.
- Simulation: template `cocotb/chip_top_tb.py` only; no firmware test. No bring-up data.

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| d-burnett | sole committer (3 commits), owner of GitHub org burnettlab | not stated | `git shortlog`, `gh api` (no name/company) |

## Value for GF180MCU characterisation and PDK development
### Verdict: Low
Synthesised digital on stock 5 V cells plus eight foundry 5 V SRAMs; a functional/yield data point and a worked 5 V SRAM integration.
### Test structures and measurable circuits
Nothing built for characterisation. The SoC run at a known clock gives a max-frequency vs conditions point; signoff SDF/SPEF are in `final/` to compare (SS setup is short by 4.3 ns at 25 MHz).
### Candidate PDK additions
Nothing found; no PDK problems documented.
### What would be needed to use it
Packaged test with QSPI flash holding firmware (reset vector 0x00100000) and UART; no firmware or test plan in repo.
## Notes and caveats
Platform description and README differ in scope; nothing analog is present; repo owner (burnettlab) differs from the platform owner (d-burnett).

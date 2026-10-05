# NAX1: Naxos CoB (ws-run2)

| | |
|---|---|
| Repository | https://github.com/ZeduloTech/Naxos @ 17da59e (main, last commit 2026-07-15) |
| Slot | 1x0p5 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 (LICENSE; SPDX headers in sources) |
| README | TEMPLATE (100% the wafer.space project-template README, no own text) |

## What the repo actually contains

Platform description is empty and the README is the template, so this is derived from sources. Naxos is a sibling of CAB1 Cabrera: same Caravel (VexRiscv) harness, same Zedulo team, same repo layout, but the whole chip runs in the 3.3 V domain with the `gf180mcu_as_sc_mcu7t3v3` standard-cell library (`STD_CELL_LIBRARY` in `librelane/config.yaml`; commit "Update gf180mcu_as_sc_mcu7t3v3 due to hotfix"). Clock 50 MHz (CLOCK_PERIOD 20). Build: `run.sh` hardens `ztimer/` first, then the chip with LibreLane (leo/gf180mcu branch).

Contents of `src/chip_core.sv`:
1. Caravel core (VexRiscv, SPI flash, GPIO), selectable CMOS or crystal clock via `gf180mcu_as_sc_mcu7t3v3__mux2_4`.
2. `XTAL` custom analog crystal-oscillator driver macro (`ip/XTAL3P3/XTAL.gds/.lef`, 456.4 x 68.5 um, pins OSC1, OSC2, VCLOCK, own VDD_XTAL/VSS_XTAL; GDS shows nfet/pfet/ppolyf_u_resistor pcells at 3.3 V). Simulation model is a fixed 48 MHz clock. Clock also fed back to pad `PAD_SYS_CLK_FB`.
3. OpenTitan USB full-speed device (`otUSB/src/usbdev*.sv`, `usb2sram`, wrapper `naxos_usb_wrapper`) with four foundry 3.3 V SRAM macros `gf180mcu_ocd_ip_sram__sram512x8m8wm1` (`i_chip_core.usb.sram_0..3`, macros_3v3.yaml) giving 2 kB packet buffer (wrappers for 1024x8 and 512x8 in `ip/sram/`). Behavioural sim passes USB enumeration.
4. `ztimer`: SPI-read timer built around four copies of a pulse-shrinking time-to-digital converter `shrinking_tdc` (`pstdc/`), see below.
5. `apad_helper` cells to route analog pads (EXTPULSE, START, STOP) via OpenROAD.

No eFuse, no flash block, no ring-oscillator macros; the only SRAM is the USB buffer. `final/gds/naxos.gds.gz` is the committed chip layout. No silicon data. `PAD_MARK_DOWN.md` lists pads for ztimer (CSB 43, SDI 42, SCK 41, SDO 40, STOP/START analog[3]/[2], ROSC_EN input[1], the last a leftover from the Cabrera-style ring-oscillator design; the Naxos code has no ROSC_EN).

## Authors and affiliations

| Who | Role | Affiliation | Source |
|---|---|---|---|
| Egor Lukyanchenko (egorxe) | Caravel integration, USB, psTDC model, 41 commits | not stated; Zedulo copyright in headers | git log, AUTHORS.md |
| snapaa257 (several identities, Zedulo emails) | ztimer, USB, pads, CI, 42 commits | Zedulo (header "Zedulo Sweden AB"; email domain hint) | git shortlog, SPDX headers |
| Leo Moser | wafer.space template, 98 commits | wafer.space template maintainer (AUTHORS.md; affiliation not stated) | AUTHORS.md |
| Tim Ansell, TrevorPeyton, ZeduloAdmin | single commits | not stated | git shortlog |
| ZeduloTech org | owner | "Zedulo", Sweden, zedulo.com | `gh api orgs/ZeduloTech` |

## Value for GF180MCU characterisation and PDK development

### Verdict: High

Contains a purpose-built 3.3 V pulse-shrinking TDC (picosecond-class gate-delay measurement), a custom analog crystal-oscillator driver macro, and uses a new 3.3 V standard-cell library and the 3.3 V foundry SRAM at scale, all pad-accessible via SPI/analog pads.

### Test structures and measurable circuits

| Structure | What it exercises | Access | Where |
|---|---|---|---|
| `shrinking_tdc` x4 (sc_start, sc_stop, sc_cal, sc_direct): `shrink_unit` = NAND gate + loop of 1024 `gf180mcu_as_sc_mcu7t3v3__inv_2` closed through nand2_4 (each trip about 48 ns per ztimer.sv comments), feeding a 13-bit ripple counter of `dfsrtp_2` flops. A negative pulse loses about 30 ps per trip (author's comment); the number of trips before it vanishes is the count | Rise/fall delay asymmetry of inv_2 at 3.3 V (pulse shrink per stage), absolute inverter delay (loop time), dfsrtp_2 clk-to-Q; subnanosecond timing | START/STOP/EXTPULSE analog pads (via apad_helper), reset-synchronised; counts read through SPI (CSB/SCK/SDI/SDO pads) | `pstdc/shrinking_tdc.v`, `pstdc/final/{gds,lef,spice}`, `ztimer/src/*.sv` |
| Post-layout extracted netlist and SPICE bench for the TDC | Direct simulation reference: `pstdc/pex/shrinking_tdc.pex.spice` (3.6 MB), `digital_shrink_test.ngspice` / `.xyce` use `sm141064.ngspice` typical models at 3.3 V, 25 C, transient 150 ns | silicon vs simulation comparison possible | `pstdc/pex/` |
| `clk_timer` on core clock | Reference count of the same window | SPI | `ztimer/src/clk_timer.sv` |
| `XTAL` crystal oscillator driver | Analog oscillator start-up/gain with 3.3 V nfet/pfet and ppolyf_u_resistor | OSC1/OSC2 analog pads (external crystal), VCLOCK to core mux and feedback pad | `ip/XTAL3P3/` |
| 3.3 V `gf180mcu_as_sc_mcu7t3v3` library (inv, nand2, dfsrtp, mux2, clkbuff) used chip-wide | Library delay/power at 3.3 V for a full SoC | functional at 50 MHz STA target | `librelane/config.yaml` |
| 3.3 V foundry SRAM `gf180mcu_ocd_ip_sram__sram512x8m8wm1` x4 | 3.3 V SRAM macro in anger (USB buffer) | via Caravel Wishbone/USB | `librelane/macros/macros_3v3.yaml` |

### Candidate PDK additions

- The pulse-shrinking TDC flow (hardened at 120x120 um with a custom pin order, timing steps disabled) as a reusable delay-measurement macro, with a PEX netlist and SPICE bench.
- `gf180mcu_as_sc_mcu7t3v3` 3.3 V library exercised on a whole SoC; the Egor commit log shows a hotfix to it during the project (unmapped-cell and latch issues "Fix latches", "unmapped cells fixed").
- `apad_helper` cell workaround so OpenROAD can route analog pads; analog `XTAL` macro with separate supplies.
- Flow notes: PDN_MACRO_CONNECTIONS for SRAM and XTAL supplies, 3.3 V core ring layers changed to Metal3/Metal4.

### What would be needed to use it

Packaged die with SPI master, a pulse source with controllable width (ps-class pulse width needs an external generator or the EXTPULSE pad), and a crystal for the XTAL test. Documentation of the TDC calibration (sc_cal) and register map is only in code comments (`ztimer/src/ztimer.sv`, `spi_device.sv`).

## Notes and caveats

- Platform description empty; "Naxos"/"CoB" unexplained in the repo.
- `ztimer.sv` selects `sctimer` (behavioural, with simulated delays 0.047 ns/inverter) for SIM and `shrinking_tdc` for synthesis, so RTL simulation does not exercise the real delay line; only the PEX SPICE bench does.
- The GDS of XTAL and shrinking TDC were not opened in a layout tool (strings only).
- Relationship to earlier chips: TZ01 (Run 1 eFuse+SRAM test chip, Zedulo/Egor with Tillitis support) used the same Caravel template; Naxos has no eFuse or SPI-SRAM test blocks. CAB1 Cabrera is the 5 V sibling with Ethernet/10BASE-T, 4-RO ztimer and a flash_ip probe block; Naxos is the 3.3 V sibling with USB, XTAL and the psTDC ztimer.

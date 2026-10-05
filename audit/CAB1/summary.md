# CAB1: Cabrera CoB (ws-run2)

| | |
|---|---|
| Repository | https://github.com/ZeduloTech/Cabrera @ 2081f9b (main, last commit 2026-07-15) |
| Slot | 1x0p5 (DIE_AREA 0 0 3932 2531 um) |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 (LICENSE; SPDX headers "Zedulo" in source) |
| README | TEMPLATE (100% the wafer.space project-template README, no own text) |

## What the repo actually contains

Platform description is empty and the README is the template, so this is derived from sources. "CoB" is not explained anywhere in the repo (inferred: chip-on-board). Cabrera is a Caravel-based (VexRiscv SoC from egorxe/gf180mcu-caravel-template, `caravel/`) 5 V design with four user peripherals, built with the leo/gf180mcu LibreLane branch and the standard wafer.space template (`librelane/config.yaml`, `src/chip_core.sv`, `src/chip_top.sv`). Standard cells: gf180mcu_fd_sc_mcu7t5v0. Wishbone clock 20 MHz (commit "clock period set to 20MHz").

Contents of `src/chip_core.sv`:
1. Caravel core (Wishbone master, SPI flash pads, GPIO).
2. LiteEth Ethernet MAC (`EthernetMac/src/liteeth_core.v`, generated, 256x8 MAC memory) with two foundry 5 V SRAM macros `gf180mcu_fd_ip_sram__sram256x8m8wm1` (reader/writer slot0) and a `mii_mux` to route MII either to external pads or to the PHY.
3. 10BASE-T PHY (`ip/tenbaset/`: tenbaset_phy_top.v, tx, rx digital at 80 MHz) with a custom analog transmit driver macro `tenbaset_tx_driver` (207.97 x 186.175 um; GDS cells `dac_cell`, `dac_cell_x2/x4`, `driver_cell`, `driver_half`, built from nfet, pfet and ppolyf_u_resistor pcells; outputs on analog pads TXP/TXN). Commit log says an earlier "PHY ip breaks LVS" and a precheck-clean GDS "with non functional timer and 10BaseT PHY" (`final/gds/cabrera_notimer_testphy.gds.gz`) exist, so the PHY was iterated; final integration commit 2026-07-15 "Update 10BaseT PHY integration".
4. `ztimer` (see below), a pad-accessible time-interval meter with a ring-oscillator bank.
5. `flash_ip`: a 2003 x 222.6 um block with 16 bondpads (Pad1..Pad16, cell `Bondpad_5LM` and `flash_3v3`), instantiated with no ports (`(* keep *) flash_ip flash_ip ();`), placed at (513, 1860). See below.

Other: `ip/simple_por` (SPICE-level power-on-reset with Schmitt trigger testbenches, `ip/simple_por/netlist/*.spice`), `cocotb/` RTL and gate-level testbench, `final/` with hardened outputs (gds.gz, lib, nl, pnl, spef, vh) for the chip and sub-macros, `rosc3/5/9/27/` and `ztimer/` hardened sub-flows including SDF/SPEF/spice at 9 PVT corners. Chip GDS (`final/gds/cabrera_260714.gds.gz`, `chip_top.gds.gz`) is committed. No post-silicon data. No eFuse macros and no SRAM test structure; only two foundry SRAM instances used as MAC buffers.

## Authors and affiliations

| Who | Role | Affiliation | Source |
|---|---|---|---|
| Egor Lukyanchenko (egorxe) | Caravel integration, Ethernet MAC, 10BaseT PHY, flash_ip, 32 commits | not stated in repo/GitHub profile; "Zedulo" appears in copyright | git log, AUTHORS (NAX1), README of TZ01 |
| snapaa257 (two identities, Zedulo email addresses) | ztimer, ring oscillators, PADs, CI, 16 commits | Zedulo (email domain hint; source headers say "Zedulo Sweden AB") | git shortlog, SPDX headers |
| Leo Moser | wafer.space template author, 78 commits of template history | wafer.space template maintainer (AUTHORS.md lists him; affiliation not stated) | AUTHORS.md, git log |
| Tim Ansell, TrevorPeyton | one commit each (template) | not stated | git shortlog |
| Zedulo / ZeduloTech org | owner | "Zedulo", location Sweden, zedulo.com | `gh api orgs/ZeduloTech`; header "Zedulo Sweden AB" |

## Value for GF180MCU characterisation and PDK development

### Verdict: High

Contains purpose-built, pad-accessible measurement structures: a bank of four free-running ring oscillators with a timer/time-interval instrument readable over SPI, plus a 16-pad probe-pad block that appears to be a floating-gate/flash test cell. Both are not hidden behind the CPU.

### Test structures and measurable circuits

| Structure | What it exercises | Access | Where |
|---|---|---|---|
| `not_rosc3/5/9/27`: ring oscillators of 3, 5, 9, 27 `gf180mcu_fd_sc_mcu7t5v0__inv_1` (with `rosc_enable ? loop : 1` gating), each a separate 50x50 um hardened macro, enable tied high (free-running), each buffered by clkbuf_8 into its own 32-bit counter | inv_1 propagation delay at 5 V (period/(2N), slope over N=3..27 separates fixed overhead from per-stage delay), across die and temperature | start/stop on input/analog pads (`PADI_ZTIMER_START/STOP`), SPI slave on 4 bidir pads (CSB/SCK/SDI/SDO) reads five 32-bit counts (xtal reference + 4 ROs), clear via SPI | `ztimer/src/ztimer.sv`, `clk_timer.sv`, `rosc*/src/*.sv`, `rosc*/final/` |
| Reference-clock timer `u_timer_xtal` counting `clk` for the same window | Calibration of the RO counts against external clock | same | `ztimer/src/ztimer.sv` |
| `flash_ip` (`ip/flash_ip/gds/flash_ip.gds`, top cell TOP1, 16 Metal5 bondpads, cell `flash_3v3`) | Probable floating-gate/flash cell or pass-gate array in 3.3 V devices; LVS netlist (`project.spice`) extracts 16 pfet_03v3 (L=0.28 u, W 6.4 u and 0.8 u) and 24 nfet_03v3 (L 0.28 u, W 0.8 u) forming 4 identical 4-device columns driven from pads; the storage element itself is not extracted as a device (inferred, no documentation) | direct probe/bond on the 16 pads; unconnected to the core | `ip/flash_ip/` (also `test.gds`, `test.spice`, `Flash_SPI.gds`) |
| `tenbaset_tx_driver` analog driver/DAC | Resistor-DAC and driver cell behaviour; custom nfet/pfet/ppolyf_u_resistor | analog pads TXP/TXN, digital DAC inputs from PHY | `ip/tenbaset/` |

Voltage: core and ring oscillators run at 5 V (7t5v0 cells, 4.5-5.5 V corners); flash_ip uses 03v3 devices (pad-driven, supply unspecified). No Monte Carlo or silicon-correlation data exist; the per-macro SDF/lib files (`rosc3/final/sdf/*`) give STA delays at 9 corners that silicon can be compared against.

### Candidate PDK additions

- Probe-padded flash/floating-gate test cell: `flash_3v3` and `Bondpad_5LM` / `probe_pad` cells exist as GDS (not an official PDK cell). Documentation of what the cell is (floating-gate flash cell?) is absent; the `magic_lef.tcl` still carries commented-out eFuse-compiler lines, so it descends from the eFuse compiler flow.
- A hardened ring-oscillator-bank + timer + SPI block usable as a PDK "characterisation macro".
- Analog drive/DAC macro for 10BASE-T.
- Flow workarounds documented in commit log: "Add PND obstruction to remove superfluous vias and fix DRC", MAGIC_GDS_FLATGLOB entries for flash_ip, "OR optimization crash" workaround with a Wishbone register.

### What would be needed to use it

Packaged dies on a PCB with an SPI master (the SPI pins) plus a pulse generator or the Caravel CPU to produce a start/stop window; flash_ip needs direct pad probing/bonding and a cell description. A temperature chamber for RO delay versus T. No test plan or PCB in repo.

## Notes and caveats

- Platform description empty; name "Cabrera" and "CoB" are unexplained in repo.
- `flash_ip.v` is a blackbox with no ports: LVS/GDS evidence only. The "Flash_SPI" name suggests an SPI-flash IP, but nothing in the sources drives it. What the storage cell is cannot be determined from files read (GDS not opened with layout tools).
- `final/gds` holds three layouts (cabrera_260714, cabrera_notimer_testphy, chip_top); which one was submitted is not verified against the platform layout hash.
- `ztimer` RO enables are tied high so ring oscillators run permanently (power/self-heating, supply noise on neighbouring logic).
- Relationship: the same team made the Run 1 TZ01 "TillitisZedulo-testchip2025" (eFuse + SRAM + Caravel + UART2GPI). Cabrera reuses the Caravel template/flow from that chip but contains no eFuse macros; its flash_ip/probe-pad block is the nearest successor to the eFuse test blocks. Sibling chip: NAX1 Naxos (same ztimer idea, different peripherals, 3.3 V).

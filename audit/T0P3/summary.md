# T0P3: Tiny Tapeout GF 0p3 (ws-run2)

| | |
|---|---|
| Repository | https://github.com/TinyTapeout/tinytapeout-gf-0p3 @ 16c3012 (main, last commit authored 2026-07-15, committed 2026-09-14); taped out from 3050476 (2026-07-03), release `tapeout-ws2607` |
| Slot | 1x1 |
| Top cell | tt_gf_wrapper |
| Licence in repo | Apache-2.0 (`LICENSE`; no licence claim on the platform) |
| README | Thin: 74 words, links out to tinytapeout.com and the multiplexer docs; says nothing about analog support |

## What the repo actually contains

Tiny Tapeout GF 0p3 is a multi-project die for the wafer.space G802 run (die id G802T0P3, 3932 x 5122 um): 32 user designs behind the Tiny Tapeout multiplexer, 16 of them analog or mixed-signal custom layouts. It is the first Tiny Tapeout shuttle on GF180MCU with analog pads, analog switches, a separate analog supply and per-project power gating on both supplies. The platform description ("experimental shuttle with analog design support") is accurate.

Like the GF 0.2 repo (TTP2/TTPG on run 1), this is the integration repo, not the design sources:

| Path | Contents |
|---|---|
| `config.yaml`, `modules.yaml`, `mux_overrides.yaml` | Shuttle id `ttgf0p3`, PDK `gf180mcuD`, deadline 2026-06-19, `no_power_gating: false`. `modules.yaml` pins the placement and analog pad assignment of the 555, both VCOs and the ring oscillator ("high current pins short as possible", "control high-speed pins") |
| `projects/tt_um_*/` (32 dirs) | Per project: `.oas` layout, `.lef`, `.v` (gate-level netlist for digital projects, blackbox or structural stub for analog ones), `info.yaml`, `docs/info.md`, `commit_id.json`, `pdk.json`. No schematics, SPICE netlists or testbenches for the user projects; those are in each author's repo (linked in the table, not cloned here) |
| `projects/danger_level.yaml` | One entry, added after tapeout: `tt_um_fabulous_gf_0p3_3v3`, level `high`, "Uses a broken version of the 3v3 SCL that has a short in buf_8" |
| `tt-multiplexer/` (submodule, smunaut/tt-multiplexer branch `dev`, 3a0e0bb) | Mux RTL, top-level build scripts, and the full-custom GF180 infrastructure macros with sources: `pg/gf180mcuD/` (power gates) and `asw/gf180mcuD/` (analog switch, pad contact), each with xschem schematics, magic layouts, GDS, LEF |
| `tt/` (submodule tt-support-tools), `librelane/` (submodule smunaut/librelane branch `dev-tt-gf26`) | Tooling and flow |
| `verilog/dv/mux/` | cocotb mux testbench |

There is no PDK submodule; `BUILDING.md` fetches gf180mcuD with ciel at version `98203068432a374192b0163c6c7d491207b52992`.

### Shuttle infrastructure

Read from the release netlist `foundry_submission.zip/verilog/gl/tt_gf_wrapper.nl.v`, `macros.zip` and the `tt-multiplexer` sources:

| Block | Count | What it is |
|---|---|---|
| `tt_mux`, `tt_ctrl` | 13, 1 | Synthesised mux and controller on `gf180mcu_fd_sc_mcu7t5v0`; top-level corners `tt_025C_3v30`, `ss_125C_3v00`, `ff_n40C_3v60` |
| Pad ring `gf180mcu_ocd_io` | 74 pads | 16 `bi_24t`, 10 `in_c`, 3 `in_s`, 29 `asig_5p0`, 4 `dvdd`, 8 `dvss`, 2 `vdd`, 2 `vss`, 4 `cor`. Not the stock `gf180mcu_fd_io`. Separate IO, core and analog supply nets |
| `tt_pg_3v3_hp_1` / `_2` / `_4` | 3 / 26 / 3 | Per-project PMOS header switch on the 3.3 V core rail (VDPWR to the project's local rail), one per project. `hp_2` schematic: `pfet_03v3` L=0.28u W=3357.5u nf=395, gate inverter `pfet_03v3` 10.34u / `nfet_03v3` 5.5u, and a discharge chain of 8 `nfet_03v3` 0.99u/0.6u. Thin-oxide 3.3 V devices (no Dualgate layer in the GDS). Macro 11.2 um wide, 160.72 / 325.36 / 736.96 um tall |
| `tt_pg_5v0_2` | 6 | Power switch on the analog rail (VAPWR to GAPWR) for projects that asked for it (`pg_vaa: true`): `tt_um_tnt_gf_555`, `tt_um_analog_factory_test`, `tt_um_cw_testbuffer`, `tt_um_LPCAS_TTGF0P3_TP1`, `tt_um_rahulbhagwat_gf180_bandgap_reference`, `tt_um_odgrip_polywave`. `pfet_05v0` L=0.5u W=3311u nf=301, with an `lv2hv` level shifter (03v3 input inverters, 05v0 cross-coupled stage) and a 05v0 discharge chain. 14.52 x 325.36 um |
| `tt_asw_5v0` | 60 | Analog switch between a project `ua[n]` pin and a shared analog pad bus, one per used analog pin. Transmission gate: `pfet_05v0` L=0.5u W=592u nf=16 and `nfet_05v0` L=0.6u W=217u nf=7, a third `nfet_05v0` L=0.6u W=31u driven by the inverted enable, and the same `lv2hv` level shifter. 40.32 x 30.25 um |
| `tt_ckt_ana` | 22 | Metal2-to-Metal3 contact macro (75 x 5 um) joining each `asig_5p0` pad to its analog bus; the schematic is a 0-ohm resistor |
| wafer.space id macros | 4 | `gf180mcu_ws_ip__logo`, `__project_id`, `__qrcode_id`, `__shuttle_id` |
| Tiny Tapeout logos | 4 | `tt_logo_top`, `tt_logo_bottom`, `tt_logo_corner_tl`, `tt_logo_corner_tr` |

Analog routing: there are 22 analog pads, `analog[0..21]`, on `pad_raw[19..24]`, `[27..32]`, `[58..61]` and `[64..69]` (`ol2/tt_top/tt_gf_wrapper.v`). Pads are shared: each project's `ua[n]` reaches its pad through its own `tt_asw_5v0`, closed only when the project is selected. The assignments in `shuttle_index.json` put up to four projects on one pad (for example pads 12 to 15 serve the MoM capacitor, algofoogle's VCO/DAC, the folded-cascode OTA, and one pin each of the current DAC, the SkullFET oscillator and the R2R DAC). Every analog measurement therefore has one switch on-resistance in series and the off-state capacitance and leakage of the other projects' switches in parallel.

Standard-cell libraries on the die: `gf180mcu_fd_sc_mcu7t5v0` for all synthesised logic, and `gf180mcu_as_sc_mcu7t3v3` (a 3.3 V thin-oxide 7-track library that is not one of the foundry `fd_sc` libraries) in `tt_um_fabulous_gf_0p3_3v3` only. One SRAM macro: `gf180mcu_ocd_ip_sram__sram256x8m8wm1` in `tt_um_essen`.

Verification artefacts are in the release assets: top-level LibreLane run (`GDS.zip`), all hardened macros including every project GDS (`macros.zip`), final GDS/OAS/netlist (`foundry_submission.zip`), gate-level mux simulation (`gl_test_vcd.zip`), and the wafer.space precheck log, run tarball and output GDS/OAS. The precheck log ends "Precheck successfully completed": KLayout density, antenna and DRC report 0 violations; it also carries a non-blocking warning "[Checker.MagicDRC] 2268 Magic DRC errors found". The shuttle's own top-level build has Magic DRC commented out (tt-multiplexer 3a0e0bb: "Tech File is not perfect and triggers false positives"). No silicon bring-up data is in the repo.

### Projects on the shuttle (32)

Author and function are as declared in each project's `info.yaml`; address, analog pad numbers and source commit are from `shuttle_index.json`. "Type" is the declared `language` (analog means a custom-GDS submission).

| Addr | Macro | Title | Author (as declared) | Function | Tiles | Type | Analog pads used | Source repo@commit |
|---|---|---|---|---|---|---|---|---|
| 0 | `tt_um_chip_rom` | Chip ROM | Uri Shaked | ROM with information about the chip | 1x1 | digital | - | TinyTapeout/tt-chip-rom@bb74372 |
| 1 | `tt_um_factory_test` | Tiny Tapeout Factory Test | Tiny Tapeout | Factory test module | 1x1 | digital | - | TinyTapeout/ttgf26a-factory-test@7aea75b |
| 3 | `tt_um_a1k0n_nyancat` | VGA Nyan Cat | Andy Sloane | Displays the classic nyan.cat animation | 1x2 | digital | - | urish/ttgf0p2-a1k0n-nyan@70a13d8 |
| 5 | `tt_um_74hct00` | 74HCT00 Quad 2-Input NAND (3.3 V) | Vipul Sharma | Open-source silicon realization of 74HCT00 TTL-compatible quad 2-input NAND on gf180mcuD at 3.3 V | 1x2 | analog | 21,20,17,18,19 | engrvip123/tt_um_74hct00@ebc3b79 |
| 7 | `tt_um_analog_factory_test` | TT GF180mcuD Analog Factory Test | Sylvain Munaut | Test structures for GF180mcuD analog support | 1x2 | analog | 20,16,21,17,18,19 | smunaut/ttgf_analog_factory_test@c6ca27c |
| 33 | `tt_um_mattvenn_signal_generator` | Simple Signal Generator | Matt Venn | Square wave generator with a phase-shifting second channel for metastability experiments | 1x2 | digital | - | mattvenn/simple-signal-generator@3a0852b |
| 35 | `tt_um_gf_r2r_dac` | GF R2R DAC | Matt Venn | 8 bit R2R DAC | 1x2 | analog | 15 | mattvenn/gf-r2r-dac@1c5c8dd |
| 37 | `tt_um_algofoogle_gf_analog` | algofoogle analog stuff | algofoogle (Anton Maurovic) | Some analog and custom layout experiments in gf180mcuD for ttgf0p3 (the TT GF 1st analog experimental shuttle) | 1x2 | analog | 12,13,14,15 | algofoogle/ttgf0p3-algofoogle-analog@c9b7667 |
| 38 | `tt_um_gojimmypi_ttgfa_UART_FSM_TRNG_Lab` | Hardware Entropy Explorer: UART/SPI TRNG and PUF | gojimmypi | UART/SPI-controlled ASIC lab for exploring true-random number generation and PUF-style hardware entropy sources. | 1x2 | digital | - | gojimmypi/ttgf0p3-UART-FSM-TRNG-Lab@b94bd8a |
| 39 | `tt_um_htfab_momcap` | MoM capacitor | htfab | Simple metal-oxide-metal capacitor for gf180mcuD that fills an analog 1x2 tile | 1x2 | analog | 12,13,14,15 | htfab/ttgf0p3-momcap@b8485bd |
| 99 | `tt_um_coldbrew` | Until heat death do us part | Julia Desmazes | Counting until the heat death of the universe, broadcasting counter value every second over ethernet. | 2x2 | digital | - | Essenceia/Until_Heat_Death_Do_Us_Part@3fd08e8 |
| 101 | `tt_um_cw_testbuffer` | TT GF180mcuD Testbuffer | Christoph Weiser | Analog voltage buffer | 1x2 | analog | 10,8,9 | christoph-weiser/ttgf0p3-submission@72b1962 |
| 102 | `tt_um_fabulous_gf_0p3` | Tiny FABulous FPGA | Leo Moser | A tiny FABulous FPGA fabric, ready for use with Yosys and nextpnr. | 4x4 | digital | - | mole99/tt-fabulous-gf-0p3@61493f1 |
| 103 | `tt_um_tnt_gf_555` | tnt's recreation of a 555 on GF180mcu | Sylvain Munaut | Just a simple classic timer IC re-imagined | 1x2 | analog | 6,7,11,10,9,8 | smunaut/tt_tnt_gf_555@6044f6c |
| 199 | `tt_um_MichaelBell_tinyQV` | TinyQV Risc-V SoC | Michael Bell | A Risc-V SoC for Tiny Tapeout | 4x2 | digital | 0,4,1,3,2 | MichaelBell/ttgf0p3-tinyQV@b5f2925 |
| 256 | `tt_um_essen` | 256x8 SRAM | Julia Desmazes | 256x8 SRAM for testing | 1x2 | digital | - | Essenceia/tt_gf_ocd_sram_test@ff317fa |
| 258 | `tt_um_AbAdA_2048` | Abad2048 | Alexander Co Abad | Colorful 2048 game uploaded successfully to the TT FPGA with game pmod! | 1x2 | digital | - | alexandercoabad/Abad_2048@dfafb82 |
| 260 | `tt_um_rahulbhagwat_gf180_bandgap_reference` | GF BGR | Rahul Bhagwat | Bandgap Reference | 1x2 | analog | 16 | bhagwat-rahul/ttgf180-bandgap-reference@546feb9 |
| 262 | `tt_um_tnt_gf_vco` | Quadrature VCO | Sylvain Munaut | Quadrature VCO with nominal target frequency of 240 MHz | 1x2 | analog | 18,19,20 | smunaut/tt_tnt_gf_vco@a8c2ec2 |
| 288 | `tt_um_combined` | Philippine flag waving | Alexander Co Abad | Philippine flag waving in a DVD-like screensaver with PILIPINAS text in a 7-segment style at the bottom | 1x2 | digital | - | alexandercoabad/PILIPINAS_waving@ee71df3 |
| 290 | `tt_um_kiterai_current_dac` | Analog 4 bit Current DAC | Kiterai | Simple 4 bit current output DAC | 1x2 | analog | 13 | Kiterai/ttgf-practice1@95344ec |
| 292 | `tt_um_LPCAS_TTGF0P3_TP1` | 3.3V Folded Cascode OTA | Pranay Arvind Patil and Nithin Purushothama | NMOS Input pair based Folded Cascode OTA | 1x2 | analog | 12,13,14,15 | chennakeshavadasa/LPCAS_TTGF0P3_TP1@31ee3cd |
| 294 | `tt_um_oscillating_bones` | Oscillating Bones | Uri Shaked | A stylish SkullFET ring oscillator (~120 MHz) with an 8-bit /2../256 divider | 1x2 | analog | 14 | urish/ttgf-oscillating-bones@77f8071 |
| 356 | `tt_um_2048_vga_game` | 2048 sliding tile puzzle game (VGA) | Uri Shaked | Slide numbered tiles on a grid to combine them to create a tile with the number 2048. | 3x2 | digital | - | urish/tt-2048-game@b45898a |
| 358 | `tt_um_gojimmypi_ttgfa_UART_FSM_TRNG_Lab_analog` | Hardware Entropy Explorer: UART/SPI TRNG and PUF (Analog) | gojimmypi | UART/SPI-controlled GF180 analog lab with DAC, threshold sampling, TRNG monitors, and measured ua5 passive probe. | 1x2 | analog | 6,11,7,10,8,9 | gojimmypi/ttgf0p3-analog-UART-FSM-TRNG-Lab@3f7c4a5 |
| 359 | `tt_um_fabulous_gf_0p3_3v3` | Tiny FABulous FPGA (3.3V version) | Leo Moser | A tiny FABulous FPGA fabric, ready for use with Yosys and nextpnr. | 4x4 | digital | - | mole99/tt-fabulous-gf-0p3-3v3@9009473 |
| 448 | `tt_um_waferspace_vga_screensaver` | Wafer.space Logo VGA Screensaver | Uri Shaked | Wafer.space Logo bouncing around the screen (640x480, TinyVGA Pmod) | 1x2 | digital | - | TinyTapeout/tt-waferspace-vga-screensaver@ef9a2f0 |
| 450 | `tt_um_urish_usb_cdc` | USB CDC (Serial) Device | Uri Shaked | USB to UART bridge, 115200 baud rate | 1x2 | digital | - | urish/tt-usbcdc-device@2943e52 |
| 452 | `tt_um_odgrip_polywave` | PolyWave | Riccardo Pellegrini | Mixed-signal four-channel waveform source with a compact digital engine driving four 16-bit R-2R DACs. | 1x2 | analog | 4,1,3,2 | ODGrip/ttgf-polywave@a665c8f |
| 454 | `tt_um_mcml_vco` | MCML VCO | Namibj | An MCML VCO | 1x2 | analog | 0,5,2,3,1,4 | namibj/tt_gf-0p3_mcml@a82f3d3 |
| 518 | `tt_um_kianV_rv32ima_uLinux_SoC` | KianV uLinux SoC | Hirosh Dabui | A RISC-V ASIC that can boot μLinux. | 4x4 | digital | - | TinyTapeout/KianV-RV32IMA-RISC-V-uLinux-SoC@a55d169 |
| 519 | `tt_um_urish_simon` | Simon Says memory game | Uri Shaked | Repeat the sequence of colors and sounds to win the game | 1x1 | digital | - | urish/tt-simon-game@3a0a46f |

Analog pad numbers above are `analog[k]` indices, not `ua[n]` order; the list is in `ua[0], ua[1], ...` order. `tt_um_MichaelBell_tinyQV` uses one analog pin functionally (`ua[0]`, the DAC output); the other four were added by the shuttle operator to shorten an enable wire ("extra analog pins to prevent antenna violations", commit 2771233).

Device content of the analog macros below was read from the cell names and layers of each project's GDS in `macros.zip` (3.3 V thin-oxide = no Dualgate layer; 5 V/6 V = Dualgate and V5_XTOR present). Device sizes are not in this repo.

**Analog and custom-layout projects**

- **`tt_um_analog_factory_test`** (addr 7, Sylvain Munaut). Purpose-built infrastructure test: two large current-mirror loads (`mirror_load` x2, 5 V devices, with an `lv2hv` shifter) that multiply a reference current on `ua[0]` by about 50 and draw it from VDPWR or VAPWR (`ui[0]`, `ui[1]`), with Kelvin sense lines for VGND, VDPWR and VAPWR on `ua[1..3]` and a pad-to-pad loopback on `ua[4]`/`ua[5]`. Measures the IR drop of the power distribution and of the 3.3 V and 5 V power gates under a known load, and (through the loopback) two analog switches in series.
- **`tt_um_htfab_momcap`** (addr 39, htfab). Interdigitated metal-oxide-metal capacitor filling a 1x2 tile, terminals on `ua[0]`/`ua[1]`, two dummy terminals on `ua[2]`/`ua[3]` for de-embedding. GDS contains only metal and via layers, almost all of it Metal4 (62 Metal4 shapes against 2 each on Metal1 to Metal3), so this is mainly a Metal4 lateral capacitor (inferred from shape counts). Docs: magic extraction estimates about 85 pF. The upstream repo is said to contain a generator script.
- **`tt_um_rahulbhagwat_gf180_bandgap_reference`** (addr 260, Rahul Bhagwat). Bandgap reference: `npn_05p00x05p00` x2, `pfet_03v3` x10, `nfet_03v3` x5, `ppolyf_u_1k` x3, error amplifier and over-voltage clamp sub-cells; uses a deep N-well and the BJT marker layers. Output VBGR on `ua[0]`, supplied from VAPWR through the 5 V gate at 3.3 V. Docs: 1.674 V to 1.697 V from -40 C to 125 C in typical-corner simulation, no trimming.
- **`tt_um_tnt_gf_vco`** (addr 262, Sylvain Munaut). 4-stage differential delay-cell VCO (`vco_dly` x4, current mirror, control cell, two output comparators), 3.3 V devices. Nominal 240 MHz, expected tuning range about 120 MHz to 500 MHz. Phases 0 and 270 on digital `uo[0]`, `uo[1]`; phases 180 and 90 on `ua[0]`, `ua[1]`; control voltage on `ua[2]`.
- **`tt_um_mcml_vco`** (addr 454, Namibj). MOS current-mode-logic VCO: `nfet` x6, `vco_core_segment` x4, `ppolyf_u_high_Rs_resistor` x2, no PMOS (no Nwell in the GDS). Two tail-bias inputs on `ua[0]`, `ua[1]`, two differential clock outputs on `ua[2..5]`. The docs are the unfilled template.
- **`tt_um_oscillating_bones`** (addr 294, Uri Shaked). 21-stage ring oscillator of hand-drawn skull-shaped 3.3 V MOSFET inverters ported from an IHP sg13g2 design by 1.45x scaling, one more as an output buffer on `ua[0]`, and an 8-stage `dffrnq` divider on `uo[0..7]`. Docs: about 120 MHz in post-layout simulation (magic extraction, gf180mcuD ngspice models), unchanged for 0 to 10 pF on `ua[0]`. Non-standard transistor geometry, so a test of how well the models and extraction hold for unusual layouts.
- **`tt_um_algofoogle_gf_analog`** (addr 37, Anton Maurovic). 5-stage current-starved ring-oscillator VCO (`csringosc`, `csrostage`, `nfet_03v3`, custom `inv_P15_N4p5` inverters), control on `ua[0]`, output on `ua[1]`, expected 2 MHz to 400 MHz for 0.55 V to 3.3 V. A second copy driven by an on-chip R-2R DAC (`r2r_dac_R24_P15_N4p5`, `ppolyf_u_1k`) with its control node and output on `ua[2]`, `ua[3]`. Divided outputs on `uio[0..5]`. Also contains artwork cells (`lily_pics`, `m4screen`) and a synthesised controller.
- **`tt_um_tnt_gf_555`** (addr 103, Sylvain Munaut). CMOS 555 re-creation: two OTAs (N and P input), a reference (`ref_nmos_vth`, `ref_res`, `ref_nmos_drv`), resistor divider, `ppolyf_u_1k`, `nmoscap_3p3`, Schmitt inverters, NMOS/PMOS output drivers; Dualgate (5 V) devices on part of the layout; on VAPWR through the 5 V gate. Threshold, trigger, reset, control, out and discharge on `ua[0..5]`; an on-chip oscillator configuration on `uo[0]`/`uio[0]`.
- **`tt_um_cw_testbuffer`** (addr 101, Christoph Weiser). Op-amp voltage buffer built from `nfet_06v0` and `pfet_06v0` devices with a `ppolyf_u_1k_6p0` resistor and a compensation capacitor cell. Input `ua[0]`, 5 uA bias `ua[1]`, output `ua[2]`. The docs carry a full simulated specification table across PVT (supply current 47.9 / 50.6 / 57.5 uA, open-loop gain 85.9 dB typ, UGBW 2.6 MHz typ, offset 10.2 mV 3-sigma, noise densities, PSRR, slew rate). This is the best-documented simulation target on the die.
- **`tt_um_LPCAS_TTGF0P3_TP1`** (addr 292, Pranay Arvind Patil and Nithin Purushothama). Folded-cascode OTA, 3.3 V devices, about 15 uA, UGB about 100 kHz, output swing 0.5 V to 3.0 V. VINN, VINP, VBIAS, VOUT on `ua[0..3]`. The `info.yaml` description says NMOS input pair; the body of `docs/info.md` describes a PMOS input pair. The GDS is flattened (1 cell), so this could not be settled from the layout.
- **`tt_um_gf_r2r_dac`** (addr 35, Matt Venn). 8-bit R-2R DAC with poly resistors and a synthesised sine generator / external-data mux; output `ua[0]`. The same `r2r` macro (`ppolyf_u_1k`) is instantiated inside `tt_um_MichaelBell_tinyQV` (addr 199) as a memory-mapped peripheral, output on that project's `ua[0]`.
- **`tt_um_odgrip_polywave`** (addr 452, Riccardo Pellegrini). Four 16-bit R-2R ladders (16 `r2r_unit` references in the GDS) driven by a synthesised waveform engine; direct-write mode lets any 16-bit code be loaded. Outputs `ua[0..3]`. Usable for resistor-matching and DAC linearity measurements.
- **`tt_um_kiterai_current_dac`** (addr 290, Kiterai). 4-bit current-sink DAC, NMOS only (no Nwell in the GDS), code on `ui[3:0]`, sink output on `ua[0]`.
- **`tt_um_74hct00`** (addr 5, Vipul Sharma). Quad 2-input NAND with TTL-compatible input thresholds built from skewed inverters, a NOR2 and an output inverter, full-custom 3.3 V devices, sized for +/-4 mA. All four outputs on `ua[0..3]` and one input on `ua[4]` so the input transfer curve and VOH/VOL under load can be measured without the pad buffers. Docs say xschem schematics and ngspice simulations exist upstream.
- **`tt_um_gojimmypi_ttgfa_UART_FSM_TRNG_Lab_analog`** (addr 358, gojimmypi). Synthesised ring-oscillator TRNG/PUF lab (all `gf180mcu_fd_sc_mcu7t5v0` cells) with the six analog pads used as threshold-sampled inputs, a 1-bit sigma-delta output and monitor outputs, plus a small Metal4 fringe/pickup structure on `ua[5]` whose charge decay is timed by the logic. The author states it is "not a precision analog macro". The all-digital sibling is at addr 38.

**Digital projects of process interest**

- **`tt_um_essen`** (addr 256, Julia Desmazes). Test wrapper around the Open Circuit Design SRAM macro `gf180mcu_ocd_ip_sram__sram256x8m8wm1` (upstream repo `Essenceia/tt_gf_ocd_sram_test`): registered address, data in, write enable and data out. Only 128 of the 256 words are reachable (7 address bits on `ui[0..6]`; the docs say "6 bits of address" in one place and "top 128 entries" in another). The SRAM sub-cells carry the `3v256x8m81` suffix and the macro GDS has no Dualgate layer beyond the standard cells around it, so this is a 3.3 V thin-oxide bit cell (inferred).
- **`tt_um_fabulous_gf_0p3`** (addr 102) and **`tt_um_fabulous_gf_0p3_3v3`** (addr 359) (Leo Moser). The same 64-LUT4 FABulous eFPGA fabric (6x4 tiles, latch-based configuration, bit-banged bitstream) hardened twice: once on `gf180mcu_fd_sc_mcu7t5v0`, once on `gf180mcu_as_sc_mcu7t3v3`. A direct same-design comparison of the two cell libraries, except that the 3.3 V version instantiates `gf180mcu_as_sc_mcu7t3v3__buff_8`, which the shuttle operators flagged after tapeout as containing a short; its danger level is `high` ("will damage the ASIC").
- **`tt_um_mattvenn_signal_generator`** (addr 33, Matt Venn). Two square-wave channels with sub-cycle programmable phase offset, intended as a stimulus for metastability experiments on other chips.
- **`tt_um_gojimmypi_ttgfa_UART_FSM_TRNG_Lab`** (addr 38). Bank of synthesised ring oscillators as an entropy source, readable over UART/SPI.
- **`tt_um_factory_test`** (addr 1). IO mirror and counter; reference for the digital pad path.

The remaining projects (chip ROM, TinyQV, KianV, 2048 x2, Nyan Cat, Simon, USB CDC, screensaver, flag demo, `tt_um_coldbrew`) are ordinary synthesised logic on the 7-track cells.

## Authors and affiliations

| Person or organisation | Role | Affiliation | Source |
|---|---|---|---|
| Tiny Tapeout (org `TinyTapeout`) | Shuttle operator, repo owner | Tiny Tapeout, tinytapeout.com | `gh api orgs/TinyTapeout`, README |
| Uri Shaked (`urish`) | Shuttle integration (293 commits); SkullFET oscillator, chip ROM, Simon, 2048, USB CDC, screensaver | Tiny Tapeout / Wokwi (GitHub bio) | `git shortlog`, `gh api users/urish` |
| Sylvain Munaut (`smunaut`) | tt-multiplexer author; designed and laid out all GF180 power gates, the analog switch and pad contact; analog factory test, 555, quadrature VCO; 5 integration commits incl. the danger-level entry | not stated | `pg/gf180mcuD/README.md`, `asw/gf180mcuD/README.md`, copyright headers, `git shortlog` |
| Matt Venn (`mattvenn`) | R2R DAC, signal generator | YosysHQ and Tiny Tapeout (GitHub profile) | `info.yaml`, `gh api users/mattvenn` |
| htfab | MoM capacitor; 10 integration commits | not stated | `info.yaml`, `git shortlog` |
| Leo Moser (`mole99`) | Both FABulous FPGA tiles | not stated; location Austria | `info.yaml`, `gh api users/mole99` |
| Julia Desmazes (`Essenceia`) | OCD SRAM test, `tt_um_coldbrew` | not stated; location Austin | `info.yaml`, `gh api` |
| Anton Maurovic (`algofoogle`) | Current-starved VCO and DAC | not stated; Adelaide | `info.yaml`, `gh api` |
| Christoph Weiser | Test buffer op-amp | not stated | `info.yaml` |
| Rahul Bhagwat | Bandgap reference | not stated | `info.yaml` |
| Namibj | MCML VCO | not stated | `info.yaml` |
| Pranay Arvind Patil, Nithin Purushothama (`chennakeshavadasa`) | Folded-cascode OTA | not stated ("LPCAS" in the repo and macro name is not expanded anywhere in this repo) | `info.yaml` |
| Riccardo Pellegrini (`ODGrip`) | PolyWave 4x16-bit DAC | not stated | `info.yaml` |
| Vipul Sharma (`engrvip123`) | 74HCT00 | not stated; India | `info.yaml`, `gh api` |
| Kiterai | Current DAC | not stated | `info.yaml` |
| gojimmypi | TRNG lab, digital and analog versions | "Contractor" (GitHub company field), California | `gh api users/gojimmypi` |
| Michael Bell, Hirosh Dabui, Andy Sloane, Alexander Co Abad | Digital projects (TinyQV, KianV, Nyan Cat, 2048 and flag demos) | not stated | `info.yaml` |
| Open Circuit Design | Source of the `gf180mcu_ocd_io` pad library and `gf180mcu_ocd_ip_sram` macro | named in `tt_um_essen/docs/info.md` ("Open Circuit Design 256x8 SRAM"); the `ocd` prefix on the pad library is read the same way (inferred) | project docs, cell names |
| Tillitis, Wit | Funded GF180mcuD support in Tiny Tapeout | sponsors | `docs/funding.typ` |

The origin of `gf180mcu_as_sc_mcu7t3v3` is not stated in this repo.

## Value for GF180MCU characterisation and PDK development

### Verdict: High

Sixteen custom analog layouts with direct analog-pad access (a MoM capacitor, a bandgap, three VCOs and two ring oscillators, an op-amp buffer, an OTA, a 555, R-2R and current DACs, a full-custom logic gate), a purpose-built power-distribution test tile, an SRAM macro test, and one FPGA design hardened on two different standard-cell libraries. Several come with stated simulation numbers to compare silicon against.

### Test structures and measurable circuits

Domains: "3.3 V" means thin-oxide `*_03v3` devices on VDPWR (through the project's `tt_pg_3v3` gate); "5 V" means `*_05v0`/`*_06v0` devices, mostly on VAPWR. All access is through the mux: select the project, then use the listed pads. Analog pads go through one `tt_asw_5v0` each.

| Structure | Exercises | Access | Sim reference in this repo |
|---|---|---|---|
| Current-mirror loads with rail sense (`tt_um_analog_factory_test`) | Power-gate and grid IR drop on VDPWR and VAPWR, 05v0 mirror ratio, analog switch + pad resistance via loopback | addr 7; `ua[0]` iref, `ua[1..3]` sense, `ua[4..5]` loopback, `ui[0..1]` enables | None; "about 50x" only |
| MoM capacitor (`tt_um_htfab_momcap`) | Metal4 lateral/fringe capacitance (mostly), extraction accuracy of magic | addr 39; `ua[0]`, `ua[1]`, dummies `ua[2]`, `ua[3]` | About 85 pF (magic extraction) |
| Bandgap (`..._bandgap_reference`) | `npn_05p00x05p00` Vbe and temperature slope, `ppolyf_u_1k` ratio and TC, `pfet_03v3` matching | addr 260; `ua[0]` | 1.674 V to 1.697 V, -40 C to 125 C typical; plot `docs/vbgr-simulation-curve.png` |
| Quadrature VCO (`tt_um_tnt_gf_vco`) | 03v3 delay-cell speed versus control voltage | addr 262; `ua[2]` control, `uo[0..1]`, `ua[0..1]` outputs | 240 MHz nominal, 120 MHz to 500 MHz range |
| MCML VCO (`tt_um_mcml_vco`) | NMOS current-mode logic with `ppolyf_u_high_Rs` loads: high-Rs poly sheet resistance, nfet gm | addr 454; `ua[0..1]` bias, `ua[2..5]` differential outputs | None |
| SkullFET ring oscillator (`tt_um_oscillating_bones`) | 03v3 models and extraction on non-standard transistor geometry | addr 294; `ua[0]` raw, `uo[0..7]` /2 to /256 | About 120 MHz post-layout; plot `docs/layout_sim.png` |
| Current-starved ring VCO x2 (`tt_um_algofoogle_gf_analog`) | `nfet_03v3` in subthreshold to strong inversion (0.55 V to 3.3 V control), custom inverter delay; `ppolyf_u_1k` R-2R ladder | addr 37; `ua[0]` vin, `ua[1]` out, `ua[2..3]` DAC-driven copy, `uio[0..5]` divided | 2 MHz to 400 MHz expected |
| Op-amp buffer (`tt_um_cw_testbuffer`) | `nfet_06v0`/`pfet_06v0` gm, matching (offset), 1/f noise, `ppolyf_u_1k_6p0` | addr 101; `ua[0]` in, `ua[1]` 5 uA bias, `ua[2]` out | Full PVT spec table in `docs/info.md` |
| Folded-cascode OTA (`tt_um_LPCAS_TTGF0P3_TP1`) | 03v3 analog performance at about 15 uA | addr 292; `ua[0..3]` | Target figures in prose only |
| CMOS 555 (`tt_um_tnt_gf_555`) | Comparator offsets, Vth-based reference, `ppolyf_u_1k` divider, `nmoscap_3p3`, output driver strength | addr 103; `ua[0..5]`, `uo[0]`, `uio[0]` | None |
| R-2R DACs: 8-bit (`tt_um_gf_r2r_dac`, also inside tinyQV), 4 x 16-bit (`tt_um_odgrip_polywave`) | Poly resistor matching (INL/DNL), switch resistance | addr 35 `ua[0]`; addr 199 `ua[0]`; addr 452 `ua[0..3]` | None |
| 4-bit current-sink DAC (`tt_um_kiterai_current_dac`) | NMOS mirror matching and output conductance | addr 290; `ui[3:0]`, `ua[0]` | None |
| 74HCT00 (`tt_um_74hct00`) | Full-custom 03v3 inverter transfer curve (skewed threshold), drive at +/-4 mA | addr 5; input `ua[4]`, outputs `ua[0..3]` | Stated to exist upstream; not in this repo |
| Metal4 fringe structure with decay timer (gojimmypi analog) | Pad plus switch leakage and capacitance, coarse | addr 358; `ua[5]`, register R15 | None |
| OCD 256x8 SRAM (`tt_um_essen`) | Bit-cell function, access time (registered both sides, so only by clock-frequency sweep), retention | addr 256; `ui`, `uio`, `uo` | None |
| FABulous FPGA on 7t5v0 versus on `as_sc_mcu7t3v3` | Same netlist on two libraries: relative speed and power of 5 V-rated and 3.3 V cells | addr 102, addr 359 (flagged `high` danger) | None |
| Synthesised ring-oscillator bank (gojimmypi digital) | 7t5v0 cell delay, jitter | addr 38; UART/SPI | None |
| Infrastructure: `tt_pg_3v3_hp_*`, `tt_pg_5v0_2`, `tt_asw_5v0` | `pfet_03v3` and `pfet_05v0` switch Ron and off leakage; 05v0 transmission-gate Ron versus signal voltage | Indirect: supply current selected versus deselected; factory-test tile; any analog pad pair | Testbench schematics only (`tb_rdson.sch`, `tb_switch.sch`); no result files |
| `gf180mcu_ocd_io` pads | `bi_24t`, `in_c`, `in_s`, `asig_5p0` in a non-foundry pad library | pads | None |

### Candidate PDK additions

- **Power-gate macros** `tt_pg_3v3_hp_1`, `tt_pg_3v3_hp_2`, `tt_pg_3v3_hp_4`, `tt_pg_5v0_2`: complete sources (xschem, magic, GDS, LEF, Verilog model) under `tt-multiplexer/pg/gf180mcuD/`, Apache-2.0.
- **Analog switch** `tt_asw_5v0` with its 3.3 V-to-5 V level shifter `lv2hv`, and the pad contact `tt_ckt_ana`: sources under `tt-multiplexer/asw/gf180mcuD/`.
- **`gf180mcu_as_sc_mcu7t3v3`**: a 3.3 V 7-track standard-cell library used in anger for a 4x4-tile FPGA. 39 distinct cells appear in the layout (and2, ao*, aoi*, buff, clkbuff, dfxtp, dlxfp, maj3, mux2, nand*, nor*, oai211, or2, xnor2, tiel, tap, diode, fill, fillcap). The reported short in `buff_8` is a concrete library bug to check before the library goes anywhere near the PDK; the fixed version is not referenced here.
- **`gf180mcu_ocd_ip_sram__sram256x8m8wm1`** and **`gf180mcu_ocd_io`**: both taped out here; this shuttle is silicon evidence for them.
- **MoM capacitor generator** (htfab), **R-2R DAC** (Matt Venn, reused by a second project), **bandgap**, **op-amp buffer** with a characterised spec table: reusable analog blocks, sources upstream.
- **PDK/flow problems the authors hit**: Magic DRC disabled at top level because the tech file "is not perfect and triggers false positives" (and 2268 Magic DRC errors reported in the wafer.space precheck against a KLayout-clean layout); `MAGIC_EXT_SHORT_RESISTOR` and `MAGIC_EXT_UNIQUE: notopports` needed for LVS; "Move DUMMY to DRAWING" fix applied to the bandgap layout (commit 1a81e7f); antenna violations on the long analog-switch enable wire worked around by adding analog pins (2771233); "Hack for gf180mcuD" commits across `rtl`, `tt_ctrl`, `tt_mux`, `tt_top` in tt-multiplexer; forked LibreLane branch `dev-tt-gf26`.

### What would be needed to use it

- Packaged parts on a board that drives the three mux control pads and breaks out the 22 analog pads and the separate core, IO and analog supplies. No GF 0p3 board documentation is in this repo.
- For the DC structures (bandgap, DACs, current DAC, factory test, 74HCT00, OTA, buffer): source-measure units, a 6.5-digit DMM, a temperature chamber for the bandgap. For the VCOs and ring oscillators: an oscilloscope or spectrum analyser good to 500 MHz and low-capacitance probing on the analog pads; `asig_5p0` pad and switch capacitance will load the raw outputs. For the MoM capacitor: an LCR meter or VNA, using the dummy terminals to de-embed.
- A characterisation of the analog path itself first (`tt_asw_5v0` Ron and the shared-bus parasitics), most easily with the factory-test loopback, since every other analog number depends on it.
- The upstream repos for schematics, SPICE netlists and testbenches; without them only the figures quoted in `docs/info.md` are available for comparison. Per-project test plans are thin: several analog docs are one or two lines and `tt_um_mcml_vco` has none.
- Do not select address 359 (`tt_um_fabulous_gf_0p3_3v3`) on a part you want to keep; power gating should keep it isolated while deselected.

## Notes and caveats

- The `sha256` in `project.json` (`da186a23...`, for `T0P3/tt_gf_wrapper.oas`) matches none of the three layout files in the release (`tt_gf_wrapper.oas` `592efeb6...`, precheck output `.oas` `2af579de...`, precheck output `.gds` `e7bfbe93...`). The submitted file may have been a different serialisation of the same layout; not resolved.
- `main` is one commit past the tag: the `danger_level.yaml` entry for the 3.3 V FPGA (authored 2026-07-15, committed 2026-09-14). The commit title says "3v3 SCL projects" in the plural; only one project is listed and only one uses that library.
- That commit is the only statement of the `buff_8` short; no detail on the failure mechanism or which library revision is affected is in this repo.
- The 56 other remote branches are per-project CI import branches; there is no alternative shuttle configuration on another branch.
- Project layouts in git are compressed OASIS; device content was read from the per-project GDS files in `macros.zip` using cell names and layer presence. Flattened macros (`tt_um_LPCAS_TTGF0P3_TP1`, `tt_um_kiterai_current_dac`, the infrastructure macros) give layers only. No LVS or extraction was run.
- The description of which projects share which pads comes from `shuttle_index.json`; the physical bus routing was not traced.
- The analog rail voltage is not fixed by the repo: the gates and switches are named 5v0 and built from `*_05v0` devices, while individual projects document 3.3 V operation (bandgap, 74HCT00) or 3.0 V to 5.0 V (test buffer). 3.3 V-only analog projects sit behind 5 V-capable switches.
- Power-gate and analog-switch enables are driven per project by `tt_mux` (`um_pg_ena`); that they follow project selection is inferred from the RTL port names, not simulated.
- `tt_um_MichaelBell_tinyQV` lists `git@github.com:MichaelBell/ttgf0p3-tinyQV.git` as its source in the index (an SSH URL, unlike the others).

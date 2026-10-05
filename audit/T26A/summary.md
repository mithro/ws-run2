# T26A: Tiny Tapeout GF 26a (ws-run2)

| | |
|---|---|
| Repository | https://github.com/TinyTapeout/tinytapeout-gf-26a @ 35e7026 (main, last commit 2026-06-22; tag `tapeout-ws2607` is the same commit) |
| Slot | 1x1 (die 3932 x 5122 um per `tt-multiplexer/cfg/gf180mcuD.yaml`) |
| Top cell | tt_gf_wrapper |
| Licence in repo | Apache-2.0 (`LICENSE`; each `projects/*/LICENSE` is the submitter's own) |
| README | Thin (74 words, points at tinytapeout.com and the multiplexer docs) |

## What the repo actually contains

A Tiny Tapeout multi-project shuttle: 95 user macros (93 user designs plus the
`tt_um_chip_rom` and `tt_um_factory_test` infrastructure tiles) filling all 160
tile slots of an 8 x 20 grid, behind the Tiny Tapeout multiplexer. The repo is
an assembly repo, not a design repo: user RTL/schematics are **not** here.

- `projects/<macro>/`: for every user design the hardened deliverables only:
  `<macro>.oas` (layout), `<macro>.lef`, `<macro>.v` (gate-level netlist, or a
  blackbox stub for custom-GDS designs), `info.yaml` (title, author, pinout),
  `docs/info.md` (datasheet text), `commit_id.json` (source repo + commit +
  GitHub Actions run), `pdk.json` (flow and PDK version), `stats/metrics.csv`
  and `stats/synthesis-stats.txt` (LibreLane metrics incl. STA at
  `nom_{tt_025C_3v30, ss_125C_3v00, ff_n40C_3v60}`). `tt_um_chip_rom` has no
  layout in the repo (generated at build time by `tt/rom`).
- `tt-multiplexer/` (submodule @ b6bed69, Sylvain Munaut, a branch of
  `[gf] [HACK]` commits dated 2025-11/12): mux/controller RTL, GF180 primitive
  wrappers (`rtl/prim_gf180mcuD/`), pad wrapper `rtl/tt_gf_gpio.v`, top
  `ol2/tt_top/tt_gf_wrapper.v`, LibreLane build scripts, and the pre-built
  power-gate macros `ol2/tt_top/{gds,lef,verilog}/tt_pg_3v3_hp_{1,2,4}`.
- `tt/` (submodule tt-support-tools @ d4626aa): shuttle tooling, precheck,
  `tech/gf180mcuD/` (tile sizes, cell defs, logo generator).
- `gf180mcu/` (submodule wafer-space/gf180mcu @ cae6f09): a PDK snapshot built
  from open_pdks 40cee97 with `gf180mcu_ocd_io` imported and a commit titled
  "libs.tech/librelane: Hack to get the new IO library to play nice".
- `librelane/` (submodule @ e2f0b0e).
- `verilog/dv/mux/` cocotb mux test, `verilog/rtl/tt_um_factory_test.v`.
  `verilog/gl/` is empty in the repo.
- `docs/`: two Typst snippets and two renders (`full_gds.png`,
  `logic_density.png`). `docs/funding.typ` states GF180 support was funded by
  Tillitis and Wit and "manufacturing of Tiny Tapeout GF 0p2 silicon was funded
  by wafer.space" (text carried over from an earlier shuttle).

Release `tapeout-ws2607` ("Wafer Space 2607 (G802) Tapeout") holds the final
artefacts: `tt_gf_wrapper.oas`, `foundry_submission.zip` (GDS, OAS, gate-level
`tt_gf_wrapper.v`/`.nl.v`, `shuttle_index.json`, README index),
`macros.zip` (every macro GDS/LEF as used, plus `cfg/modules_placed.yaml`),
`GDS.zip`, `gl_test_vcd.zip` (gate-level mux test VCD + `results.xml`), and the
wafer.space precheck log, output GDS/OAS and `runs.tar`.

### Shuttle infrastructure (identical in 26a and 26b)

| Item | What is used | Evidence |
|---|---|---|
| Standard cells (mux, ctrl, almost all users) | `gf180mcu_fd_sc_mcu7t5v0` (7-track, 5 V-rated devices) operated at **3.3 V** core; STA corners tt_025C_3v30 / ss_125C_3v00 / ff_n40C_3v60 | `tt-multiplexer/ol2/tt_top/build.py` (`VDD_PIN_VOLTAGE: 3.3`), `rtl/prim_gf180mcuD/*.v` |
| IO cells | `gf180mcu_ocd_io` (not `gf180mcu_fd_io`): 16x `bi_24t`, 10x `in_c`, 3x `in_s`, 29x `asig_5p0`, 4x `dvdd`, 6x `dvss`, 2x `vdd`, 4x `vss`, 4x `cor`, fillers | instance count in `foundry_submission.zip:verilog/gl/tt_gf_wrapper.nl.v`; `rtl/tt_gf_gpio.v` |
| Pads | 74 pads: 3 control (`ctrl_ena`, `ctrl_sel_inc`, `ctrl_sel_rst_n`, Schmitt inputs with pull), `clk`, `rst_n`, `ui[7:0]` (CMOS inputs), `uo[7:0]` (24 mA outputs), `uio[7:0]` (24 mA bidir), 22 `analog[]` pads, 5 reserved NC, power/ground | `ol2/tt_top/tt_gf_wrapper.v` |
| Mux | `tt_ctrl` x1 + `tt_mux` x15, address = `mux_id*32 + blk_id`; tri-state spine built from `bufz_1/bufz_12`, `mux2_2/mux4_2`, `dffrnq_2` | `tt_gf_wrapper.nl.v`, `rtl/tt_mux.v`, `rtl/tt_ctrl.v` |
| Power gating | Every user macro (including chip_rom and factory_test) has its own header switch `tt_pg_3v3_hp_{1,2,4}` (72/21/2 instances) between `vdpwr` and the tile's `VPWR`, enabled by `pg_ena` from the mux. The switch GDS has no Dualgate (55/0) layer, so it is built from 3.3 V thin-oxide devices (inferred from layers; no schematic in repo). No analog-supply gate (`pg_vaa: false` everywhere; `tt_pg_5v0` is named in the config but not instantiated). | `macros.zip:cfg/modules_placed.yaml`, `ol2/tt_top/gds/tt_pg_3v3_hp_*.gds` |
| Analog pin routing | **None.** `cfg/gf180mcuD.yaml` has `analog: []`; the 22 `asig_5p0` analog pads are bonded out (`ASIG5V` to `pad_raw[n]`) but have no connection into the core, and the two "VDD Analog" pads are unconnected `asig_5p0` cells. No user project declares `analog_pins > 0`. | `tt_gf_wrapper.nl.v`, all `info.yaml` |
| ID/logo | `gf180mcu_ws_ip__id`, `gf180mcu_ws_ip__logo` (wafer.space template 1.3.1), four `tt_logo_*` art macros | `BUILDING.md`, `build.py` |

User designs were hardened in each submitter's own repo by the Tiny Tapeout
GitHub action: 92 of 95 with LibreLane (73x 3.0.3, 17x 3.0.0, one 3.0.0.dev44,
one 2.4.2) against open_pdks 5443591 (two against other open_pdks commits);
two are `custom_gds` submissions.

### User projects (all 95, by mux address)

"Cell instances" counts every `gf180mcu_*` instance in the gate-level netlist,
including fill, tap and endcap cells (an empty 1x1 tile is about 1250).

| Addr | Macro (tiles) | Title | Author (as declared) | Function | Source repo | Std cells | Note |
|---|---|---|---|---|---|---|---|
| 0 | `tt_um_chip_rom` (1x1) | Chip ROM | Uri Shaked | ROM with information about the chip | TinyTapeout/tt-chip-rom | - | infrastructure; no layout in repo (hardened at build time by tt/rom) |
| 1 | `tt_um_factory_test` (1x1) | Tiny Tapeout Factory Test | Tiny Tapeout | Factory test module | TinyTapeout/ttgf26a-factory-test | 1356 | infrastructure IO loopback/counter |
| 3 | `tt_um_AlvaroRub_ringcounter` (1x1) | Counter16Outputs | Alvaro Rubio | A 16-bit ring counter that sequentially activates its outputs at the clock rate. | AlvaroRub/tt-alvaros-first-wokwi | 1365 |  |
| 5 | `tt_um_peg_top` (1x1) | 2x2 CNN Accelerator PE Grid with UART | Vidhyanandhan Sathishkumar | UART-controlled 2x2 systolic processing-element grid for CNN inference. Send 3-byte packets over UART to drive activations/weights; receive 2-byte ... | Vidhyanandhan-01/tinytapeout-gf | 2843 |  |
| 7 | `tt_um_systolic_mac_2x2` (1x1) | 2x2 Systolic Array Matrix Multiplier | Irene-ux | 2x2 output-stationary systolic array for signed 4-bit matrix multiply on GF180 | Irene-ux/tt-systolic-array-2x2 | 2937 |  |
| 32 | `tt_um_rebeccargb_hardware_utf8` (1x1) | Hardware UTF Encoder/Decoder | Rebecca G. Bettencourt | Converts Unicode code points between UTF-8, UTF-16, and UTF-32. | RebeccaRGB/ttgf-hardware-utf8 | 3118 |  |
| 34 | `tt_um_systolic_array` (1x2) | 2x2 MAC Systolic array with DFT | Vijay Sharma | 2x2 multiply and accumulate systolic array supporting signed 8 bit values with design for test infrastructure. | Eulerianial/tt_gf_systolic_array | 6210 |  |
| 36 | `tt_um_hydrocomms` (1x2) | FSK Modem | Vaishnavi V | FSK modem for underwater acoustic communication (46-56 kHz, 100 bps) | vvedn/hydrocomms-tt | 6431 |  |
| 38 | `tt_um_santhosh_rsd_char_gf` (1x2) | RRAM Characterization Platform (DC sweep + endurance + retention + histogram, GF180) | Prof. Santhosh Sivasubramani, IIT Delhi | GF180mcuD standalone characterization platform for one external resistive-switching device (RRAM / memristor / PCM). Drives an 8-bit DAC rail and r... | SanthoshSivasubramani/tt_um_santhosh_rsd_char_gf_pub | 5923 | digital controller for external RRAM + external DAC/ADC |
| 39 | `tt_um_prem_pipeline_test` (4x4) | Programmable_Pipeline-RISC-V | Prem | Zero to ASIC demo project | PrmBRana/ttgf_prem_programmable_RISC_v | 58688 |  |
| 65 | `tt_um_wokwi_465731440267947009` (1x1) | Antonio's first Wokwi design | Antonio | An elite project | aglcoin04/tt-antonios-first-wokwi | 1272 | Wokwi |
| 66 | `tt_um_wokwi_465731403724006401` (1x1) | sdft wokwi 1 | Santiago Díaz Fernández de la Torre | some bs | santidft/tt-sdft-wokwi-1 | 1282 | Wokwi |
| 67 | `tt_um_wokwi_465732706576877569` (1x1) | Guille's first Wokwi design. | Guillermo | Proyecto elite. | guillermomillansolis-rgb/tt-guilles-first-wokwi | 1282 | Wokwi |
| 68 | `tt_um_line_follower_arvaloez` (1x1) | Line Follower Robot controller | Escuela Colombiana de Ingenieria Julio Gravito | Basic controller for a line follower of 8 sensors | Arvaloez/ECI_SEGUIDOR_LINEA_IEEE_BOOTCAMP | 1749 |  |
| 69 | `tt_um_wokwi_465731481873367041` (1x1) | MIPS-Lite 8-bit Processor | Jesus (jalperdev) | 8-bit MIPS-inspired single-cycle processor with 8 registers, ALU, branches and jumps | jalperdev/tt-chip-design-nucleo | 2682 |  |
| 70 | `tt_um_xoroshiro64plus_v2` (1x1) | xoroshiro64 | Vivek Chiranjit | xoroshiro TRNG | ChiranjitPatel/ttgf_xoroshiro64 | 3049 | **2 ring oscillators** (135/195 inv_1; verified in netlist, contradicts docs) |
| 71 | `tt_um_wokwi_465736612213902337` (1x1) | Juan`s first Worki design | Juan Andres | Proyecto bombi de la elite, drip drip | JuanAndres6386/tt-juans-first-worki | 1257 | Wokwi |
| 96 | `tt_um_waferspace_vga_screensaver` (1x2) | Wafer.space Logo VGA Screensaver | Uri Shaked | Wafer.space Logo bouncing around the screen (640x480, TinyVGA Pmod) | TinyTapeout/tt-waferspace-vga-screensaver | 6529 |  |
| 98 | `tt_um_happyhop_deadcast2` (1x1) | happyhop | deadcast2 | A bouncing smiley face rendered live to VGA via the standard TT VGA PMOD. No framebuffer; pixels computed on the fly. | deadcast2/tt_um_happyhop | 2353 |  |
| 100 | `tt_um_dino7` (1x1) | Dino-7: 7-Segment Runner Game | Dr Sopes | A minimalist single-button endless runner game inspired by the Chrome Dinosaur game, rendered on a single 7-segment display. Features an LFSR of 32... | DrSopes/Dino-7-GF | 3069 | contains art macro `tt_um_dino7_logo` |
| 102 | `tt_um_uacj` (1x1) | Custom DVD Screensaver for VGA | Jazmin Nayeli / Kensy Buatista | Bouncing DVD logo on VGA with color change on wall hits, speed control, invert, and flip options | nayelikensy930-lang/tt_um_uacj_ | 2980 |  |
| 103 | `tt_um_kluterirv_rv32e_core` (4x2) | Minimal RV32E SoC with UART Loader | Kris / KLuterIRV | Minimal RV32E microcontroller with UART program loader, internal instruction memory, GPIO and configurable 7-segment output | KLuterIRV/INNOVA-IRV-ULP-RISCV | 14290 | 2x `gf180mcu_fd_ip_sram__sram128x8m8wm1` macros |
| 128 | `tt_um_wokwi_465731521356457985` (1x1) | Tiny Tapeout Template Copy | Pablo Ruiz | 7-Segment | pabloruizlopez2001-cloud/tt-template-copy | 1273 | Wokwi |
| 129 | `tt_um_machinelearning` (1x2) | 7-Segment Neural Predictor | Abdul Hannan A. | A small neural network that predicts digits 0-9 from 7-segment display patterns. | Nontinium/ttgf-machine-learning | 7439 |  |
| 130 | `tt_um_wokwi_465731520738845697` (1x1) | El primer diseño | Maria Saldaña | Mi primer diseño con Wokwi | 02mariasv/tt-el-primer-diseo | 1272 | Wokwi |
| 132 | `tt_um_wokwi_465731458628527105` (1x1) | Mi copia del Tiny Tapeout | Antonio | Test del Taller Tiny Tapeout | VallejoPretelA/tt-mi-copia-del | 1272 | Wokwi |
| 134 | `tt_um_wokwi_465736691688630273` (1x1) | test1 | Alberto | First contact with the application | aperezfer/tt-test1 | 1270 | Wokwi |
| 135 | `tt_um_divadnauj_GB_serv_soc_wb` (3x2) | serv_soc_wb | Juan David Guerrero Balaguera | Custom SOC using the SERV processor under RV32e | divadnauj-GB/tt_um_divadnauj-GB_serv_soc_wb | 19336 |  |
| 192 | `tt_um_gen1_digital_companion_tile` (1x1) | Gen1 Digital Companion Tile | Juan Fernandez | Symbolic pulse-update and write-verify companion tile for a future local memristive AI chip | JuanCarlosFdezMlg/tt-juan-carloss-first | 1556 |  |
| 194 | `tt_um_wokwi_465732827753495553` (1x1) | Tiny Tapeout Template Ayman | Ayman Harraz | Tinytapeout | aymanhq96/tt-template-ayman | 1289 | Wokwi |
| 195 | `tt_um_pixel_processor` (2x2) | Tiny Pixel Processor | Julian Schlager, Thomas Lindinger, Patrick Pollak, Sebastian Gmeiner, Simon Vogelhuber | A custom processor built for generating procedural graphics | vogelhubersimon/Tiny-Pixel-Processor | 12245 |  |
| 196 | `tt_um_wokwi_465731394728267777` (1x1) | Julian_Proyecto | Julián | It shows my first letter of my name | jpachecorub/tt-julianproyecto | 1280 | Wokwi |
| 198 | `tt_um_wokwi_465731458535202817` (1x1) | Tiny Tapeout Template Copy | Alicia | Test | AliciaRRs/tt-template-copy | 1280 | Wokwi |
| 199 | `tt_um_bioimpedance` (2x2) | Very Low Resource Digital Implementation of Bioimpedance Analysis | Fabien | Digital bioimpedance demodulator with 8-stage I/Q cascade and UART output | fabien-soulier/tt-gf26A-bioimpedance | 9818 |  |
| 295 | `tt_um_utoss_riscv` (4x4) | UTOSS RISC-V core | University of Toronto Open Source Students | RV32I core implementation | UTOSS/risc-v-ttgf | 45634 |  |
| 352 | `tt_um_gojimmypi_ttgf_UART_FSM_TRNG_Lab` (1x2) | Hardware Entropy Explorer: UART/SPI TRNG and PUF | gojimmypi | UART/SPI-controlled ASIC lab for exploring true-random number generation and PUF-style hardware entropy sources. | gojimmypi/ttgf-UART-FSM-TRNG-Lab | 6341 | **8 ring oscillators** (verified in netlist) |
| 353 | `tt_um_algofoogle_dottee` (1x1) | DOTTEE VGA demo (TTGF26a) | algofoogle (Anton Maurovic) | DOTTEE: Pretty little 1-tile Tiny Tapeout ASIC demo (TTGF26a version) | algofoogle/dottee-demo | 3264 |  |
| 354 | `tt_um_8bit_risc_cpu` (1x2) | 8-bit RISC CPU | Jan Kozina | 8-bit RISC CPU with ALU, registers, data memory and external 16-bit instructions | hofi505/risc-v-tt26a | 5228 |  |
| 355 | `tt_um_urish_simon` (1x1) | Simon Says memory game | Uri Shaked | Repeat the sequence of colors and sounds to win the game | urish/tt-simon-game | 2659 | **13-stage RO** clock source, output on uo[7] |
| 356 | `tt_um_top` (1x2) | RHD2164-MCU-SPI Bridge | Manuel Monge | Various SPIs | manuel-monge/tt2606 | 5227 |  |
| 357 | `tt_um_wokwi_465483277165299713` (1x1) | First Tinytapeout | Raúl | First deployment with TinyTapeOut | raullopez54/tt-first-tinytapeout | 1259 | Wokwi |
| 358 | `tt_um_santhosh_stoch_stdp_pair_gf` (1x2) | Stochastic neuron + STDP controller (merged, GF180) | Prof. Santhosh Sivasubramani, IIT Delhi | GF180mcuD merged-pair cell: an 8-bit saturating LIF/stochastic neuron with an 8-entry sigmoid LUT, 8-bit Galois LFSR, programmable refractory, per-... | SanthoshSivasubramani/tt_um_santhosh_stoch_stdp_pair_gf_pub | 6105 |  |
| 359 | `tt_um_wokwi_467219410242853889` (1x1) | Tiny Tapeout testtest 111233 | Suresh Devanathan | Test project for segment display | idatarm/tt-testtest-111233 | 1281 | Wokwi |
| 384 | `tt_um_joannec34_teenytpu` (1x2) | teenytpu | joannec34 | 2x2 INT8 systolic-array TPU with SPI memory interface | joannec34/teenytpu | 5734 |  |
| 385 | `tt_um_wokwi_465736492859711489` (1x1) | Tiny Tapeout Workshop JuanF | Juan | TinyTapeOutWorkshop | jfm92/tt-workshop-juanf | 1259 | Wokwi |
| 386 | `tt_um_main` (1x2) | Pong in Verilog | Jorobraun, TnTim1, ColdC5 | A simple Pong game with VGA-style output | ColdC5/TinyTapeoutGFPong | 4443 |  |
| 387 | `tt_um_wokwi_465732744934845441` (1x1) | Tiny Tapeout Template_1234 | Najlae | hello world project | neshla/tt-template1234 | 1285 | Wokwi |
| 388 | `tt_um_bgao43` (1x2) | Tiny TPU Systolic Array | Yu Xia，Bohong Gao, Junjie Yan, Yufeng Wang, Jinyao Sun, Arthur Stanson | A small systolic-array-based matrix multiplication accelerator | bgao43-wq/tt-tiny-tpu-gf180 | 4880 |  |
| 389 | `tt_um_wokwi_465731371445677057` (1x1) | Arturo's first Wokwi design | Artcraft | My first ever Wokwi design | Artcraftx107/tt-arturos-first-wokwi | 1297 | Wokwi |
| 390 | `tt_um_jpigdon_gps_accelerator_top` (1x2) | GPS_Accelerator | jpigdon | GNSS Accelerator to demonstrate acquisition and tracking on Tiny Tapeout | jpigdon/ttgf_gnss_accelerator | 6275 |  |
| 391 | `tt_um_wokwi_465549494272929793` (1x1) | Pacos first design | Paco | Just AND gate | flozgom/tt-pacos-first-design | 1259 | Wokwi |
| 448 | `tt_um_apa102_ws2812_squidgeefish` (1x2) | APA102 to WS2812 Translator | Squidgeefish | Convert a 7-LED APA102 stream to a WS2812-compatible one | squidgeefish/TT09 | 5692 |  |
| 449 | `tt_um_wokwi_465731430225727489` (1x1) | Rafa’s first Wokwi design | Rafael Morales | tipitaka chip | RafaMG10/tt-rafas-first-wokwi | 1277 | Wokwi |
| 450 | `tt_um_arty3_mac_engine` (1x2) | Simple MAC Engine w/ Postproc | Luca Goddijn | Quantized INT8 MAC engine with bias, activation, and quantizer postproc, SPI-controlled | Arty3/ttgf-mac-engine | 6531 |  |
| 451 | `tt_um_wokwi_465731458365332481` (1x1) | 7 segment Display Fli-Flop Try-out | Carlos David | An amazing flip-flop example with a seven segment display | CarlosDavidTorresRico/tt-7-segment-display | 1270 | Wokwi |
| 452 | `tt_um_mattvenn_signal_generator` (1x2) | Simple Signal Generator | Matt Venn | Square wave generator with a phase-shifting second channel for metastability experiments | mattvenn/simple-signal-generator | 5124 | two-phase edge generator for external SR-latch metastability tests |
| 453 | `tt_um_wokwi_465732744245929985` (1x1) | DiseñoCursoTiny | José Ramñirez Díaz | biestables | joserdElectronics/tt-diseocursotiny | 1263 | Wokwi |
| 454 | `tt_um_tpu` (1x2) | Tensor Processing Unit For GF | Mocus Zhang | multiplies fp8 matrices | mocusez/ttgf-tpu | 6642 |  |
| 455 | `tt_um_wokwi_465731490568160257` (1x1) | Matt’s first Wokwi design | Pedro Da Silva | It shows 1 to 4 | pedro-adasilva/tt-matts-first-wokwi | 1286 | Wokwi |
| 480 | `tt_um_fhw_appel_spiPWMio` (1x1) | spiPWMio | Sönke Appel | A PWM input and PWM generator are configurable via input pins, readable via output pins, and accessible via SPI for read and write operations. | FHW-Appel/TTgf26a-spiPWMio | 2583 |  |
| 481 | `tt_um_wokwi_465732847401723905` (1x1) | Basic Circuit | Izan Amador | It's a basic circuit with 2 NOTs and 1 OR | izanamador/tt-basic-circuit | 1280 | Wokwi |
| 482 | `tt_um_8bitcustomcomputer` (1x1) | SAP 8 Bit Computer | Navneet Prasad, Mohammed Riyaj J, Akash P, Vikash R | The processor implements a 16-instruction, 8-bit ISA inspired by SAP-style architectures, with support for memory access, immediate operations, ari... | navneetprasad1311/ttgf180-8bitcomputer | 2534 |  |
| 483 | `tt_um_wokwi_465731452481768449` (1x1) | El primer diseño de Matt para Wokwi | Marcos | Mi primer proyecto | marcosgafer/tt-el-primer-diseo | 1274 | Wokwi |
| 484 | `tt_um_mgj_bist8` (1x1) | BIST-8: Built-In Self-Test for 8-bit CLA Adder | Mario Garcia Jimenez | BIST architecture for an 8-bit Carry-Lookahead Adder. Includes 12-bit LFSR pattern generator, 16-bit MISR response compactor, fault injection and 4... | mgarciajimenezAirzone/tt-mmggjj | 1755 |  |
| 485 | `tt_um_wokwi_465731502018614273` (1x1) | Tiny Tapeout Template flip flop | Nerea | Circuito basico con puertas logicas | nsuarezparrilla3/tt-template-flip-flop | 1275 | Wokwi |
| 486 | `tt_um_roberto_tiny_radar_tile` (1x1) | BioPulse Tile | Roberto Medina | A tiny vital-sign radar event detector: tracks an 8-bit signal baseline, detects breathing cycles, and flags normal/fast/slow/irregular breathing a... | RobMBSos/tt_um_roberto_tiny_radar_tile | 2934 |  |
| 487 | `tt_um_wokwi_465732616714924033` (1x1) | Tiny Tapeout RJAP | Rodrigo Álvarez | Wokwi Tiny Tapeout Beginner Project | rodalvar23/tt-rjap | 1305 | Wokwi |
| 512 | `tt_um_wokwi_465731455677830145` (1x1) | Tiny Tapeout JMCG | Jose Manuel Cano Garcia | LSFR | jmcanogarcia/tt-jmcg | 1301 | Wokwi |
| 513 | `tt_um_rgb_mixer` (1x1) | rgb_mixer | divadnaujGB | This is my own version of the Z2A course of the rgb_mmixer | divadnauj-GB/tt_um_divadnaujGB_rgb_muxer_pb | 2815 |  |
| 514 | `tt_um_wokwi_465731858252480513` (1x1) | Paula's first Wokwi design | Paula García Jimémez | Demo | paulagarcianm-cmd/tt-paulas-first-wokwi | 1278 | Wokwi |
| 515 | `tt_um_microlane_demo` (1x1) | microlane demo project | htfab | Scrolls a message on the 7-segment display. Hardened using microlane. | htfab/ttgf-microlane-demo | 369 | custom_gds; hardened with htfab/microlane (Python flow); uses latq/icgtp cells |
| 516 | `tt_um_wokwi_465732880722332673` (1x1) | Pedro Template | Pedro Barbero | Plantilla curso tinytipeout | PitBarber/tt-pedro-template | 1259 | Wokwi |
| 517 | `tt_um_danielpenas42` (1x1) | Ball Display | Daniel Penas | shows in vga display and bounces and you can send commands to move it through spi | danielpenas42/ttgf-verilog-danielpenas42 | 2883 |  |
| 518 | `tt_um_wokwi_465731575275296769` (1x1) | ocxpkeWokwiDesign | Jose Ramírez | The first (of many) chip designs | ocxpke/tt-ocxpkewokwidesign | 1556 | Wokwi |
| 519 | `tt_um_memory_game_top` (1x1) | Number Memory Game | Daniel Gabai & Shehroze Kiani | Number based memory game | DanielGabai/ttgf26a-memory-game | 2511 |  |
| 545 | `tt_um_joseph_bf` (1x1) | BF | Joseph Wan and Joseph Mensah | Runs programs in the BF language | Josephwann/jj-tinytapeout | 2979 |  |
| 547 | `tt_um_santhosh_xbar_ctrl_gf` (1x1) | Memristive Crossbar Peripheral Controller (GF180) | Prof. Santhosh Sivasubramani, IIT Delhi | GF180mcuD port of the 8x8 memristive crossbar controller: READ/SET/RESET/FORMING/SWEEP modes, pulse trains, 16-bit pulse counter, compliance auto-a... | SanthoshSivasubramani/tt_um_santhosh_xbar_ctrl_gf_pub | 2948 | digital controller for external crossbar + DAC/ADC |
| 549 | `tt_um_santhosh_ring_osc_gf` (1x1) | Ring Oscillator PVT Sensor & TRNG (GF180) | Prof. Santhosh Sivasubramani, IIT Delhi | GF180mcuD port of 5 SPI-configurable ring oscillators (7/11/15/21/31 gf180 stages) with 16-bit frequency counter, auto gate timer, configurable pre... | SanthoshSivasubramani/tt_um_santhosh_ring_osc_gf_pub | 2972 | **5 ring oscillators** (verified in netlist) |
| 551 | `tt_um_ohuettenhofer_tiny_qsim` (1x1) | Tiny Quantum Circuit Simulator | Oliver Hüttenhofer | Single-qubit quantum circuit simulator | ohuettenhofer/tiny-qsim-ttgf26a | 3390 |  |
| 576 | `tt_um_wokwi_465737601403996161` (1x1) | Tiny Number Simon | Ernesto M | Simon-style digital memory game with eight number inputs and a 7-segment display | ernestomgz/ernest-tiny-tapeout | 2453 | Wokwi |
| 577 | `tt_um_uacj_bouncing_DVD_screensaver` (1x1) | Custom DVD Screensaver for VGA | Alan Sigala | 128x40 bouncing DVD logo with CRT scanlines, checkerboard background, color cycling on wall hits, and random VHS-style corruption effects | AlanPandaSK/tt_um_uacj_bouncing_DVD_screensaver | 3379 |  |
| 578 | `tt_um_ttmul` (1x1) | Balanced Ternary Multiplier | Serge Rabyking | Serial balanced-ternary multiplier: two 8-bit signed in, 16-bit signed out | lanserge/tt-ternary-multiplier-tiny | 3232 |  |
| 579 | `tt_um_logoUACJ_MOGA` (1x1) | VGA_screensaver_UACJ | Angelica Morales Gallegos | Screensaver VGA adaptado a TinyTapeout con logo UACJ y A.M.G | angelicakoehn/tt_um_logoUACJ_MOGA | 2818 |  |
| 580 | `tt_um_wokwi_465731466664816641` (1x1) | Tiny Tapeout Workshop Malaga 2jun2026 | Martin Gonzalez Garcia | 4-bit lfsr with reset | mgonzalezg/tt-workshop-malaga-2jun2026 | 1278 | Wokwi |
| 581 | `tt_um_grace_spi_led_driver` (1x1) | SPI-Controlled 8-Channel LED Driver | Grace Eysenbach | SPI peripheral with addressable 8-bit registers for controlling 8x LEDs | gey16/tt_um_grace_spi_led_driver | 2758 |  |
| 582 | `tt_um_wokwi_451184391728659457` (1x1) | Simple Sprinkler | Noah Perez | Simple sprinkler that functions based on 4 conditions. | noahzperez29/Noah_Simple_Sprinkler | 1283 | Wokwi |
| 583 | `tt_um_rebeccargb_universal_decoder` (1x1) | Universal Binary to Segment Decoder | Rebecca G. Bettencourt | Decodes various binary codes to various segmented displays. | RebeccaRGB/ttgf-ubcd | 1902 |  |
| 608 | `tt_um_wokwi_465731439156454401` (1x1) | Rhyloo’s first Wokwi design | Jorge Benavides Macías | Just a simple logic | rhyloo/tiny-tapeout-test | 1259 | Wokwi |
| 609 | `tt_um_algofoogle_ttgf26a_vco` (1x1) | VCO driven by DAC | algofoogle (Anton Maurovic) | Mixed-signal project with DAC setting a VCO's control voltage | algofoogle/ttgf26a-vco | - | **ANALOG, custom GDS**: R-2R DAC + current-starved RO, 9T cells |
| 610 | `tt_um_wokwi_465732536551273473` (1x1) | Tiny Tapeout Marcos Fernandez | Marcos | Test | marcosfdez99/tt-marcos-fernandez | 1286 | Wokwi |
| 611 | `tt_um_fer_logo_music_vga` (1x1) | UNIZG-FER VGA project | Daniel Hofman | FER logo and music | hofi505/fer-vga-tt26a | 3241 |  |
| 612 | `tt_um_wokwi_465737290543084545` (1x1) | Tiny Tapeout Template | Sankori | My first project | sankori-ai/tt-template | 1273 | Wokwi |
| 613 | `tt_um_maqsudbek_dyadic_pwm` (1x1) | Dyadic PWM | Maksudjon Usmonov | Digital PWM generator with selectable width, dyadic and dithering modulation | maqsudbek/ttgf-dyadic-pwm-iot | 2252 |  |
| 614 | `tt_um_wokwi_465630130495825921` (1x1) | ram 1 bit Copy | siningua_alagartos | ram de 1 bit con dos posiciones | siningua/tt-ram-1-bit | 1299 | Wokwi |
| 615 | `tt_um_htfab_vga_tester` (1x1) | Video mode tester | htfab | Experiment with different VGA timing parameters | htfab/ttgf-vga-tester | 2890 |  |

Seven macros also appear on T26B (same source commit unless noted):
`tt_um_chip_rom`, `tt_um_factory_test`, `tt_um_fhw_appel_spiPWMio`,
`tt_um_rebeccargb_hardware_utf8`, `tt_um_rebeccargb_universal_decoder`,
`tt_um_waferspace_vga_screensaver`, and `tt_um_urish_simon` (26a at commit
1ad919a, 26b at 3a0a46f).

### Verification results present

- wafer.space precheck log (release asset, run 2026-07-04): KLayout DRC
  "SUCCESS (0 violations)", KLayout antenna clear, density clear; **Magic DRC
  reported 4316 errors as a non-gating warning.** The report inside `runs.tar`
  (`12-magic-drc/reports/drc.magic.rpt`) is dominated by `DF.8` (N-diffusion to
  N-well spacing), `DV.9` ("Both LV and MV devices cannot be in the same
  N-well"), `DV.6 + DV.3` (5/6 V diffusion to 3.3 V tap) and sub-cell
  abut/overlap messages. Which macros these fall in was not attributed.
- `gl_test_vcd.zip`: gate-level mux cocotb test results.
- No silicon bring-up data in the repo or release.

## Authors and affiliations

| Person / organisation | Role | Affiliation | Source |
|---|---|---|---|
| Tiny Tapeout (org `TinyTapeout`) | Shuttle organiser, repo owner | Tiny Tapeout | `gh api orgs/TinyTapeout`, README |
| Uri Shaked (`urish`) | 289 commits; release author; chip ROM, Simon, wafer.space screensaver | "working on Wokwi and Tiny Tapeout" | git shortlog, GitHub bio |
| TinyTapeoutBot | 307 automated project-import commits | - | git shortlog |
| Sylvain Munaut (`smunaut`) | Multiplexer, GF180 port, pad wrapper, power gates, factory test | not stated | copyright headers in `tt-multiplexer`, submodule log |
| htfab | Precheck (GF antenna check), microlane demo, VGA tester | not stated | `tt` submodule log, `info.yaml` |
| Kristaps Jurkans | tooling commits | not stated | git shortlog |
| Anton Maurovic (`algofoogle`) | VCO+DAC analog tile, DOTTEE demo | not stated (Adelaide, Australia per GitHub profile) | `info.yaml`, `gh api users/algofoogle` |
| Prof. Santhosh Sivasubramani | 4 tiles (ring oscillator PVT sensor, RRAM characterisation controller, crossbar controller, neuron/STDP) | IIT Delhi | `info.yaml` author field |
| gojimmypi | TRNG/PUF entropy lab | "Contractor", California (GitHub profile) | `gh api users/gojimmypi` |
| Vivek Chiranjit (`ChiranjitPatel`) | xoroshiro64 + ring oscillators | not stated | `info.yaml` |
| Kris / Kristian Thomas Luter Arregui (`KLuterIRV`) | RV32E SoC with SRAM macros | not stated (repo name `INNOVA-IRV-ULP-RISCV`) | `info.yaml`, GitHub profile |
| Matt Venn | Signal generator | YosysHQ / Tiny Tapeout (GitHub profile) | `gh api users/mattvenn` |
| University of Toronto Open Source Students (UTOSS) | RV32I core (4x4) | University of Toronto | `info.yaml` author field |
| Escuela Colombiana de Ingenieria Julio Garavito | Line follower | as named | `info.yaml` author field |
| ~36 Wokwi first-design authors | Workshop tiles (Spanish-language; one titled "Tiny Tapeout Workshop Malaga 2jun2026") | not stated | `info.yaml` |
| Tillitis, Wit | Funded GF180 support in Tiny Tapeout | - | `docs/funding.typ` |

All other authors are as listed in the project table; no affiliation is stated
for them beyond what appears in the author column.

## Value for GF180MCU characterisation and PDK development

### Verdict: High

One custom analog tile (R-2R poly-resistor DAC driving a current-starved ring
oscillator, using `ppolyf_u_1k`, `nfet_03v3` and 9-track cells) and four
digital tiles with real, netlist-verified standard-cell ring oscillators and
on-chip counters, all reachable through the shuttle's digital pads. Everything
else is ordinary synthesised 7T logic, useful as about 90 functional/yield data
points at 3.3 V on the 5 V library.

### Test structures and measurable circuits

All structures are in the 3.3 V core domain (`vdpwr`, behind a per-tile power
switch). Access is by selecting the tile's mux address and using the shared
`ui/uo/uio` pads; there are no probe pads and no analog pad connections.

| Structure | What it exercises | Access | Where |
|---|---|---|---|
| `tt_um_algofoogle_ttgf26a_vco` (addr 609): 9-bit R-2R DAC (`r2r_dac`, cells `ppolyf_u_1k_*`) feeding a 5-stage current-starved ring oscillator (`csringosc`, 5x `csrostage`, `nfet_03v3_*`), then a 5-bit divider hardened with `gf180mcu_fd_sc_mcu9t5v0`; the GDS also carries an art cell `lily_dino` | `ppolyf_u_1k` matching/linearity (indirectly, via frequency), nfet_03v3/pfet_03v3 current vs gate voltage, VCO tuning curve, 9T-library flip-flop max toggle rate | DAC code on `ui[7:0]`+`uio[0]`; raw VCO on `uio[2]`, /2../32 on `uio[3..7]`. No external clock needed | `projects/tt_um_algofoogle_ttgf26a_vco/` (OAS, LEF, stub `.v`, `docs/info.md`); cell names read from `macros.zip` GDS. Schematics/magic/SPICE are in algofoogle/ttgf26a-vco @ 3d790fd (not in this repo) |
| `tt_um_santhosh_ring_osc_gf` (addr 549): five gated ROs, netlist shows loops of 7, 11, 15, 21, 31 stages (`nand2_1` + `inv_1`; the 31-stage loop has had three inverters resized by the flow to `inv_2`/`clkinv_1`/`clkinv_2`) | `gf180mcu_fd_sc_mcu7t5v0__inv_1`/`nand2_1` stage delay at 3.3 V vs length; jitter; local mismatch via beat mode | 16-bit gated counter read on `uo[7:0]` or SPI (`uio[0..3]`); raw RO on `uio[5]`, prescaled/synchronised on `uio[6]` | `projects/tt_um_santhosh_ring_osc_gf/` (`.v` netlist instances `ro7_*`..`ro31_*`, `docs/info.md` register map) |
| `tt_um_gojimmypi_ttgf_UART_FSM_TRNG_Lab` (addr 352): eight ROs, loops of 7, 9, 11, 13, 15, 17, 19, 21 `inv_2` + one `and2_1` enable each | `inv_2` stage delay, jitter/entropy | UART/SPI register interface, sampled bits via registers (a raw RO frequency pin was not identified in the docs) | `projects/tt_um_gojimmypi_ttgf_UART_FSM_TRNG_Lab/` (instances `u_trng.u_ro0..7`) |
| `tt_um_xoroshiro64plus_v2` (addr 70): two long ROs, 135 and 195 `inv_1` + `and2_1` (`ro_fast`, `ro_slow`) | long-chain `inv_1` delay (averages mismatch) | Only as noise XORed into a PRNG; no direct frequency output documented | `projects/tt_um_xoroshiro64plus_v2/` |
| `tt_um_urish_simon` (addr 355, also on T26B): 13-stage RO (`clkinv_1` x13 + `and2_1`), divided by 2048 | `clkinv_1` stage delay | `clk_sel=1`, divided clock on `uo[7]` (about 50 kHz expected) | `projects/tt_um_urish_simon/` (`ring_osc.inv[*]`) |
| `tt_um_kluterirv_rv32e_core` (addr 103): two `gf180mcu_fd_ip_sram__sram128x8m8wm1` macros | Stock PDK SRAM macro function at 3.3 V core supply | Only through the RV32E SoC (UART loader); no direct SRAM pins | `projects/tt_um_kluterirv_rv32e_core/` |
| `tt_um_factory_test` (addr 1) | IO pad function, `bi_24t` output drive, input thresholds, mux path delay | `ui`->`uo` mirror, `uio`->`uo` mirror, 8-bit counter on `uo`/`uio` | `verilog/rtl/tt_um_factory_test.v` |
| Per-tile power switches `tt_pg_3v3_hp_{1,2,4}` | Header switch on-resistance / leakage (only observable as tile supply behaviour) | Not separately instrumented | `tt-multiplexer/ol2/tt_top/gds/` |

Simulation references that silicon could be compared against:

- VCO: `docs/info.md` gives estimates only (3 MHz to 400 MHz range, about
  61 MHz at DAC code 154 = 0.993 V, stall below code about 85, counter unstable
  above about 388). No SPICE decks or plots in this repo.
- Simon RO: `docs/info.md` states "~101 MHz in GF180 SPICE at 3.3 V" for the
  13-stage ring.
- Santhosh RO: no frequency predictions; the docs say gate-level simulation was
  skipped.
- Every LibreLane-hardened tile has `stats/metrics.csv` with post-route STA
  slack, skew and power at three 3.3 V-range corners.

`tt_um_santhosh_rsd_char_gf` and `tt_um_santhosh_xbar_ctrl_gf` have
"characterisation" in their descriptions but are purely digital sequencers for
an external RRAM/crossbar with external DAC and ADC; they contain nothing that
measures GF180 devices.

### Candidate PDK additions

- `gf180mcu_ocd_io` pad library used in production as a full pad ring; the PDK
  snapshot needed a LibreLane "hack" commit to accept it (`gf180mcu` submodule
  cae6f09, d4d5fab).
- GF180 header power switch macros `tt_pg_3v3_hp_{1,2,4}` (GDS/LEF/blackbox
  only; imported directly, commit "[hack] Import power gate directly").
- LVS netlist fix-up script `tt-multiplexer/py/gf_fixup_netlist.py` and the
  `MAGIC_EXT_SHORT_RESISTOR` workaround in `ol2/tt_top/build.py`; antenna
  work-arounds (`ol2/tt_mux/odb_diodes.py`, commits "[HACK] ol2/tt_mux: Fix
  antenna", "IO routing to fix antenna").
- Magic DRC deck versus KLayout deck disagreement: 4316 Magic errors on a
  layout the KLayout deck passes with 0 (rule classes listed above). Worth
  triaging as a deck issue.
- Two custom analog cells from the VCO tile (`csrostage`, `r2r_dac`) as
  examples; sources are upstream in algofoogle/ttgf26a-vco.
- `htfab/microlane` Python hardening flow demonstrated on GF180
  (`tt_um_microlane_demo`).
- Precheck antenna check for gf180mcuD in `tt/` (commits c904c49, d4626aa).

### What would be needed to use it

- Packaged test on a Tiny Tapeout demo board (or any board giving the 3 mux
  control pins, clk, rst_n and the 24 user IOs); no bare-die probing required
  and none possible beyond the pad ring.
- Frequency counter or oscilloscope for the VCO (`uio[2]` can be far above
  what a 24 mA pad passes cleanly; use the divided outputs) and the RO tiles;
  SPI/UART host for the Santhosh and gojimmypi tiles.
- Core supply sweep and temperature control for PVT work; the documented
  corners are 3.0 to 3.6 V.
- Missing: SPICE predictions for RO frequencies (except the two figures above),
  a bench test plan, pad-to-package pin map (lives in Tiny Tapeout docs, not
  here), and the user design sources (each in its own repo, pinned by
  `commit_id.json`).

## Notes and caveats

- The repo holds 152 remote branches. All except `main` are bot staging
  branches `projects/<macro>-<actions run id>`, each one commit ahead of an
  older main, carrying an earlier submission of a single project. 13 macro
  names appear only on branches and are **not** on the taped-out die:
  `tt_um_asic_cpu`, `tt_um_xoroshiro64plus` (superseded by `_v2`), and 11
  `tt_um_wokwi_*` designs. No branch holds different infrastructure.
- `tt_um_xoroshiro64plus_v2`: `docs/info.md` says the ring-oscillator noise is
  an external input, but the netlist contains two internal ring oscillators.
- `tt_um_santhosh_ring_osc_gf`: three of the 31-stage ring's inverters are
  not `inv_1` in the final netlist despite the `keep/dont_touch` claim.
- `tt_um_prem_pipeline_test` (4x4) still has the template description
  "Zero to ASIC demo project".
- Many netlists contain combinational feedback loops that are not oscillators
  (mux/latch structures in Wokwi designs, large false loops in
  `tt_um_utoss_riscv`, `tt_um_maqsudbek_dyadic_pwm`,
  `tt_um_jpigdon_gps_accelerator_top`); only the loops listed in the table
  above are inverter rings.
- Power-gate device type and the attribution of Magic DRC errors are inferred
  from GDS layers and report text, not from schematics.
- `project.json` on the platform has an empty description; `docs/funding.typ`
  refers to "Tiny Tapeout GF 0p2" rather than this shuttle.
- User-project analysis is from the hardened netlists, GDS cell names and
  each project's `docs/info.md`; the 93 upstream source repos were not cloned.

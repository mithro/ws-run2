# wafer.space GF180MCU Run 2 — Standard Cell & SRAM Density Report

**GF180MCU Process (GlobalFoundries 180nm), Shuttle G802**

## Introduction

This report analyzes the standard cell and SRAM density achieved by the 40 unique public chip designs on the [wafer.space](https://wafer.space/) GF180MCU Run 2 reticle. The reticle has 54 slots; the public layout contains 43 slot placements (some designs appear more than once, and private designs are not included).

All designs were fabricated on GlobalFoundries' GF180MCU process, a 180-nanometer (0.18um) technology node. This is a mature, relatively large-geometry process — for comparison, modern smartphone chips use 3nm or 5nm processes with features roughly 50x smaller.

> **Note on counting methodology:** All standard cell counts in this report count only **logic cells** — cells that perform actual computation (gates, flip-flops, buffers, multiplexers, etc.). Infrastructure cells are excluded: filler cells (fill, fillcap, endcap, filltie), well taps, antenna fix diodes, ESD diodes, and tie-high/tie-low cells. These infrastructure cells are inserted by automated tools to satisfy manufacturing rules but perform no logic function. On this reticle there are 6.8M infrastructure cell instances and 2.4M logic cell instances across the unique designs — 2.8 infrastructure cells for every logic cell.

## What Are Standard Cells?

A "standard cell" is a pre-designed, pre-verified building block used to construct digital circuits. Think of them like LEGO bricks for chip design: each cell performs one simple logic function (an AND gate, a flip-flop for storing one bit, a buffer for boosting signal strength), and a chip designer assembles thousands or millions of them to build complex circuits.

Standard cells in a library all share the same height (so they line up in rows) but vary in width depending on their function. Automated tools place these cells in rows and then route wires between them.

The "density" of standard cells — how many fit per square millimeter — is a key measure of how efficiently a design uses its silicon area. Higher density generally means more logic functionality packed into less chip area, which reduces cost.

## Standard Cell Libraries on This Reticle

| Library | Row Height | Rows per mm | Relative Density | Logic instances | Share |
|---|---|---|---|---|---|
| mcu7t3v3 (7-track, 3.3V) | 3.92 um | 255 rows | 100% | 1.3M | 53% |
| mcu7t5v0 (7-track, 5V) | 3.92 um | 255 rows | 100% | 1.1M | 46% |
| mcu9t5v0 (9-track, 5V) | 5.04 um | 198 rows | 78% | 46k | 2% |

Row height is the height of the cells' placement boundary, which is what rows are stacked at. Taller rows hold fewer cells per mm² but leave more room for wiring inside the cell.

Most designs use one library exclusively. The designs that mix libraries are: [T0P3](https://github.com/TinyTapeout/tinytapeout-gf-0p3) (94k mcu7t5v0 + 25k mcu7t3v3); [T26B](https://github.com/TinyTapeout/tinytapeout-gf-26b) (154k mcu7t5v0 + 2k mcu7t3v3).

## Theoretical Maximum Standard Cell Density

If you filled an entire square millimeter with nothing but one type of logic standard cell (no wiring, no gaps, no infrastructure cells), the theoretical maximum density would be:

| Cell Type | 7t-3.3V | 7t-5V | 9t-5V | What it does |
|---|---|---|---|---|
| Inverter | 114k/mm² (inv_2, 2.24um) | 114k/mm² (inv_1, 2.24um) | 89k/mm² (inv_1, 2.24um) | Flips a signal |
| NAND gate | 65k/mm² (nand2_2, 3.92um) | 91k/mm² (nand2_1, 2.80um) | 71k/mm² (nand2_1, 2.80um) | Basic logic gate |
| Buffer | 76k/mm² (buff_2, 3.36um) | 76k/mm² (buf_1, 3.36um) | 59k/mm² (buf_1, 3.36um) | Strengthens a signal |
| Flip-flop | 17k/mm² (dfxtp_2, 15.12um) | 16k/mm² (dffq_1, 16.24um) | 13k/mm² (dffq_1, 15.68um) | Stores one bit |

These are hard upper bounds — the density if you packed cells edge-to-edge with zero routing overhead. For each library the smallest cell of that kind is used; the 3.3V library has no drive strength 1 cells, so its smallest cells are the `_2` variants.

In practice, real designs achieve significantly less because:

- **(a) Routing overhead** — wires connecting cells need room, which limits how tightly cells can be placed
- **(b) Infrastructure cells** — fillers, taps, antenna diodes, and tie cells make up 74% of cell instances on this reticle
- **(c) Mixed cell types** — designs use a mix of small and large cells
- **(d) Power planning** — power/ground straps consume area
- **(e) Clock distribution** — clock tree buffers and wiring take space

## Achieved Standard Cell Density — Design Averages

The following tables show the average logic standard cell density for each design's "core area" — the interior of the chip excluding the I/O pad ring (a 350um border of large pads around the perimeter used for external connections).

"% of max" compares against the buffer theoretical maximum for the design's primary library. "Cell area" is the share of the core area actually covered by logic cells — the placement utilisation of the die as a whole, including any area left empty or given to SRAM.

### High Density (above 10k logic SC/mm² core average)

| Design | Library | Core SC/mm² | % of max | Cell area | Logic SC | SRAM | Project |
|---|---|---|---|---|---|---|---|
| [CLON](https://github.com/ThorbenMoos/Cloneless2) | 7t-5V | 23k | 30% | 52% | 324k | 0 | Cloneless2 |
| BTX1 | 7t-3.3V | 18k | 23% | 42% | 253k | 19 | BTX |
| [SCUP](https://github.com/sifferman/gf180mcu-peripherals) | 7t-3.3V | 17k | 22% | 48% | 239k | 0 | GF180MCU Peripherals |
| [TQVA](https://github.com/MichaelBell/ws01-tinyQV) | 7t-5V | 16k | 21% | 36% | 36k | 1 | TinyQV - Crowdsourced Risc-V SoC |
| [MOLE](https://github.com/mole99/wsrun2-fabulous-fpga) | 7t-3.3V | 15k | 20% | 48% | 212k | 13 | FABulous FPGA |
| [DPK2](https://github.com/dpks2003/cordic-romless) | 7t-5V | 15k | 19% | 31% | 33k | 0 | cordic-romless-x8 |
| [DPK1](https://github.com/dpks2003/bio-core) | 7t-5V | 12k | 16% | 27% | 66k | 8 | bio180 |
| [EURO](https://github.com/anfroholic/eurosynth) | 7t-5V | 12k | 15% | 29% | 68k | 0 | EuroSynth |
| [T26B](https://github.com/TinyTapeout/tinytapeout-gf-26b) | mixed | 11k | 14% | 31% | 156k | custom | Tiny Tapeout GF 26b |
| TQVE | 7t-3.3V | 11k | 14% | 31% | 24k | 10 | TinyQV - RISC-V SoC with experimental pad setup |
| [TQVD](https://github.com/MichaelBell/ws02-tinyQV) | 7t-3.3V | 10k | 14% | 28% | 24k | 5 | TinyQV - RISC-V SoC with HDMI output |
| [T26A](https://github.com/TinyTapeout/tinytapeout-gf-26a) | 7t-5V | 10k | 13% | 30% | 144k | 2 | Tiny Tapeout GF 26a |

### Medium Density (3k–10k logic SC/mm² core average)

| Design | Library | Core SC/mm² | % of max | Cell area | Logic SC | SRAM | Project |
|---|---|---|---|---|---|---|---|
| [CAB1](https://github.com/ZeduloTech/Cabrera) | 7t-5V | 9k | 12% | 24% | 52k | 6 | Cabrera CoB |
| [SCTP](https://github.com/SlugTPU/gf180mcu-slugtpu) | 7t-3.3V | 9k | 11% | 24% | 125k | 17 | SlugTPU |
| [NAX1](https://github.com/ZeduloTech/Naxos) | 7t-3.3V | 8k | 11% | 23% | 50k | 12 | Naxos CoB |
| [T0P3](https://github.com/TinyTapeout/tinytapeout-gf-0p3) | mixed | 8k | 11% | 24% | 119k | 1 | Tiny Tapeout GF 0p3 |
| [SCML](https://github.com/kjconway5/ML-Audio) | 7t-3.3V | 8k | 10% | 23% | 111k | 38 | ML-Audio SC |
| [AS04](https://github.com/AvalonSemiconductors/ws-submission-2026/) | 7t-3.3V | 6k | 8% | 16% | 87k | 0 | AS04 Multi-Project die using 3.3V SCL |
| [TQVC](https://github.com/MichaelBell/ws01-tinyQV) | 7t-5V | 6k | 8% | 14% | 36k | 1 | TinyQV - Crowdsourced Risc-V SoC (1x0.5) |
| [GD04](https://github.com/gregdavill/gf180mcu-racquet-1x0.5) | 9t-5V | 6k | 10% | 24% | 36k | 6 | Racquet Wide 1x0.5 |
| [KIAN](https://github.com/splinedrive/gf180mcu-kianv-rv32ima-sv32-ws02/) | 7t-3.3V | 5k | 7% | 15% | 77k | 21 | KianV: A 32-bit RISC-V Linux SoC taped out on GF180MCU Run 2 |
| [AMM1](https://github.com/algofoogle/gf180ws2-raybox-zero) | 7t-5V | 5k | 7% | 16% | 32k | 0 | raybox-zero wafer.space run 2 half height |
| [CAFE](https://github.com/Essenceia/Expresso_ASIC_Chip) | 7t-5V | 4k | 5% | 12% | 9k | 0 | Expresso Ethernet Chip: 100Mbps Ethernet switch + Heat death of the U… |
| [SCMT](https://github.com/dhgaddy/microTheia) | 7t-3.3V | 3k | 4% | 6% | 48k | 41 | microTheia |
| [PSOC](https://github.com/d-burnett/picosoc-on-waferspace) | 7t-5V | 3k | 4% | 10% | 18k | 8 | Simplest possible PicoSoC implementation using wafer.space flow |

### Low Density (below 3k logic SC/mm² core average)

| Design | Library | Core SC/mm² | % of max | Cell area | Logic SC | SRAM | Project |
|---|---|---|---|---|---|---|---|
| [QZ80](https://github.com/rejunity/ws0-z80-open-silicon-gf180mcu) | 9t-5V | 2k | 4% | 8% | 5k | 0 | FOSSi open-source replacement for Z80 classic 8-bit CPU (0.5 x 0.5 sl… |
| [DCO0](https://github.com/asinghani/ws-dco-tdc) | 7t-5V | 1k | 2% | 5% | 7k | 0 | Standard Cell DCO+TDC |
| [WSLG](https://github.com/89Mods/ws-logo-die) | 7t-5V | 1k | 1% | 4% | 14k | 0 | Wafer.Space Logo |
| [HZ80](https://github.com/rejunity/ws0-z80-open-silicon-gf180mcu) | 9t-5V | 1k | 2% | 3% | 5k | 0 | FOSSi open-source replacement for Z80 classic 8-bit CPU (0.5 x 1 slot) |
| [AS16](http://github.com/SUD0NET/as16) | 7t-5V | 1k | 1% | 3% | 6k | 2 | AS16 CPU |
| [SALU](https://github.com/StackDoubleFlow/alu_silicon) | 7t-5V | 1k | 1% | 2% | 2k | 0 | Simple ALU |
| [FS03](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | 7t-5V | 1k | 1% | 1% | 4k | 0 | Test chip with 5V SRAM blocks |
| [FS01](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | 7t-5V | 1k | 1% | 1% | 4k | 0 | Test chip with 3.3V SRAM blocks using regular design rules |
| [FS02](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | 7t-5V | 1k | 1% | 1% | 3k | custom | Test chip with 3.3V SRAM blocks using SRAM design rules |

### Minimal (analog, custom or test structures)

These designs contain fewer than 1,000 logic standard cells:

| Design | Logic SC | Transistors | SRAM | Pads | Project |
|---|---|---|---|---|---|
| [0000](https://github.com/GTIceLab/ASHES-GF180nm) | 40 | 113k | 0 | 73 | ICELab Test Chip |
| FC01 | 0 | 68k | 0 | 12 | Flip Chip pad test version 1 |
| [ISHI](https://github.com/ishi-kai/ISHI-KAI_Multiple_Projects_WaferSapce-GF180-2) | 0 | 99k | 0 | 145 | ISHI-KAI_Multiple_Projects_WaferSapce-GF180-2 |
| [MEME](https://github.com/anfroholic/meme_chip) | 226 | 181k | 0 | 73 | Artwork Meme Chip |
| [OCD3](https://github.com/RTimothyEdwards/gf180mcu_ocd_sram_test) | 123 | 240k | 4 | 73 | 3.3V SRAM test 2 |
| [RLCM](https://github.com/EngGhaith/RLCM-Test-Passives-For-GF180MCUD) | 0 | 44k | 0 | 247 | RLCM: Test Passives For GF180MCUD |

## Achieved Density — Peak 1mm x 1mm Regions

While the averages above include sparse regions, the peak density in the best single 1mm x 1mm grid cell shows the maximum density achieved anywhere on each design. Grid cells that overlap an SRAM macro are excluded.

| Design | Peak Logic SC/mm² | % of buffer max | Library |
|---|---|---|---|
| [SCUP](https://github.com/sifferman/gf180mcu-peripherals) | 30k | 39% of 76k | 7t-3.3V |
| [CLON](https://github.com/ThorbenMoos/Cloneless2) | 30k | 39% of 76k | 7t-5V |
| BTX1 | 24k | 32% of 76k | 7t-3.3V |
| [MOLE](https://github.com/mole99/wsrun2-fabulous-fpga) | 23k | 31% of 76k | 7t-3.3V |
| [T26B](https://github.com/TinyTapeout/tinytapeout-gf-26b) | 18k | 23% of 76k | mixed |
| [T26A](https://github.com/TinyTapeout/tinytapeout-gf-26a) | 18k | 23% of 76k | 7t-5V |
| [CAB1](https://github.com/ZeduloTech/Cabrera) | 17k | 22% of 76k | 7t-5V |
| [T0P3](https://github.com/TinyTapeout/tinytapeout-gf-0p3) | 17k | 22% of 76k | mixed |
| [EURO](https://github.com/anfroholic/eurosynth) | 15k | 19% of 76k | 7t-5V |
| [DPK1](https://github.com/dpks2003/bio-core) | 14k | 18% of 76k | 7t-5V |
| [KIAN](https://github.com/splinedrive/gf180mcu-kianv-rv32ima-sv32-ws02/) | 14k | 18% of 76k | 7t-3.3V |
| [AS04](https://github.com/AvalonSemiconductors/ws-submission-2026/) | 13k | 17% of 76k | 7t-3.3V |
| [TQVA](https://github.com/MichaelBell/ws01-tinyQV) | 12k | 15% of 76k | 7t-5V |
| [DPK2](https://github.com/dpks2003/cordic-romless) | 12k | 15% of 76k | 7t-5V |
| [TQVC](https://github.com/MichaelBell/ws01-tinyQV) | 11k | 15% of 76k | 7t-5V |

The highest achieved density on this reticle is 39% of the buffer theoretical maximum, observed in the densest 1mm² region of [SCUP](https://github.com/sifferman/gf180mcu-peripherals). The rest of that area is consumed by larger cells, infrastructure cells and the gaps left for routing.

## Library Comparison

Comparing designs that use one library exclusively:

| Metric | mcu7t3v3 (7-track, 3.3V) | mcu7t5v0 (7-track, 5V) | mcu9t5v0 (9-track, 5V) |
|---|---|---|---|
| Designs using this library | 12 | 20 | 3 |
| Best core density | 18k SC/mm² · 23% of max (BTX1) | 23k SC/mm² · 30% of max ([CLON](https://github.com/ThorbenMoos/Cloneless2)) | 6k SC/mm² · 10% of max ([GD04](https://github.com/gregdavill/gf180mcu-racquet-1x0.5)) |
| Best peak grid cell | 30k SC/mm² · 39% of max ([SCUP](https://github.com/sifferman/gf180mcu-peripherals)) | 30k SC/mm² · 39% of max ([CLON](https://github.com/ThorbenMoos/Cloneless2)) | 3k SC/mm² · 5% of max ([HZ80](https://github.com/rejunity/ws0-z80-open-silicon-gf180mcu)) |
| Median core density | 9k SC/mm² · 11% of max | 3k SC/mm² · 5% of max | 2k SC/mm² · 4% of max |

Differences between libraries here reflect which designs chose which library as much as the libraries themselves; the theoretical difference from row height alone is in the table above.

## Most Common Logic Cell Types

The 15 most-used logic cell types across all unique designs on the reticle:

| Cell Type | Library | Instances | What it does |
|---|---|---|---|
| buff_2 | 7t-3.3V | 216k | Buffer (2x drive) |
| nand2_1 | 7t-5V | 162k | 2-input NAND gate |
| mux2_2 | 7t-3.3V | 111k | 2-input multiplexer (2x drive) |
| dlybuff_2 | 7t-3.3V | 99k | Delay buffer (2x drive) |
| dfxtp_2 | 7t-3.3V | 99k | D flip-flop (1 bit storage) (2x drive) |
| oai21_1 | 7t-5V | 71k | OR-AND-Invert compound gate |
| dffq_1 | 7t-5V | 67k | D flip-flop (1 bit storage) |
| nor2_1 | 7t-5V | 66k | 2-input NOR gate |
| xor2_1 | 7t-5V | 65k | 2-input XOR gate |
| dlyb_1 | 7t-5V | 62k | Delay buffer |
| xnor2_2 | 7t-3.3V | 61k | 2-input XNOR gate (2x drive) |
| and2_2 | 7t-3.3V | 61k | 2-input AND gate (2x drive) |
| clkinv_1 | 7t-5V | 59k | Clock inverter |
| aoi21_1 | 7t-5V | 55k | AND-OR-Invert compound gate |
| dlxtp_2 | 7t-3.3V | 54k | Latch (level-sensitive) (2x drive) |

Across the reticle there are 227k 2-input NAND gates and 208k flip-flops — 1.1 NAND2 gates per flip-flop.

## SRAM Block Usage

SRAM (Static Random-Access Memory) blocks are pre-designed memory macros. Unlike standard cells, which are composed by automated tools, SRAM blocks are hand-optimized fixed-size units designed to store data as densely as possible.

21 of the 40 designs include SRAM, holding 152 KiB of memory between them:

| Design | SRAM macros | SRAM bits | SRAM area | Logic SC | Project |
|---|---|---|---|---|---|
| [SCMT](https://github.com/dhgaddy/microTheia) | 41 | 280,576 | 5.58 mm² (39% of core) | 48k | microTheia |
| [SCML](https://github.com/kjconway5/ML-Audio) | 38 | 223,232 | 4.65 mm² (33% of core) | 111k | ML-Audio SC |
| [KIAN](https://github.com/splinedrive/gf180mcu-kianv-rv32ima-sv32-ws02/) | 21 | 86,016 | 2.04 mm² (14% of core) | 77k | KianV: A 32-bit RISC-V Linux SoC taped out on GF180MCU Run 2 |
| BTX1 | 19 | 71,680 | 1.76 mm² (12% of core) | 253k | BTX |
| [SCTP](https://github.com/SlugTPU/gf180mcu-slugtpu) | 17 | 139,264 | 2.64 mm² (19% of core) | 125k | SlugTPU |
| [MOLE](https://github.com/mole99/wsrun2-fabulous-fpga) | 13 | 106,496 | 2.02 mm² (14% of core) | 212k | FABulous FPGA |
| [NAX1](https://github.com/ZeduloTech/Naxos) | 12 | 81,920 | 1.63 mm² (28% of core) | 50k | Naxos CoB |
| TQVE | 10 | 77,824 | 1.50 mm² (66% of core) | 24k | TinyQV - RISC-V SoC with experimental pad setup |
| [DPK1](https://github.com/dpks2003/bio-core) | 8 | 32,768 | 1.68 mm² (31% of core) | 66k | bio180 |
| [PSOC](https://github.com/d-burnett/picosoc-on-waferspace) | 8 | 32,768 | 1.68 mm² (28% of core) | 18k | Simplest possible PicoSoC implementation using wafer.space flow |
| [CAB1](https://github.com/ZeduloTech/Cabrera) | 6 | 20,480 | 1.13 mm² (19% of core) | 52k | Cabrera CoB |
| [GD04](https://github.com/gregdavill/gf180mcu-racquet-1x0.5) | 6 | 24,576 | 1.26 mm² (21% of core) | 36k | Racquet Wide 1x0.5 |
| [TQVD](https://github.com/MichaelBell/ws02-tinyQV) | 5 | 32,768 | 0.66 mm² (29% of core) | 24k | TinyQV - RISC-V SoC with HDMI output |
| [OCD3](https://github.com/RTimothyEdwards/gf180mcu_ocd_sram_test) | 4 | 14,848 | 0.37 mm² (6% of core) | 123 | 3.3V SRAM test 2 |
| [AS16](http://github.com/SUD0NET/as16) | 2 | 8,192 | 0.42 mm² (7% of core) | 6k | AS16 CPU |
| [T26A](https://github.com/TinyTapeout/tinytapeout-gf-26a) | 2 | 2,048 | 0.23 mm² (2% of core) | 144k | Tiny Tapeout GF 26a |
| [T0P3](https://github.com/TinyTapeout/tinytapeout-gf-0p3) | 1 | 2,048 | 0.07 mm² (<1% of core) | 119k | Tiny Tapeout GF 0p3 |
| [TQVA](https://github.com/MichaelBell/ws01-tinyQV) | 1 | 4,096 | 0.21 mm² (9% of core) | 36k | TinyQV - Crowdsourced Risc-V SoC |
| [TQVC](https://github.com/MichaelBell/ws01-tinyQV) | 1 | 4,096 | 0.21 mm² (4% of core) | 36k | TinyQV - Crowdsourced Risc-V SoC (1x0.5) |
| [FS02](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | custom | — | 0.35 mm² (6% of core) | 3k | Test chip with 3.3V SRAM blocks using SRAM design rules |
| [T26B](https://github.com/TinyTapeout/tinytapeout-gf-26b) | custom | — | 0.01 mm² (<1% of core) | 156k | Tiny Tapeout GF 26b |

SRAM macros are identified by cell name, and their area is the macro footprint. "custom" marks a design with SRAM marker shapes (GDS 108/5) but no recognised macro, where the count and size are not known and the area is that of the marked bitcell arrays.

## SRAM vs Standard Cell Transistor Density

"Transistor density" here counts the number of distinct regions where a gate electrode (polysilicon, GDS 30/0) crosses an active area (diffusion, GDS 22/0) — each such crossing forms one transistor.

### Theoretical Maximum Transistor Density for Standard Cells

| Cell (7t-3.3V) | Width | Cells/mm² | Trans/cell | Trans/mm² theoretical max |
|---|---|---|---|---|
| inv_2 | 2.24 um | 114k | 4 | 456k/mm² |
| nand2_2 | 3.92 um | 65k | 8 | 521k/mm² |
| buff_2 | 3.36 um | 76k | 6 | 456k/mm² |
| dfxtp_2 | 15.12 um | 17k | 26 | 439k/mm² |

| Cell (7t-5V) | Width | Cells/mm² | Trans/cell | Trans/mm² theoretical max |
|---|---|---|---|---|
| inv_1 | 2.24 um | 114k | 2 | 228k/mm² |
| nand2_1 | 2.80 um | 91k | 4 | 364k/mm² |
| buf_1 | 3.36 um | 76k | 4 | 304k/mm² |
| dffq_1 | 16.24 um | 16k | 24 | 377k/mm² |

| Cell (9t-5V) | Width | Cells/mm² | Trans/cell | Trans/mm² theoretical max |
|---|---|---|---|---|
| inv_1 | 2.24 um | 89k | 2 | 177k/mm² |
| nand2_1 | 2.80 um | 71k | 4 | 283k/mm² |
| buf_1 | 3.36 um | 59k | 4 | 236k/mm² |
| dffq_1 | 15.68 um | 13k | 24 | 304k/mm² |

### SRAM Macros

| Macro | Size | Trans/mm² | % of flip-flop max | Placements |
|---|---|---|---|---|
| `gf180mcu_ocd_ip_sram__sram1024x8m8wm1` | 301 x 516 um | 385k/mm² | 88% | 106 |
| `gf180mcu_ocd_ip_sram__sram512x8m8wm1` | 301 x 322 um | 332k/mm² | 76% | 47 |
| `gf180mcu_ocd_ip_sram__sram256x8m8wm1` | 301 x 225 um | 270k/mm² | 62% | 27 |
| `gf180mcu_ocd_ip_sram__sram64x8m8wm1` | 301 x 152 um | 173k/mm² | 39% | 1 |
| `gf180mcu_fd_ip_sram__sram512x8m8wm1` | 432 x 485 um | 154k/mm² | 35% | 36 |
| `gf180mcu_fd_ip_sram__sram256x8m8wm1` | 432 x 341 um | 124k/mm² | 28% | 2 |
| `gf180mcu_fd_ip_sram__sram128x8m8wm1` | 432 x 269 um | 98k/mm² | 22% | 2 |

The macro density includes the peripheral circuits (address decoders, sense amplifiers, I/O drivers) around the bitcell array, which is why larger macros of a family are denser than smaller ones.

### Best Standard Cell Regions

| Design | Peak 1mm² Trans/mm² | % of flip-flop max | Library |
|---|---|---|---|
| [MOLE](https://github.com/mole99/wsrun2-fabulous-fpga) | 353k/mm² | 80% | 7t-3.3V |
| [SCUP](https://github.com/sifferman/gf180mcu-peripherals) | 341k/mm² | 78% | 7t-3.3V |
| BTX1 | 331k/mm² | 75% | 7t-3.3V |
| [CLON](https://github.com/ThorbenMoos/Cloneless2) | 299k/mm² | 68% | 7t-5V |
| [T26A](https://github.com/TinyTapeout/tinytapeout-gf-26a) | 266k/mm² | 61% | 7t-5V |
| [AMM1](https://github.com/algofoogle/gf180ws2-raybox-zero) | 257k/mm² | 59% | 7t-5V |
| [T26B](https://github.com/TinyTapeout/tinytapeout-gf-26b) | 252k/mm² | 58% | mixed |
| [TQVC](https://github.com/MichaelBell/ws01-tinyQV) | 252k/mm² | 57% | 7t-5V |

Infrastructure cells are excluded from logic cell counts but their transistors (decoupling capacitors in particular) are included in transistor counts.

## Key Findings

1. The densest logic standard cell design, [CLON](https://github.com/ThorbenMoos/Cloneless2) (Cloneless2), achieves **23k logic SC/mm²** averaged over its core (30% of buffer max), with a peak of **30k logic SC/mm²** in its densest 1mm² region.

2. Standard cell libraries in use: **7t-3.3V** (53% of logic cells), **7t-5V** (46% of logic cells), **9t-5V** (2% of logic cells).

3. The median digital design achieves **7k logic SC/mm²** over its core. 12 of 34 designs exceed 10k logic SC/mm².

4. The best standard cell region reaches **353k transistors/mm²** ([MOLE](https://github.com/mole99/wsrun2-fabulous-fpga)); the most used SRAM macro, `gf180mcu_ocd_ip_sram__sram1024x8m8wm1`, is 385k transistors/mm².

5. Infrastructure cells (fillers, taps, antenna diodes, ties) outnumber logic cells **2.8 to 1** across the reticle (6.8M vs 2.4M). Any density analysis must exclude these to avoid dramatically overstating actual logic content.

6. The most common logic cell is **buff_2** (216k instances in 7t-3.3V).

## Per-Design Details

| Design | Cell | Die (mm) | Core mm² | Placements | Pads | Logic SC | Infra SC | Transistors | SRAM | Libraries |
|---|---|---|---|---|---|---|---|---|---|---|
| [0000](https://github.com/GTIceLab/ASHES-GF180nm) | `0000_chip_top_6_7` | 3.93 x 2.53 | 5.9 | 1 | 73 | 40 | 10 | 112,906 | 0 | mcu7t5v0: 40 |
| [AMM1](https://github.com/algofoogle/gf180ws2-raybox-zero) | `AMM1_chip_top_2_6` | 3.93 x 2.53 | 5.9 | 2 | 73 | 31,608 | 122,990 | 1,259,744 | 0 | mcu7t5v0: 31,608 |
| [AS04](https://github.com/AvalonSemiconductors/ws-submission-2026/) | `AS04_chip_top_10_0` | 3.93 x 5.12 | 14.3 | 1 | 75 | 87,322 | 494,369 | 1,784,287 | 0 | mcu7t3v3: 87,322 |
| [AS16](http://github.com/SUD0NET/as16) | `AS16_chip_top_0_7` | 3.93 x 2.53 | 5.9 | 1 | 73 | 5,508 | 92,536 | 1,135,048 | 2 | mcu7t5v0: 5,508 |
| BTX1 | `BTX1_chip_top_0_0` | 3.93 x 5.12 | 14.3 | 1 | 75 | 252,619 | 505,451 | 4,066,156 | 19 | mcu7t3v3: 252,619 |
| [CAB1](https://github.com/ZeduloTech/Cabrera) | `CAB1_chip_top_4_8` | 3.93 x 2.53 | 5.9 | 1 | 89 | 52,199 | 100,188 | 1,043,814 | 6 | mcu7t5v0: 52,199 |
| [CAFE](https://github.com/Essenceia/Expresso_ASIC_Chip) | `CAFE_chip_top_12_7` | 1.94 x 2.53 | 2.3 | 1 | 57 | 8,747 | 48,803 | 442,821 | 0 | mcu7t5v0: 8,747 |
| [CLON](https://github.com/ThorbenMoos/Cloneless2) | `CLON_chip_top_2_0` | 3.93 x 5.12 | 14.3 | 1 | 33 | 323,612 | 486,920 | 3,671,486 | 0 | mcu7t5v0: 323,612 |
| [DCO0](https://github.com/asinghani/ws-dco-tdc) | `DCO0_chip_top_0_6` | 3.93 x 2.53 | 5.9 | 1 | 73 | 7,139 | 100,281 | 1,184,643 | 0 | mcu7t5v0: 7,139 |
| [DPK1](https://github.com/dpks2003/bio-core) | `DPK1_chip_top_12_4` | 1.94 x 5.12 | 5.5 | 1 | 73 | 66,232 | 120,983 | 1,065,547 | 8 | mcu7t5v0: 66,232 |
| [DPK2](https://github.com/dpks2003/cordic-romless) | `DPK2_chip_top_13_7` | 1.94 x 2.53 | 2.3 | 1 | 57 | 33,464 | 73,753 | 483,418 | 0 | mcu7t5v0: 33,464 |
| [EURO](https://github.com/anfroholic/eurosynth) | `EURO_chip_top_2_7` | 3.93 x 2.53 | 5.9 | 1 | 73 | 68,077 | 129,324 | 1,069,880 | 0 | mcu7t5v0: 68,077 |
| FC01 | `FC01_TOP_12_6` | 1.94 x 2.53 | 2.3 | 1 | 12 | 0 | 0 | 68,234 | 0 | — |
| [FS01](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | `FS01_chip_top_14_0` | 1.94 x 5.12 | 5.5 | 1 | 73 | 3,540 | 87,332 | 1,225,935 | 0 | mcu7t5v0: 3,540 |
| [FS02](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | `FS02_chip_top_13_0` | 1.94 x 5.12 | 5.5 | 1 | 73 | 3,492 | 88,252 | 1,237,374 | custom | mcu7t5v0: 3,492 |
| [FS03](https://gitlab.com/Chips4Makers/arrakeen-sram-testchip) | `FS03_chip_top_12_0` | 1.94 x 5.12 | 5.5 | 1 | 73 | 3,788 | 78,222 | 1,109,012 | 0 | mcu7t5v0: 3,788 |
| [GD04](https://github.com/gregdavill/gf180mcu-racquet-1x0.5) | `GD04_chip_top_8_7` | 3.93 x 2.53 | 5.9 | 2 | 73 | 35,525 | 104,165 | 1,002,605 | 6 | mcu9t5v0: 35,525 |
| [HZ80](https://github.com/rejunity/ws0-z80-open-silicon-gf180mcu) | `HZ80_chip_top_12_2` | 1.94 x 5.12 | 5.5 | 1 | 73 | 5,143 | 80,093 | 831,740 | 0 | mcu9t5v0: 5,143 |
| [ISHI](https://github.com/ishi-kai/ISHI-KAI_Multiple_Projects_WaferSapce-GF180-2) | `ISHI_ISHI-KAI_WS_RUN2_13_4` | 1.94 x 5.12 | 5.5 | 1 | 145 | 0 | 63 | 98,529 | 0 | — |
| [KIAN](https://github.com/splinedrive/gf180mcu-kianv-rv32ima-sv32-ws02/) | `KIAN_chip_top_4_0` | 3.93 x 5.12 | 14.3 | 1 | 75 | 76,850 | 445,794 | 2,371,661 | 21 | mcu7t3v3: 76,850 |
| [MEME](https://github.com/anfroholic/meme_chip) | `MEME_chip_top_8_6` | 3.93 x 2.53 | 5.9 | 2 | 73 | 226 | 15,682 | 181,340 | 0 | mcu7t5v0: 226 |
| [MOLE](https://github.com/mole99/wsrun2-fabulous-fpga) | `MOLE_chip_top_8_0` | 3.93 x 5.12 | 14.3 | 1 | 75 | 211,813 | 341,915 | 4,113,914 | 13 | mcu7t3v3: 211,813 |
| [NAX1](https://github.com/ZeduloTech/Naxos) | `NAX1_chip_top_2_8` | 3.93 x 2.53 | 5.9 | 1 | 73 | 49,919 | 110,470 | 1,409,654 | 12 | mcu7t3v3: 49,717, mcu7t5v0: 202 |
| [OCD3](https://github.com/RTimothyEdwards/gf180mcu_ocd_sram_test) | `OCD3_gf180mcu_ocd_sram2_top_4_7` | 3.93 x 2.53 | 5.9 | 1 | 73 | 123 | 442 | 239,921 | 4 | mcu7t3v3: 123 |
| [PSOC](https://github.com/d-burnett/picosoc-on-waferspace) | `PSOC_chip_top_6_6` | 3.93 x 2.53 | 5.9 | 1 | 73 | 18,372 | 86,401 | 1,064,446 | 8 | mcu7t5v0: 18,372 |
| [QZ80](https://github.com/rejunity/ws0-z80-open-silicon-gf180mcu) | `QZ80_chip_top_14_6` | 1.94 x 2.53 | 2.3 | 1 | 57 | 5,096 | 36,102 | 343,883 | 0 | mcu9t5v0: 5,096 |
| [RLCM](https://github.com/EngGhaith/RLCM-Test-Passives-For-GF180MCUD) | `RLCM_RLCMV4_filled_14_2` | 1.94 x 5.12 | 5.5 | 1 | 247 | 0 | 0 | 44,298 | 0 | — |
| [SALU](https://github.com/StackDoubleFlow/alu_silicon) | `SALU_chip_top_13_6` | 1.94 x 2.53 | 2.3 | 1 | 57 | 1,608 | 36,011 | 416,485 | 0 | mcu7t5v0: 1,608 |
| [SCML](https://github.com/kjconway5/ML-Audio) | `SCML_chip_top_6_2` | 3.93 x 5.12 | 14.3 | 1 | 75 | 111,492 | 303,499 | 3,614,846 | 38 | mcu7t3v3: 111,492 |
| [SCMT](https://github.com/dhgaddy/microTheia) | `SCMT_chip_top_2_2` | 3.93 x 5.12 | 14.3 | 1 | 75 | 47,523 | 269,002 | 2,970,832 | 41 | mcu7t3v3: 47,523 |
| [SCTP](https://github.com/SlugTPU/gf180mcu-slugtpu) | `SCTP_chip_top_0_2` | 3.93 x 5.12 | 14.3 | 1 | 75 | 124,628 | 443,248 | 3,238,613 | 17 | mcu7t3v3: 124,628 |
| [SCUP](https://github.com/sifferman/gf180mcu-peripherals) | `SCUP_chip_top_4_2` | 3.93 x 5.12 | 14.3 | 1 | 75 | 239,123 | 684,932 | 3,806,825 | 0 | mcu7t3v3: 239,123 |
| [T0P3](https://github.com/TinyTapeout/tinytapeout-gf-0p3) | `T0P3_tt_gf_wrapper_6_0` | 3.93 x 5.12 | 14.3 | 1 | 75 | 118,911 | 216,633 | 2,081,504 | 1 | mcu7t5v0: 93,727, mcu7t3v3: 25,184 |
| [T26A](https://github.com/TinyTapeout/tinytapeout-gf-26a) | `T26A_tt_gf_wrapper_0_4` | 3.93 x 5.12 | 14.3 | 1 | 75 | 144,419 | 318,284 | 2,907,694 | 2 | mcu7t5v0: 144,371, mcu9t5v0: 48 |
| [T26B](https://github.com/TinyTapeout/tinytapeout-gf-26b) | `T26B_tt_gf_wrapper_2_4` | 3.93 x 5.12 | 14.3 | 1 | 75 | 155,961 | 329,068 | 2,970,303 | custom | mcu7t5v0: 153,556, mcu7t3v3: 2,405 |
| [TQVA](https://github.com/MichaelBell/ws01-tinyQV) | `TQVA_chip_top_13_8` | 1.94 x 2.53 | 2.3 | 1 | 57 | 35,711 | 62,585 | 480,963 | 1 | mcu7t5v0: 35,711 |
| [TQVC](https://github.com/MichaelBell/ws01-tinyQV) | `TQVC_chip_top_0_8` | 3.93 x 2.53 | 5.9 | 1 | 73 | 36,116 | 137,094 | 1,219,676 | 1 | mcu7t5v0: 36,116 |
| [TQVD](https://github.com/MichaelBell/ws02-tinyQV) | `TQVD_chip_top_14_8` | 1.94 x 2.53 | 2.3 | 1 | 57 | 23,689 | 40,036 | 619,827 | 5 | mcu7t3v3: 23,689 |
| TQVE | `TQVE_chip_top_14_7` | 1.94 x 2.53 | 2.3 | 1 | 18 | 24,213 | 70,319 | 994,648 | 10 | mcu7t3v3: 24,213 |
| [WSLG](https://github.com/89Mods/ws-logo-die) | `WSLG_chip_top_10_2` | 3.93 x 5.12 | 14.3 | 1 | 75 | 14,290 | 145,520 | 1,521,509 | 0 | mcu7t5v0: 14,290 |

## Methodology

- **Logic cell counts** come from walking the layout hierarchy and counting instances of every cell whose name contains a standard cell library prefix, excluding types starting with `fill`, `endcap`, `filltie`, `fillcap`, `tap`, `antenna`, `diode`, `tiel`, `tieh`.
- **Transistor counts** are the number of merged polygons in the boolean AND of the diffusion (22/0) and gate polysilicon (30/0) layers.
- **Core area** is (die width − 0.70mm) x (die height − 0.70mm), removing a 350um pad ring from each side.
- **Cell dimensions** are the width and height of each standard cell's placement boundary (GDS 0/0), measured from the cells present in this layout.
- **Theoretical maximum** = (1000um / cell width) x (1000um / row height).
- **Peak figures** are the best single cell of a 1mm x 1mm grid laid over each design, skipping grid cells that overlap an SRAM macro. Grid cells at the top and right edges of a die are smaller than 1mm², so peaks are lower bounds.
- **SRAM macros** are counted by cell name. The `sram_block_count` column of the summary CSV is kept for comparison with earlier results; it counts SramCore marker shapes, of which each GF180MCU macro has two.
- Designs placed more than once on the reticle are counted once.

### Difference from the March 2026 Run 1 report

The first version of the Run 1 report measured cell width and row height from each cell's overall bounding box. That box includes n-well and implant shapes which deliberately overhang the cell and overlap its neighbours, so it is larger than the area a placed cell occupies: 4.22 x 4.78um instead of 3.36 x 3.92um for a 7-track buffer. Theoretical maximum densities in that version were therefore about 35% too low, and every "% of max" figure correspondingly too high. This report uses the placement boundary. It also reported SRAM "blocks" by counting SramCore marker shapes, which gave twice the number of macros. Logic cell counts, transistor counts and achieved densities are unchanged.

---

*Generated by [ws-run-reports](https://github.com/wafer-space/ws-run-reports) from `G802.oas` (md5 `57fa57f52eac82835a051f2a353e5a30`) in [wafer-space/ws-run2](https://github.com/wafer-space/ws-run2). Analysis method: KLayout boolean geometry operations on GDS layers. Grid resolution: 1mm x 1mm. Density figures are rounded to the nearest 1k.*

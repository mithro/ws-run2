# MOLE: FABulous FPGA (ws-run2)

| | |
|---|---|
| Repository | https://github.com/mole99/wsrun2-fabulous-fpga @ 282dda8 (main, last commit 2026-09-16); submodule `ip/fabulous-tiles` @ 276f289 |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | TEMPLATE+NOTE (91% the project-template README plus about 160 words of own text) |

## What the repo actually contains

An improved FABulous eFPGA on the 3.3 V flow: 624 LUT4, 13 tiles each with a 3.3 V 1024x8 SRAM (`gf180mcu_ocd_ip_sram__sram1024x8m8wm1`), 13 `RAM_32x4_2R_1W` register files, 48 `GF_IOBUF` with input/output DDR registers (48 IDDR, 48 ODDR), 4 global buffers, WARMBOOT and SYS_RESET.

Libraries, read from the release netlist: 80,355 instances of `gf180mcu_as_sc_mcu7t3v3` standard cells, 13 ocd `sram1024x8`, and `gf180mcu_ocd_io` pads (53 `bi_24t`, 2 `in_c`, 1 `in_s`, 6 DVDD, 8 DVSS, 2 VDD, 2 VSS), so core and IO supplies are separate.

The repo has no `final/` directory. The release `final.zip` (in `../releases/`) holds SDF for 9 corners, SPEF (nom/min/max) and metrics: setup WNS 0 at every corner, worst slack +17.8 ns at max_ss_125C_3v00 against a 40 ns clock, 0 Magic and KLayout DRC errors, 0 LVS differences, 0 antenna violations, 81,515 instances (21,296 standard cells, 662 sequential), 29.6 mW flow power estimate. The release also has `chip_top.oas` and `classic_fabric_wsrun2.zip` (pips and bitstream spec).

### Changes from run 1

| | Run 1 | Run 2 |
|---|---|---|
| Standard cells | `gf180mcu_fd_sc_mcu7t5v0` | `gf180mcu_as_sc_mcu7t3v3` |
| SRAM | 6 x foundry 512x8, 5 V | 13 x ocd 1024x8, 3.3 V |
| Pads | `gf180mcu_fd_io`, core and IO supply shorted | `gf180mcu_ocd_io`, separate supplies |
| LUT4 | 480 | 624 |
| MAC tiles | 6 | removed |
| Register files | 12 | 13 |
| IO | plain pad config | GF_IOBUF with registers, IDDR/ODDR |
| Other | | SYS_RESET, 4 GBUF; repo split into `fabulous-tiles` submodule, extra tiles and fabrics; core ring moved from Metal2/3 to Metal4/3 |

Clock target is unchanged at 40 ns.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Leo Moser (GitHub mole99) | sole author (51 commits; 116 in the tiles submodule) | not stated (GitHub location: Austria) | git shortlog, GitHub profile |

## Value for GF180MCU characterisation and PDK development

### Verdict: Medium

Same programmable-test-vehicle argument as run 1, and stronger: separate core and IO supplies allow a core-voltage sweep (3.0 to 3.6 V) on programmed oscillators, the exact routed path of any bitstream can be reconstructed from `pips.txt`/`bitStreamSpec`, and the chip is an early full-scale user of the 3.3 V standard cells, 3.3 V SRAMs and ocd IO. Comparison data is STA only (SDF/SPEF), no SPICE.

### Test structures and measurable circuits

| Structure | Exercises | Access | Where |
|---|---|---|---|
| Post-fab programmable ring oscillators and delay lines | `as_sc_mcu7t3v3` cell and routing delay versus the 9-corner SDF | 48 fabric IOs | `ip/fabulous-tiles`, release `classic_fabric_wsrun2.zip` |
| 13 x 3.3 V ocd SRAM 1024x8 | SRAM macro function and timing | from fabric | SRAM tiles |
| `GF_IOBUF` | `bi_24t` slew, Schmitt, pull settings | pads | IO tiles |
| IDDR/ODDR registers | 2x-clock sampling of internal edges | pads | IO tiles |

### Candidate PDK additions

None taken to silicon. An eFuse macro set (`ip/gf180mcu_re_efuse`, from egorxe's gf180_efuse_compiler, 5 V libraries, 7 GDS) and a hand-built power-on reset (`ip/simple_por`: spice, GDS, LEF, Schmitt) were integrated on 2026-06-16 and removed in commit a6bd586 (2026-07-01); `macros_3v3.yaml` has them commented out and the final netlist contains neither. No reason for the removal is given.

Documented PDK/flow issues:

- DUALGATE / 3.3 V devices inside the foundry SRAM layout need a MAGIC_GDS_FLATGLOB list (`dcap_103*`, `din_*`, `mux821_*`, `rdummy_*`, `pmoscap_*`, `xdec_*`, `sa_*`, ...).
- `Metal2_ignore_active` for fill density.
- KLayout deck run as "all,-antenna,-density,-cup (disable CUP for now)".
- The Makefile marks `gf180mcu_osu_sc_gp9t3v3` and `gp12t3v3` as "(broken)".
- Commit 96cb2a4 "3.3V SCL fix" (PDK bump to f6eeac7).
- 478 antenna diodes inserted by manual ECO because the fabric macro has no standard cells.

### What would be needed to use it

Packaged or bonded die with separate core and IO supplies, SPI configuration, the Yosys/nextpnr flow for this fabric, and oscillator/delay-line bitstreams, which do not exist yet. FABulous's physical timing model exists only for sky130 and IHP.

## Notes and caveats

- Final views exist only in the release, not in git.
- No bring-up data or oscillator designs in the repo.
- Library names were read from the release netlist.

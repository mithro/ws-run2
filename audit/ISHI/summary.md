# ISHI: ISHI-KAI_Multiple_Projects_WaferSapce-GF180-2 (ws-run2)

| | |
|---|---|
| Repository | https://github.com/ishi-kai/ISHI-KAI_Multiple_Projects_WaferSapce-GF180-2 @ 1a0be37 (main, last commit 2026-07-14) |
| Slot | 0p5x1 (die 1936 x 5122 um measured from the GDS) |
| Top cell | ISHI-KAI_WS_RUN2 |
| Licence in repo | Apache-2.0 (`LICENSE`, copyright line left as the unfilled template "[yyyy] [name of copyright owner]") |
| README | OK by word count (1668), but it is the run 1 README with sections deleted; several statements and links are wrong for this repo |

## What the repo actually contains

A half-width re-spin of the run 1 ISHI-KAI analog multi-project die (see
`ws-run1/ISHI/summary.md`). Nine of the fifteen run 1 circuits are carried over
unchanged, re-placed inside a new, narrower pad ring. The repo was created and
finished in one day (four commits on 2026-07-14, all by Noritsuna Imamura).

Like run 1 it is a layout-and-logs repo: no schematics, netlists, testbenches or
simulation results. `schematic/README.md` links to the same three external
repositories as run 1.

| Path | Content |
|---|---|
| `gds/ISHI-KAI_WS_RUN2.zip` | Final top GDS (230 MB unzipped, 1423 cells) with fill. The only layout file; no per-member GDS, no frame GDS, no fill-free copy |
| `docs/pin_list.xlsx`, `pin_list.pdf` | 74-row pad list |
| `precheck_log/RUN_2026-07-14_11-31-08/` | One precheck run, all checks clean (density, zero-area, antenna, Magic DRC, KLayout DRC all 0), plus a render |
| `images/` | Annotated layout picture, precheck and submission screenshots, PLL pictures |

### Sub-designs

All have the same per-layer shape counts as the corresponding cells in the
run 1 top GDS, except where noted. Devices and designers are as in the run 1
summary.

| Cell | Designer | Circuit | Devices (upstream schematic) | Change from run 1 |
|---|---|---|---|---|
| `opamp_3zki` | 3zki (Mizuki Mori) | Rail-to-rail op-amp, 5 V | nfet_06v0 / pfet_06v0 L=1 um, 2 MIM caps | Identical; now rotated to a horizontal pad row |
| `opamp_gitefu` | gitefu | Two-stage op-amp | Schematic nfet/pfet_06v0_dn L=0.7; drawn without Dualgate | Identical |
| `opamp_noritsuna` | noritsuna | Two-stage op-amp | Schematic nfet_05v0_dn / pfet_05v0; drawn without Dualgate | Identical shapes; tap cell renamed |
| `opamp_yamada3` | yamada3 (Miho Yamada) | Two-stage op-amp | Schematic nfet_05v0_dn / pfet_06v0; drawn without Dualgate | One Metal1 shape fewer, three full-stack vias added |
| `chipathon2023_CS_BGR` | A. Tsuchiya (bandgap), yamada3 (current source) | 1.2 V bandgap and 20 uA Vth-referenced source | npn_10p00x10p00 (18), nfet/pfet_03v3, ppolyf_u | Identical |
| `SAR_ADC` | Maple0705, Gitefu, Tseng, Kinako | 6-bit SAR ADC, 8 MHz, 3.3 V | nfet/pfet_03v3 L=0.28, 64 MIM 7x7 um, 798 sc7 5 V cells | Identical |
| `chipathon2023_pll` | A. Tsuchiya | Analog PLL, 8 MHz to 48/40 MHz | nfet/pfet_03v3 L=0.33 VCO and charge pump, 06v0 switches, sc7 cells, high-res poly, 22 MIM | Identical |
| `ldo_noritsuna` | noritsuna and others | LDO 3.3 V to 3.2 V, 4 mA | pfet_03v3 waffle array m=7936, ppolyf_u, npn bandgap | A few Metal1/4/5 shapes removed, 36 full-stack vias added |

**Dropped from run 1:** the five-inverter block `inverter_all` (noritsuna,
ajisai, homelith, bols-blue, ponzu840w) and ice458's dynamic comparator
`cmp_ice458`. The README member list was trimmed accordingly but still opens
with "14 novice semiconductor designers" and still lists ajisai, who has no
circuit on this die.

### What else changed between the run 1 and run 2 submissions

- Slot halved from 1x1 to 0p5x1. Pad ring rebuilt with 72 pads (8 bottom, 28 right, 8 top, 28 left) instead of 74: 21 `asig_5p0`, 8 `bi_24t`, 5 `in_c`, 17 `dvdd`, 21 `dvss`. Run 1 used the `gf180mcu_ws_io__dvdd/dvss` wrappers; run 2 instantiates `gf180mcu_fd_io__dvdd/dvss` directly.
- Two new filler variants, `fill10_noVDD` (37 placed, only DVSS/VSS rail labels) and `fill10_supplyVDD` (28 placed, DVDD/VDD/DVSS/VSS labels), alongside stock `gf180mcu_fd_io__fill10`. This looks like a deliberately segmented VDD ring so that each circuit has its own supply (inferred from cell names and labels; not traced). The pin list correspondingly adds "reserved" dvss/dvdd pairs next to each block and gives every block its own VSS pad.
- Top-level structure changed: the frame is now a `TOP_FRAME` cell, member cells sit directly in the top cell, and top-level routing is drawn in the top cell.
- New wafer.space cells: `gf180mcu_ws_ip__project_id`, `__shuttle_id`, `__qrcode_id`, `__marker` in place of run 1's single `gf180mcu_ws_ip__id`.
- The logo is now an array of 81,286 instances of a 1 x 1 um Pad-layer square (`GRID` of `CELL`) rather than 325,554 flat Pad polygons.
- The unexplained 680 x 680 um single Pad opening over eight abutted probe-pad rows is kept, now at (507.7, 2258.7) to (1187.7, 2938.7).
- Precheck moved to a newer flow: 16 steps including a render step, `WS_SLOT`/`WS_ID` variables, DRC decks selected as `all,-antenna,-density,-cup`. The precheck design name is `TOP_ISHI-KAI` reading `TOP_ISHI-KAI.gds`, while the committed file's top cell is `ISHI-KAI_WS_RUN2`.
- The platform record points at an `.oas` layout; the repo has only a zipped `.gds`.

**No run 1 measurement results are published here or in the run 1 repo.** The
run 1 repo has optical photos of fabricated dies and chip-on-board assemblies
only. This README's "Chips / Sample Bare Die" section is copied from run 1 and
links to a `chip_photo/` directory that does not exist in this repo.

## Authors and affiliations

| Person or organisation | Role | Affiliation | Source |
|---|---|---|---|
| ISHI-KAI (Inter-linked Society on Homemade IC Kai) | Organiser | Community, https://ishi-kai.org/ | README, `gh api orgs/ishi-kai` |
| Noritsuna Imamura (`noritsuna`) | Sole committer (4 commits), integration; op-amp, LDO | SIProp.org | git log; GitHub profile company field |
| Akira Tsuchiya (`atuchiya`) | PLL, bandgap, original current source | Not stated (README calls him "Prof. Tsuchiya") | README |
| Mizuki Mori (`3zki`) | Rail-to-rail op-amp | Not stated | README, upstream ADC README |
| Miho Yamada (`keropiyo`, "yamada3") | Op-amp, current source | Not stated | README |
| `Gitefu` | Op-amp, ADC comparator | Not stated (graduate student, per README) | README |
| `maple0705`, `kinako71`, `tsengs0` | ADC logic and integration; latch and switches; MIM array | Not stated; not stated; JAIST | upstream ADC README; GitHub profile for tsengs0 |
| ajisai | Listed as member, no circuit on this die | Not stated | README |

## Value for GF180MCU characterisation and PDK development

### Verdict: High

The same probe-accessible analog blocks as run 1 on a second fabrication run,
which makes run-to-run comparison of the bandgap voltage, the 20 uA reference,
VCO frequency and op-amp offsets possible with identical layouts. As in run 1
there are no stand-alone device structures, and three op-amps do not match
their schematics.

### Test structures and measurable circuits

Probe pads are 80 x 80 um openings on 100 um pitch in rows of seven. Coordinates
are pad centres in um from the GDS origin (lower-left die corner), extracted
from `ISHI-KAI_WS_RUN2.gds`; names are the Metal5 labels in each cell.

| Structure | Exercises | Probe pads | Ring pins (per pin list) | Reference simulation (upstream only) |
|---|---|---|---|---|
| `opamp_noritsuna` | Two-stage op-amp gain, offset, GBW | x = 1276.6; y = 556.9 VSS, 656.9 OUT, 756.9 VINP, 856.9 VDD, 956.9 VINN, 1056.9 IB, 1156.9 VSS | 1 to 9 | AC testbench and PEX netlist, for 5 V devices |
| `opamp_gitefu` | Same | x = 1275.9; y = 1298.7 VSS, 1398.7 OUT, 1498.7 VINP, 1598.7 VDD, 1698.7 VINN, 1798.7 IB, 1898.7 VSS | 10 to 17 | Testbench, PEX netlist, for 6 V devices |
| `opamp_3zki` | 6 V MOS rail-to-rail op-amp | y = 3688.8; x = 594.3 VSS, 694.3 VB, 794.3 VINN, 894.3 VDD, 994.3 VINP, 1094.3 OUT, 1194.3 VSS | 29 to 36 | None |
| `opamp_yamada3` | Two-stage op-amp | x = 1328.5; y = 4021.6 VSS, 4121.6 IB, 4221.6 VINN, 4321.6 VDD, 4421.6 VINP, 4521.6 OUT, 4621.6 VSS | 37 to 44 | None |
| Current source | nfet_03v3 Vth, ppolyf_u, pfet_03v3 mirror | Shared column x = 1276.2, y = 2040.7 to 2640.7, unlabelled | 20 to 22 | 20 uA with supply and temperature sweeps |
| Bandgap | npn_10p00x10p00 Vbe, 16:1 ratio, ppolyf_u | Same shared column | 25 to 27 | 1.2 V with supply and temperature sweeps |
| SAR ADC | 8x8 MIM matching, 3.3 V comparator, sc7 cells at 3.3 V | Two rows y = 3889.2 and 4189.2, x = 597.5 to 1197.5, unlabelled | 45 to 59 | Transient CSVs, PEX netlist |
| PLL | VCO frequency versus `VCTRL`, free-run mode, lock at 48/40 MHz | Column x = 777.2, y = 1460.1 to 2060.1, unlabelled | 63 to 69 | Testbench, no numbers |
| LDO | pfet_03v3 waffle array, 10 mm ppolyf_u divider | Column x = 501.1, y = 559.7 to 1159.7; VSS at both ends, four VOUT, one unlabelled | 72 to 74 | PEX testbench |

Devices and domains: nfet_03v3, pfet_03v3, nfet_03v3_dn, nfet_06v0, pfet_06v0,
npn_10p00x10p00, ppolyf_u, high-res poly, MIM (2 fF/um2, Metal4 to Metal5), and
`gf180mcu_fd_sc_mcu7t5v0` cells. Chipathon blocks run at 3.3 V; `opamp_3zki` at
5 V.

### Candidate PDK additions

- `fill10_noVDD` and `fill10_supplyVDD`: IO filler variants that break or carry the VDD rail, which is what a multi-supply analog die needs and the stock IO library does not offer.
- `pads_ishikai` 7-pad probe row, and the pad glue cells (`ANALOG_CON`, `D_BI_T_CON`, `D_IN_C_CON`, `VDD_VSS_CON`), unchanged from run 1.
- Logo drawn as a Pad-layer array of 1 um squares: a useful stress case for Pad-layer DRC and density rules.
- PDK problems documented by the authors are all in the run 1 repo and the upstream repos (missing 5 V PFET model, MIM LVS naming, label-induced precheck failures, KLayout deep-DRC crash); nothing new is recorded here.

### What would be needed to use it

- Bare-die probing (7-pin 100 um pitch) or wire bonding to the 72-pad ring. Whether a wafer.space chip-on-board carrier fits this 72-pad arrangement is not stated.
- A verified pin list; the committed one cannot be right as written (below).
- Probe-pad maps for the unlabelled rows (ADC, PLL, bandgap and current source), traced from layout.
- SMUs, scope, 8 MHz clock source, 20 uA bias source. No test plan exists.
- Re-simulation of the gitefu, noritsuna and yamada3 op-amps with 3.3 V devices.

## Notes and caveats

- **Three op-amps are still drawn without the Dualgate and V5_XTOR layers** (zero shapes on 55/0 and 112/1 in `opamp_gitefu`, `opamp_noritsuna`, `opamp_yamada3`), exactly as in the run 1 top GDS, while their schematics use 5 V and 6 V devices. They are thin-oxide transistors at L = 0.5 to 0.7 um and should not be run at 5 V. Read from layer counts; no LVS was run. The pin list still types their pads `asig_5p0` and says nothing about supply voltage.
- `docs/pin_list` has 74 rows but the layout has 72 pads. Two rows look like duplicates: `OPAMP_noritsuna IB` appears as pins 3 and 8, and `ADC EOC` as pins 50 and 57. With those removed, the cell types match the layout on the right, top and left edges going counter-clockwise, except that each "reserved" dvss/dvdd pair is in the opposite order on the top and left edges. The bottom edge only matches if read right to left. Treat the pin numbers as unverified.
- README errors carried over from run 1: the "Project List" and schematic links point at the run 1 repo; the "Submitted Project" link is the run 1 project URL; the `chip_photo/` images do not exist; `gds/frame_ISHI-KAI.gds` and `gds/member_project/` do not exist. The second WSL image is still the run 1 precheck environment.
- No hash comparison with the platform is possible: the platform layout is OASIS, the repo layout is GDS.
- Schematics remain in three external repositories on mutable branches, so the exact sources of what was fabricated are not pinned.
- Authorship of individual blocks is taken from the run 1 README and the upstream repositories; this repo's history shows only the integrator.

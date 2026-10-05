# 0000: ICELab Test Chip (ws-run2)

| | |
|---|---|
| Repository | https://github.com/GTIceLab/ASHES-GF180nm @ 8c360e2 (`main`, last commit 2026-09-10) |
| Slot | 1x0p5 |
| Top cell | chip_top |
| Licence in repo | None (audit: MISSING; no LICENSE file, no SPDX headers) |
| README | Missing (no README anywhere in the tree) |

## What the repo actually contains

An analog test chip from the Georgia Tech ICE Lab carrying floating-gate (FG) circuits,
charge pumps to program them, and plain transistor characterisation cells. The GitHub
description calls the repo an "open-source GF180nm standard cell library" for the lab's ASHES
analog synthesis tool; "standard cells" here means fixed-pitch analog cells, not digital logic.

Flow: xschem schematics, magic layouts (`.mag`, tech `gf180mcuD`), KLayout DRC with the stock
PDK deck (`.lyrdb` files) and KLayout LVS (`.lvsdb`, for two cells). Top-level assembly was
done by hand in a layout editor; `2_Tools/` holds an experiment with the lab's `ashes_fg`
Python place-and-route (qrouter) on three cells only.

Tree:

- `1_Design/GF180_cells/`: one directory per cell (list below), plus loose
  `gf180mcu_fd_sc_mcu7t5v0__inv_1/inv_4/filltie.gds`, `SchottkyDiode.gds`, `hh_model_v5.mag`.
- `1_Design/Tapeouts/WaferSpaceShuttleRun2/`: `TrueFinalGds/chip_top.gds` (94 MB),
  `chip_top_filled.gds`, `chip_top_prefill.gds`, earlier `FinalGds/` and `PrecheckTesting/`
  versions, and `FinalGds/chip_top.lyrdb` (764 rule categories, 0 violations).
- `2_Tools/lib/`: `class_lib_GF180.py` (ASHES cell classes `TunnelingChargePump`,
  `SchottkyDiode`), cell GDS copies, `layer_map/gf180mcuD.json`, `tech_lef/gf180mcuD.lef`.
  `2_Tools/run_syn/`: a three-instance ASHES test (`chip.py`, generated `chip.v`, qrouter DEF).
- `3_Examples/`: onboarding material: an inverter schematic, NMOS and PMOS `nfet_03v3`/
  `pfet_03v3` I-V testbenches, and a copy of the 4x2 FG array layout.

What is on the die (cell hierarchy of `TrueFinalGds/chip_top_prefill.gds`):

| Cell | Function |
|---|---|
| `gf180_4x2_Indirect` | 4x2 array of indirectly programmed floating-gate pFETs |
| `gf180_FG_Characterization` | Single FG test cell with its capacitors broken out |
| `gf180_2TA_1FG_Strong` | Two transconductance amplifiers with FG-programmed bias/offset (4 floating gates) |
| `WTA` | 4-input winner-take-all current circuit (9 thick-oxide NFETs) |
| `3NFET`, `3PFET` | Three `nfet_03v3` and three `pfet_03v3` of different sizes |
| `HVSchottkyPump`, `TunnelingSchottkyPump`, `InjectionSchottkyPump` | Dickson charge pumps: `sc_diode` Schottky diodes + `cap_mim` (5 caps/11 diode cells, 4/8, 3/5) |
| `NonOvCLKGen` x3 | Non-overlapping two-phase clock generator from `gf180mcu_fd_sc_mcu7t5v0` cells (`nor2_1`, `inv_4`, `inv_20`, `clkbuf_2`, `clkinv_1`), one per pump |
| loose `inv_1`/`inv_4` | 7-track inverters (purpose not documented) |
| Pad frame | 54 `gf180mcu_fd_io__asig_5p0`, 2 custom `gf180mcu_fd_io__bare`, 8 `dvdd`, 8 `dvss`, wafer.space ID/logo cells, seal ring |

Present but not on the die: `hh_model_v5.mag` (a Hodgkin-Huxley neuron model built around the
4x2 array with MIM caps), `HVPump`, `InjectionChargePump`, `TunnelingChargePump` (earlier
junction-diode versions of the pumps).

Verification present: KLayout DRC databases for every cell and for the top level, all with
zero violations against the unmodified `gf180mcu.drc` from the ciel-installed PDK. LVS
databases for `NonOvCLKGen` and `InjectionSchottkyPump` (results not parsed). No LVS for the
FG cells or top level. No simulation outputs. No silicon data.

## Authors and affiliations

| Person / organisation | Role | Affiliation | Source |
|---|---|---|---|
| Luke Hanks (GitHub `LH220`) | Sole committer (11 commits, 2026-07-06 to 2026-09-10): cells, pumps, routing, final GDS | Georgia Tech ICE Lab (repo is in the lab's org; personal profile states nothing) | `git shortlog`, `gh api repos/GTIceLab/ASHES-GF180nm/contributors` |
| GTIceLab | Owning organisation: "Integrated Computational Electronics Laboratory at Georgia Tech", blog `hasler.ece.gatech.edu` | Georgia Institute of Technology | `gh api orgs/GTIceLab` |
| "Ike" | Directory `1_Design/GF180_cells/Ike/` holds the 3NFET/3PFET cells; presumably a second designer (inferred from the directory name only) | not stated | directory name |

## Value for GF180MCU characterisation and PDK development

### Verdict: High

Purpose-built characterisation silicon for a device the PDK does not offer (a floating-gate
transistor with injection and tunnelling), plus Schottky-diode charge pumps, bare MOSFETs of
three sizes and a custom ESD-less pad, all on analog pads. The limitation is documentation:
there is no pad map, model or test plan in the repo.

### Test structures and measurable circuits

How the floating gate is built (read from `4x2_Indirect/gf180_4x2_Indirect.mag` and the GDS
layers of the cell on the die; the functional interpretation of each well is inferred from
geometry and pin names):

- Only standard layers are used: Nwell 21/0, COMP 22/0, Poly2 30/0, Pplus 31/0, Nplus 32/0,
  Contact, Metal1-3 and Dualgate 55/0 (thick oxide). No DNWELL, no SAB, no MIM, no special
  marker. In magic the gate regions are `mvpmos`/`hvpmos`, which extract as `pfet_06v0`.
- Each floating gate is one Poly2 shape of about 19.1 um2 with **no poly contact**, crossing
  three separate n-wells:
  1. a transistor well: two thick-oxide pFETs, each W = 1.8 um, L = 0.55 um, sharing the
     floating gate (one for hot-electron injection programming, one in the signal path:
     "indirect" programming), drains on `Vd_P[]` and `Vd_R[]`;
  2. a wide well: a 7.35 um x 1.65 um poly-over-COMP MOS capacitor acting as the control gate
     (`Vg[]`);
  3. a narrow well shared by both columns: a 0.45 um x 0.55 um poly-over-COMP junction for
     Fowler-Nordheim tunnelling (`VTUN`).
- Four select pFETs with contacted gates (`Vsel[0..1]`) gate the rows. Array pins: `Vd_P[0..3]`,
  `Vd_R[0..3]`, `Vg[0..1]`, `Vs[0..1]`, `Vsel[0..1]`, `VINJ[0..1]`, `VTUN`. Cell size 37 x 11 um.
- DRC: zero violations on the stock deck for the cell (`gf180_4x2_Indirect.lyrdb`,
  `_magic.lyrdb`) and for the full chip. No waivers were needed or recorded.

| Structure | Parameter exercised | Access | Repo path | Simulation available |
|---|---|---|---|---|
| `gf180_4x2_Indirect` (8 FG pFETs) | Thick-oxide (Dualgate) gate-oxide tunnelling current versus voltage, hot-electron injection efficiency of `pfet_06v0`-type devices at L = 0.55 um, charge retention, control-gate coupling ratio, cell-to-cell mismatch | 17 analog pins (above); pad assignment not documented | `1_Design/GF180_cells/4x2_Indirect/` (`.mag`, `.gds`); no schematic | None |
| `gf180_FG_Characterization` | The same FG elements isolated: tunnelling junction (0.45/0.55 um), control-gate capacitor (7.35/1.65 um), a large 21.7 um x 2.45 um capacitor, five 2/1 um `pfet_06v0` and five 2/1 um `nfet_06v0`; the pin `Vpoly` suggests the normally floating poly is brought out so capacitances and thresholds can be measured directly | `Vpoly`, `Vgate`, `Vlarge`, `VTUN`, `VINJ`, `Vd`, `Vs`, `Vref`, `V2`, `Vout`, `VDD`, `GND` | `1_Design/GF180_cells/FGCharacterization/` (`.sch`, `_magic.gds`) | Schematic only; FG elements are drawn as `pfet_06v0` |
| `3NFET` | `nfet_03v3` Id-Vg / Id-Vd, Vth, leakage at W/L = 0.5/0.28, 5/0.28 and 10 x 5/0.28 um (thin oxide) | Common `Vg`, `Vs`, `GND`; drains `Vd_Small`, `Vd_Med`, `Vd_Large` | `1_Design/GF180_cells/Ike/3NFETs.gds`, `drc.mag` | `3_Examples/FET_Characterization/NMOS_testbench.sch` (deck only, no results) |
| `3PFET` | `pfet_03v3`, same three sizes | Common `Vg`, `Vs`, `VDD`; drains `Vd_Small`, `Vd_Med`, `Vd_Large` | `Ike/3PFETs.gds`, `pdrc.mag` | `PMOS_testbench.sch` (deck only) |
| `InjectionSchottkyPump` | PDK `sc_diode` forward drop and reverse leakage (0.62 um x 2 um, m = 4 per stage), `cap_mim_2f0fF` 40 um x 40 um, pump output versus clock frequency and load; 2 pumping stages + 40x40 um output cap | `Vin`, `PHI1`, `PHI2`, `Vout`, `GND`; clock from `NonOvCLKGen` (`CLK_IN`) | `1_Design/GF180_cells/InjectionSchottyPump/` (`.sch`, `.spice`, `.gds`, LVS runs) | Netlist only |
| `TunnelingSchottkyPump`, `HVSchottkyPump` | As above with more stages (4 and 5 MIM caps); generates the tunnelling voltage on chip, so also exercises MIM and Schottky/DNWELL breakdown limits | pump pins as above; output presumably on the bare pads (inferred) | `2_Tools/lib/gds/FinalPumps/*.gds`; `.sch` in `HVPump/` and `TunnelingChargePump/` describe the older `diode_pd2nw_06v0` versions | `TunnelingChargePump_TB.sch` (older version, deck only) |
| `NonOvCLKGen` | `gf180mcu_fd_sc_mcu7t5v0` cell delay (non-overlap time), drive of `inv_20` into MIM load | `CLK_IN`, `PHI1_out`, `PHI2_out` | `1_Design/GF180_cells/NonOvCLKGen/` (schematic, testbench, DRC, LVS) | `NonOvCLKGen_TB.sch`, extracted `NonOvCLKGen.spice` (no results) |
| `gf180_2TA_1FG_Strong` | Two OTAs (16 `nfet_05v0`, 34 `pfet_06v0` in the schematic) with FG-set bias: transconductance, offset programmability, FG retention in a circuit | `VIN1_PLUS/MINUS`, `VIN2_PLUS/MINUS`, `Vout1`, `Vout2`, `PROG`, `RUN`, `VD_P[0..1]`, `VD_R[0..1]`, `Vg[0..1]`, `Vsel[0..1]`, `VINJ`, `VTUN`, `VDD`, `GND` | `1_Design/GF180_cells/2TA/` (`.sch`, `.mag`, `.gds`) | Schematic only |
| `WTA` | Thick-oxide NFET matching and subthreshold behaviour (devices 5/1.5, 3.25/2.0, 1.5/1.0 um) | `Vin<0..3>`, `Bias<0..3>`, `Vbias`, `Vmid`, `GND` | `2_Tools/lib/gds/WTA.gds` only | None |
| `gf180mcu_fd_io__bare` pads (x2) | Pad capacitance and leakage without ESD devices; tolerance of the pad stack to programming voltages | direct | `1_Design/GF180_cells/BarePad/` | None |

Voltage domains: FG, OTA and WTA cells use the thick-oxide 5 V/6 V devices; `3NFET`/`3PFET` use
3.3 V thin oxide; the clock generators use the 7-track 5 V standard cells.

### Candidate PDK additions

- **Floating-gate pFET cell.** A complete, DRC-clean recipe for a single-poly FG memory
  element in stock GF180MCU layers (dimensions above). If silicon confirms injection and
  tunnelling, this is a candidate for a documented PDK device or parameterised cell; it would
  need a SPICE model (none exists here), an LVS recognition rule (the stock decks would see
  three `pfet_06v0` with an unconnected gate), and an antenna/floating-gate check exemption.
- **`gf180mcu_fd_io__bare`**: a 75 x 350 um pad cell with the standard DVDD/DVSS/VDD/VSS rail
  crossings and an `ASIG5V` pin but no Poly2 at all (no ESD clamps or resistor), in `.mag` and
  GDS with a clean DRC database. A high-voltage/low-capacitance analog pad is missing from
  the stock IO library.
- **Schottky diode in use.** The pumps instantiate the PDK `sc_diode` (DNWELL 12/0 + Schottky
  marker 241/0); the commit "figured out schottky diodes" (2026-07-09) indicates it took
  effort. Measured forward/reverse data would validate a device that is rarely exercised.
- **ASHES technology files**: `2_Tools/lib/layer_map/gf180mcuD.json`, `tech_lef/gf180mcuD.lef`
  and `class_lib_GF180.py` show what the lab's analog synthesis flow needs from the PDK.
- No DRC/LVS deck changes, waivers or PDK bug reports are recorded in the repo.

### What would be needed to use it

- A pad map. Top-level labels are the template names (`bidir_PAD[0..45]`, `analog_PAD[0..3]`,
  `input_PAD[0..3]`, `clk_PAD`, `rst_n_PAD`); nothing ties them to cell pins. It has to come
  from the authors or be traced in the GDS.
- A programming procedure and voltage limits for injection and tunnelling (not in the repo),
  and confirmation of which pads are the two bare ones.
- Equipment: semiconductor parameter analyser / SMUs with sub-pA resolution for FG charge and
  retention, a high-voltage source for `VTUN`, a clock source for the pumps. Bare-die probing
  or a package with direct analog pin access; the `asig_5p0` ESD diodes will clamp
  anything above the pad supply, so high-voltage nodes need the bare pads.
- A SPICE model or at least hand-calculated expectations for the FG cell.

## Notes and caveats

- The platform description lists three charge pumps, the 4x2 array, two transconductance
  amplifiers, an FG characterisation cell and NFET/PFET cells. The die also contains a `WTA`
  cell that is not mentioned.
- The pump schematics and `.mag` files in `HVPump/`, `InjectionChargePump/` and
  `TunnelingChargePump/` use `diode_pd2nw_06v0`; the pumps on the die are the `*SchottkyPump`
  versions, of which only the injection pump has a schematic and netlist.
- `4x2_Indirect` and `WTA` have no schematic at all. LVS was run only on the clock generator
  and injection pump.
- The submitted layout is an OASIS file; the repo holds nine GDS variants, so the hash could
  not be matched. `TrueFinalGds/chip_top.gds` is presumed to be the source.
- Several files carry Windows `:Zone.Identifier` side files and absolute paths under
  `/home/luha/`.
- The last commit message says "added general ASIC team onboarding information" but adds only
  the three example directories, no text.
- The FG well roles (injection/read, control gate, tunnelling) are inferred from geometry and
  pin names, consistent with the lab's published indirect-programming FG cells, but are not
  stated in the repo.

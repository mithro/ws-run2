# DCO0: Standard Cell DCO+TDC (ws-run2)

| | |
|---|---|
| Repository | https://github.com/asinghani/ws-dco-tdc @ c5b10fc (main, last commit 2026-07-14; single commit in history) |
| Slot | 1x0p5 (declared). The checked-in `src/slot_defines.svh` selects pad counts per `SLOT_*`; see caveat below |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 (LICENSE; GitHub-detected) |
| README | STUB (19 words: "A very experimental all-standard-cell DCO and TDC in gf180", plus a credit to the evezor docker starter kit) |

## What the repo actually contains

A purpose-built timing-measurement chip made only of `gf180mcu_fd_sc_mcu7t5v0` (7-track, 5 V library) standard cells, hand-instantiated in `src/chip_core.sv` with `(* keep *)` / `keep_hierarchy`. There is no macro, SRAM or analog block. I/O uses `gf180mcu_fd_io` (`in_s` clk, `in_c` rst and inputs, `bi_24t` bidirectional pads, `asig_5p0` analog pads, unused). Core and pad supplies are the same 5 V net (see the PADRING_DVDD comments in `src/chip_top.sv`). Flow is LibreLane (config `librelane/config.yaml`, slot YAMLs, `CLOCK_PERIOD: 200` = 5 MHz for the SPI-like control clock only; neither DCO is a constrained clock). `Checker.YosysSynthChecks` is switched off because the DCO deliberately ties tristate `invz_*` outputs together.

Directories:
- `src/chip_core.sv` (449 lines): the whole design (DCOs, TDCs, serial registers, dividers). `src/chip_top.sv`, `slot_defines.svh`: template padring. `src/sim_stubs.v`: sim models.
- `tb/tb_chip_core.sv`, `cocotb/chip_top_tb.py`: RTL testbenches (edge counting on DCO outputs, TDC scan readout).
- `submission/chip_top.gds.gz` (15.6 MB): the submitted layout. No LVS/DRC/STA reports, no `final/` directory in the repo.
- `experiments/`: ~400 ngspice decks in `experiments/spice_sim/`, Python drivers in `experiments/scripts/` (hard-coded `/home/anish/...` paths), a few result text files/PNGs in `experiments/results/`, a small RTL TDC prototype in `experiments/rtl` and `experiments/tb`. `experiments/README.md` says these are "a bunch of random (mostly ai-written) SPICE sims from early experiments".
- `docker/`, `docker-compose.yml`: build/sim containers from the evezor starter kit.

### The oscillators (two independent DCOs)
Both are NAND-gated ring oscillators (`nand2_1` with enable, feedback from `out`); each stage is built from `dco_tunable_stage` / `dco_fixed_stage` modules.
- DCO1 "fast": 7 inversions: `nand2_1` + 6 stages (fs0 tunable, fs1 fixed `inv_1`, fs2 tunable, fs3 fixed, fs4 tunable, fs5 tunable). Each tunable stage has a `dlyd_4` delay cell, a `mux2_1` bypass (coarse bit selects delayed or direct input), then `invz_1` always enabled plus parallel tristate inverters `invz_1`, `invz_2`, `invz_4`, `invz_8` enabled by fine bits [0..3] (binary-weighted drive).
- DCO2 "slow": 9 inversions: `nand2_1` + 8 stages. Every stage has at least one `dlyd_4` before an `inv_1`; the 4 tunable stages have two `dlyd_4` in series with a mux selecting 1 or 2, and the same `invz` fine-drive bank.
- Control: 16-bit shift register (`dco_shift_clk`, `dco_shift_data`); when `dco_shift_latch`=1 on the clock edge the word is captured: `dco1_word = {coarse[3:0], fine[3:0]}` from bits [7:0], `dco2_word` from bits [15:8]. Reset state is 0 (so coarse=0, fine=0 = the weakest-drive, no-extra-delay setting).
- So coarse: 4 bits, each adding one `dlyd_4` into one stage (thermometer-like by stage, 16 combinations, 1 inserted dlyd_4 per set bit); fine: 4 bits binary-weighted drive strength (16 steps), applied to all four tunable stages at once.

### The TDCs (six instances of `tdc_three_level`)
Each has three delay lines, all started by `start`, sampling `stop` with D flip-flops (`dffrnq_1`) clocked from the delayed `start` taps:
- FINE: 16-tap Vernier. START chain is 2x `inv_1` per tap, STOP chain is 2x `inv_4` per tap; the capture flop for tap i has CLK = START tap, D = STOP tap. The intended resolution is the per-tap difference of the two inverter-pair delays (the author's SPICE implies roughly 17 ps per tap, see below).
- COARSE: 16 taps, one `dlyd_4` per tap, `stop` sampled directly by each tap flop.
- XCOARSE: 8 taps, four series `dlyd_4` per tap.
- 40 capture bits per TDC (FINE[0..15], COARSE[0..15], XCOARSE[0..7]) are copied through a `mux2_1` + `dffrnq_1` scan chain (`scan_capture_dff`): latch=1 loads captures, latch=0 shifts toward `scan_out` (chain order FINE[0..15], COARSE[0..15], XCOARSE[0..7]; `scan_in` is tied to 0 and XCOARSE[7] is the stage that drives `scan_out`).
- Instances: TDC1 start=A stop=B, TDC2 start=B stop=A (swapped, to extract pad/path skew), TDC3 start=DCO1 out stop=C, TDC4 start=C stop=DCO1, TDC5 start=DCO2 stop=D, TDC6 start=D stop=DCO2. A..D are external inputs through `clkbuf_4` input buffers.

### Readout and I/O mapping (from the header of `chip_core.sv`)
- Inputs (core indices): 0 DCO1 enable, 1 DCO2 enable, 2 DCO shift data, 3 DCO shift clock, 4 DCO shift latch, 5 TDC scan clock, 6 TDC scan latch, 7..10 TDC A, B, C, D.
- Outputs on bidir pads 0..11: 0 DCO1 (through two `clkbuf_16`), 1 DCO1/2, 2 DCO1/8, 3 DCO2, 4 DCO2/2, 5 DCO2/8 (dividers are `dffrnq_1` toggle flip-flops reset by DCO enable), 6..11 scan-out of TDC1..TDC6 (each through a `buf_16`). Bidir pads 0..11 are output-enabled, all other bidirs are inputs. The DCO frequency is measured by an external counter/scope on pad 0..5, the TDC codes by clocking the scan chain from outside. No on-chip counter, no UART/SPI.
- Output pads are `bi_24t` with CS=0, SL=0 (CMOS, fast slew). A 100-300 MHz DCO through the pad/bond/probe will be bandwidth-limited; the /2 and /8 outputs are for that reason (inferred).

### Simulation data in the repo (what silicon could be compared against)
All ngspice, 5.0 V, `temp=25`, typical models only (`experiments/spice_sim/sm141064_typical.spice` and `smbb000149_typical.spice` are copied into the repo, with `mc_skew=3` style params set in the header). No voltage or temperature sweep, no corner runs, no Monte Carlo. Results that are actually saved:
- `experiments/spice_sim/dco_alt.log`: alternating tunable/fixed rings, 11 stages: 99.8 MHz (code 0), 124.0 (8), 126.7 (16), 127.9 (24), 128.5 (32); 13 stages: 92.4 to 116.5 MHz. Saturates quickly with the 32-code thermometer fine drive used in those earlier variants (code 0 vs 8 is a ~24 % jump, then steps of ~0.1-1 MHz).
- `dco_11st.log` (tail): 146 to 1189 MHz over 33 codes, 8.12x range, median step 0.74 MHz, last steps 0.3 MHz around 187-193 MHz. `dco_therm_scan.log` and `dco_therm_scan2.log`: ring-length scans (9-19 stages) with fixed delay cells; several runs TIMEOUT (no oscillation), and some rings ran at 2.85-2.95 GHz, i.e. inverter-only rings, an unphysical-looking regime the author was probing.
- `experiments/results/spice_ringosc.txt`, `spice_3inv.txt`, `spice_synth_ringosc.txt`, `spice_out.txt`: waveform tables of small rings (raw columns: time and node voltages). No summary table.
- TDC: `tdc_sweep.log`, `tdc3_sweep.log`, `tdc3d_sweep.log`, `tdc_wide.log` give thermometer codes vs injected start-stop delay. FINE: 0 ps gives 10 ones of 16, 50 ps 7, 100 ps 4, 150 ps 1, 200 ps 0, i.e. the code falls about 3 taps per 50 ps, which is roughly 17 ps per tap (inferred from those numbers), with a usable fine range of about 0-200 ps. COARSE: about 1.2 ns per `dlyd_4` tap (16 taps, ~19 ns span; ones count drops 1 per ~1.0-1.2 ns), XCOARSE: ~4.9 ns per tap (8 taps, ~40 ns span). Summary of the author's own resolution analysis (tdc3_sweep.log): FINE and COARSE overlap between 0 and ~225 ps.
- `experiments/spice_sim/dly_meas_*.sp` (inv_1, dlya/b/c/d_1/2/4, buf_*, clkbuf_*): decks that measure the 50 % to 50 % rising delay of each cell with `.meas`, but the repo has no output of them (no table in the log files). `run_dly_meas.py` would reproduce these.
- `post_harden_dco.sp` plus `run_post_harden_dco.py`: attempted full-chip SPICE from the Magic-extracted `chip_top_nostubs.spice` with DCO word at reset (fine 0, coarse 0). The only log (`post_harden_dco.log`) is one line ("Generated ... with 58 chip_top ports"), so there is no post-layout frequency result in the repo.
- `scripts/run_final_dco_spice.py` simulates the exact final fast and slow ring structures (fine/coarse sweeps) but no log or result file from it is in the repo. The comments in `chip_core.sv` give expected bands only: fast DCO "roughly 100-300 MHz", slow DCO "roughly 10-50 MHz".

Layout facts from the GDS (parsed top-cell instance counts, read directly): 304 `dlyd_4`, 198 `inv_1`, 192 `inv_4`, 518 `dffrnq_1`, 248 `mux2_1`, 16/8/8/8 `invz_1/2/4/8`, 2 `nand2_1`, 6 `buf_16`, 8 `clkbuf_16`, 6 `clkbuf_4`, 8 `buf_4`, 46 `bi_24t`, 4 `asig_5p0`, 5 `in_c`, 1 `in_s`, plus 5550 `dlyb_1` (hold-fix buffers inserted by the resizer, source not identified) and ~3.3e4 `filltie`/fillcaps. The dlyd_4/inv/dff counts match six TDCs plus both DCOs exactly (6x48+16 dlyd_4, 6x32 inv_4, 518 DFFs), so the whole structure is in the submitted layout.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Anish Singhani (GitHub asinghani) | sole committer; design, SPICE experiments | not stated in repo; GitHub bio "Open-source FPGA & ASIC tooling", New York City, no company | `git shortlog` (author "Anish"), GitHub profile (gh api) |
| evezor (Andrew Wingate) | author of the docker starter kit this is based on | Evezor (GitHub profile / README link) | README, gh api |
| Leo Moser / wafer.space | upstream project template | not stated | template files (AUTHORS not present here) |

## Value for GF180MCU characterisation and PDK development

### Verdict: High
This is a purpose-built characterisation vehicle: two tunable ring oscillators and six Vernier/delay-line TDCs, all out of stock 5 V standard cells, with direct pad access to the oscillator outputs and a scan readout of the TDC codes. It exercises exactly the cells whose liberty/SPICE delays one wants to check (`inv_1`, `inv_4`, `dlyd_4`, `invz_*`, `nand2_1`, `mux2_1`, `dffrnq_1`), and the author already has typical-corner ngspice numbers to compare with. One serious caveat on pad access (below) may limit what is usable on the actual die.

### Test structures and measurable circuits
All in the 5 V core domain (VDD 5 V, single supply for core and pads), library `gf180mcu_fd_sc_mcu7t5v0`.

| Structure | What it exercises | Access | Where |
|---|---|---|---|
| DCO1 fast ring (nand2_1 + 6 stages, 4 `dlyd_4`, `invz_1/2/4/8` fine bank, `mux2_1` bypass) | `dlyd_4` and inverter delay, tristate-inverter drive strength vs code | frequency on bidir pad 0, /2 pad 1, /8 pad 2 | `src/chip_core.sv`, `dco_fast`, `dco_tunable_stage` |
| DCO2 slow ring (nand2_1 + 8 stages, 8 to 12 `dlyd_4` depending on code) | long-delay-cell (`dlyd_4`) delay, ~10-50 MHz target | pads 3,4,5 | `dco_slow`, `dco_slow_tunable_stage` |
| TDC FINE Vernier (16 taps, `inv_1` pair vs `inv_4` pair) | inverter delay difference by drive strength (tens of ps) | scan out pads 6..11 | `tdc_three_level`, g_fine |
| TDC COARSE (16x `dlyd_4`) and XCOARSE (8x4 `dlyd_4`) | `dlyd_4` delay (~1.2 ns per cell in the author's typical SPICE), ~19 ns and ~40 ns spans | scan out | g_coarse, g_xcoarse |
| TDC1/TDC2 swapped start/stop on the same A,B pads | pad/input-buffer skew calibration | A,B inputs (core input 7, 8) | `tdc1`, `tdc2` |
| TDC3-6 (DCO vs external C/D edge) | DCO period/phase vs external reference | | `tdc3`..`tdc6` |
| Simulation baseline | ngspice typical 5 V 25 C only | `experiments/spice_sim/*.log`, `experiments/results/` | see above |

Simulation results do exist in the repo for typical corner (DCO frequencies vs code, TDC thermometer codes vs delay), but no per-cell delay tables are saved, there are no PVT corner results, and no post-layout (extracted) results (the post-harden log is empty). Comparing silicon across voltage and temperature to liberty `tt/ss/ff` would therefore need a fresh simulation of the extracted netlist (the Magic extraction was done by the author but is not in the repo; only the GDS is).

### Candidate PDK additions
Nothing found as a new cell or macro. Relevant PDK observations from the repo: (a) the design needs the Yosys conflicting-driver check turned off for tied-together tristate `invz_*` outputs (config comment); (b) the author bridged a PDK extracted-netlist mismatch in SPICE (`gf180mcu_fd_sc_mcu7t5v0__endcap` defined with two ports in the Magic extraction but four in the PDK SPICE, see `post_harden_dco.sp` comment); (c) the first-order point that a cell-only ring/TDC is a convenient PDK regression test for liberty versus SPICE.

### What would be needed to use it
- Packaged or bare-die access to 4 input pads, 12 output pads and power; a fast scope or frequency counter (DCO outputs up to several hundred MHz; use the /2 and /8 pads), a pulse generator with controllable ps-scale A/B skew for TDC calibration (or use the DCO as start with an external C trigger), and a host MCU to bit-bang the 16-bit shift register and the scan chain.
- A test plan and pin list is not written; the pad map is only in the header comment of `chip_core.sv`. The README is a stub.
- A voltage/temperature chamber and a bench supply (5 V core, sweep roughly 4.5-5.5 V) plus the DCO and TDC code sweeps; simulation of the extracted netlist at the same corners.

## Notes and caveats
- **Pad-count mismatch (important, partly inferred).** The submitted GDS has only 4 `gf180mcu_fd_io__in_c` input pads plus 1 `in_s` (clk), 46 `bi_24t` and 4 `asig_5p0`, which is the `1x0p5` pad map (`NUM_INPUT_PADS=4`, `NUM_BIDIR_PADS=46`). But `chip_core.sv` uses `input_in[0..10]` (11 control/measurement inputs, defaults to 12 inputs, the 1x1 pad map) and its testbenches use 12 inputs. With 4 input pads, `input_in[4]` to `input_in[10]` are out of range in the submitted configuration (DCO shift latch, TDC scan clock/latch, TDC A to D). I could not tell how Yosys resolved them (likely constants or undriven). If so, on the real die only DCO1 enable, DCO2 enable, shift data and shift clock are reachable: the DCO words could never be latched (they would stay at the reset code 0) and the TDCs would have no external start/stop or scan readout. Anyone planning to bring up this die must check the netlist (`final/pnl` is not in the repo) or the GDS connectivity before relying on the TDCs. The bidirectional pads 12+ are inputs (`bidir_ie` set) but `bidir_in` is only consumed by a keep wire, so they cannot substitute.
- 5550 `dlyb_1` cells in the layout (resizer hold fixing with `PL_RESIZER_HOLD_SLACK_MARGIN 0.35`); where they sit is not stated. If any ended up in the TDC `stop`/D paths or the delay lines they would shift measured codes by an amount SPICE did not include (inferred risk, not verified).
- STA is only against a 5 MHz virtual clock on `clk_PAD`; the rings and TDC sampling have no timing constraints, so liberty/STA says nothing about them.
- The experiments directory is mostly AI-written by the author's own description; scripts have hard-coded `/home/anish/wafer_space_docker_based_starter_kit/...` paths; some earlier ring variants (thermometer-coded 32-step `invz` banks) differ from the final 4+4 bit design in `chip_core.sv`.
- Final-design (`run_final_dco_spice.py`) results were not saved, so the "100-300 MHz" and "10-50 MHz" figures are expectations in code comments, not recorded simulation results.
- No releases, no silicon test results.

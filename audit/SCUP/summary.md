# SCUP: GF180MCU Peripherals (ws-run2)

| | |
|---|---|
| Repository | https://github.com/sifferman/gf180mcu-peripherals @ bee7cb6 on `main` (last commit 2026-06-20); the real design is on `dev` / `peripherals-mvp` @ 74c6a42 (2026-07-14) |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | GPL-3.0 (LICENSE; "inherit GPLv3 from WangXuan95/FPGA-SDcard-Reader" commit) |
| README | TEMPLATE on main (777 words, identical to the template); a real README exists on dev |

## What the repo actually contains
**The cloned `main` is the bare wafer.space template** (two commits, only `chip_core.sv` with a counter and `sram512x8` instances, no peripherals or PLLs). The real project is on `origin/dev` and `origin/peripherals-mvp` (both 74c6a42). I read these with `git show origin/dev:...`; all statements below come from dev.

Chip: SCUP, "Santa Cruz Usable Peripherals", a 3.3 V test chip and reusable IP library, 1x1, 74-pad ring (about 7 input pads retyped to bidir: NUM_INPUT 12 to 5, NUM_BIDIR 40 to 47), 50 MHz clock (RMII needs it). A host PC reads/writes memory over UDP through a hardware UDP-to-AXI-lite bridge (`ethernet-host/dma.py`), no soft CPU.
- RMII Ethernet MAC + UDP stack (LAN8720A PHY, REF_CLK-in mode): Alex Forencich verilog-ethernet (fork sifferman/alexforencich_ethernet, branch waferspace-2026.06.30) with `src/eth/*` glue.
- SDRAM controller: ultraembedded core_sdram_axi4 (`sdram_wrap.sv`) for a Winbond W9825G6KH x16.
- SD card: WangXuan95 FPGA-SDcard-Reader, modified (`src/sdcard/`, split CMD IO), file-to-LED, time-shared on the pads by a mode strap; this is why the design is GPLv3.
- AXI4-lite interconnect, scratch RAM, CSR bus.
- ADPLL array (`src/adpll/adpll_array.sv`, `adpll_config.sv`, `adpll_array_csr.sv`) from the submodule sifferman/adpll @ 5c78a74 (ssh URL in `.gitmodules`, **not initialised in the clone**; available as `/backups/github/github.com/sifferman/adpll.git`).
- Flow: LibreLane + slang (`--max-constexpr-steps 1000000000`), 3.3 V (gf180mcu_as_sc_mcu7t3v3, ocd_io), no SRAM macros in the final design, topological Netgen LVS, custom orthogonal KLayout metal filler (`librelane/klayout_fill/`). SDC with per-interface datasheet I/O delays and generated clocks for the forwarded RMII ref_clk and SDRAM clock.
- Results documented in STATUS.md/questions.md: DRC (Magic + KLayout), LVS ("match uniquely", 274,538 devices), antenna clean; setup clean at all corners; RTL sim and VCS gate-level sim pass for Ethernet, SDRAM and PLL CSR. Hold on SDRAM output I/O and RMII RX margins were discussed and closed by SDC modelling. `signoff/` holds one metrics file and the "waferspace-resubmit" note (precheck PASSED 2026-07-14, sha256 d60b956c...; GDS not in git).

### The PLLs
- **Type: all-digital, standard-cell, ring-oscillator DCO ADPLLs** (not analog). The control loop is plain RTL.
- **DCO:** NAND2 enable gate + chains built from `gf180mcu_as_sc_mcu7t3v3` inv_2, nand2_2, mux2_2 (and dlybuff_2 in the TDC), `keep`/`dont_touch`, behind a `Target` parameter in `rtl/tech_cells/`. Four ring styles: binary-weighted delay select, thermometer, muxtap (ring length via a mux tree), coarse/fine. 5- or 7-bit tune.
- **Loops:** frequency-locked (edge counter, F_DCO = mul/div x 50 MHz) with bang-bang, proportional-integral or gear-shift filters; and phase-locked (flash TDC `adpll_tdc_flash` made of dlybuff_2 delay line + phase detector, with proportional-integral filter).
- **Array in the submitted design:** NumPll = 10 curated configurations (index: filter x DCO x tune bits: 0 bb x binary x7, 1 pi x thermometer x7, 2 gear x muxtap x5, 3 bb x muxtap x5, 4 pi x muxtap x5, 5 bb x thermometer x5, 6 gear x coarsefine x7, 7 phase pi x thermometer x7, 8 phase pi x muxtap x5, 9 phase pi x binary x7). Earlier plans for 48/36/24/16/12 PLLs failed placement or routing (congestion); the DCOs are routing-heavy.
- **Sources:** the sifferman/adpll repo (BSD-3, E. Sifferman, "grounded" in Staszewski and Balsara 2006, Razavi, Kratyuk 2007, Hanumolu 2007, Da Dalt 2005). Nothing taken from other designs.
- **How outputs are observed:** control and readout via the Ethernet CSR (0x2000_0000): enable, mul, div, per-PLL lock flag and tune code. A CSR-selected observation mux for the DCO clock + lock exists in RTL but **is not routed to a pad** (chip_core comment: asig_5p0 pads cannot carry routed digital signals, LVS issue); so there is no direct frequency measurement. Frequency at lock follows from mul/div x 50 MHz and the tune code gives the code-vs-frequency point.
- **What was simulated:** behavioural RTL sims on stock Icarus with a behavioural DCO; ngspice + Icarus gate-level mixed-signal cosim (extracted ring from the hardened `ring_dco` macro via Magic, ngspice >= 42), 16 configs x process corners in the adpll repo's CI; `docs/figures/dco_freq_vs_code.png`, `dco_pvt_envelope.png`, `corner_{ff,ss,typical}.dat`, `dco_curves/tt_{binary,muxtap,thermometer}.dat`. Example typical-corner data: binary code 0 338 MHz, 8 239, 16 184, 24 150, then 32 385 (non-monotonic), 127 222 MHz. Long-ring multi-wavefront behaviour is noted (STATUS.md). In gate-level sim the ADPLLs are kept disabled (enabling the structural ring exploded the event queue); lock in the full chip is verified only by the cosim, and the chip-level ngspice cosim is of single ADPLLs, not the full chip.

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| Ethan Sifferman | sole committer, all design | UC Santa Cruz (GitHub: "Lecturer turned PhD student at UC Santa Cruz", company UC Santa Cruz) | `gh api users/sifferman` |
| Leo Moser | template author | not stated here | AUTHORS.md |
| Third-party: Alex Forencich, ultraembedded, WangXuan95 | vendored IP | | submodule URLs |
Course/lab: none stated in this repo.

## Value for GF180MCU characterisation and PDK development
### Verdict: High
It carries 10 distinct standard-cell ring DCOs and phase-locked/frequency-locked loops with SPICE-vs-RTL models, readable over Ethernet, plus a full set of timing and signoff data. The weakness is that the DCO clock is not on a pad. Valid only for the dev-branch design.
### Test structures and measurable circuits
| Structure | What it exercises | Access | Where (dev branch / adpll repo) |
|---|---|---|---|
| 10 ring DCOs (inv_2, nand2_2, mux2_2 chains, 4 styles, 5/7-bit tune), 3.3 V | std-cell delay vs code, PVT; model check against the extracted-SPICE curves | Ethernet CSR at 0x2000_0000 (enable, mul, div, lock, tune); no pad for DCO clock | `src/adpll/*`, `third_party/adpll/rtl/dco/*` |
| 3 flash TDCs (dlybuff_2 delay lines) | dlybuff_2 delay and linearity (via phase-lock tune/phase codes) | CSR | `third_party/adpll/rtl/tdc/adpll_tdc_flash.sv` |
| Pad-timing: RMII/SDRAM/SD I/O at 50 MHz on ocd_io pads | pad (`bi_24t`, `in_c/in_s`) delay, drive, slew | pads | `librelane/chip_top.sdc` |
Simulation results to compare silicon to: SPICE curves in `docs/figures/*.dat`, `dco_curves/*.dat` and cosim logs (adpll repo); STA at 9 corners; GL sim.
### Candidate PDK additions
- Ring DCO and TDC cell wrappers as a retarget seam (`tech_cells`).
- The M2.4 density rule (Metal2 coverage > 30 %): stock filler reached only 29.54 %, which forced a custom KLayout filler (`librelane/klayout_fill/fill_{all,comp,metal,poly2}.rb`, 2.5 um M2 squares at 1.0 um spacing, orthogonal lattice). Candidate for the template/precheck.
- Template power-pad fix (fd_io 3-pin) prepared on a branch `fix-fd-io-power-pad-pins` of the author's template fork (not upstreamed per STATUS.md).
- yosys-slang `--max-constexpr-steps` accumulation bug; netgen topological LVS setup for LVS-ignore cells.
- asig_5p0 analog pads cannot take routed digital signals without an LVS failure (documented in chip_core comments).
### What would be needed to use it
A packaged PCB with the LAN8720A PHY (REF_CLK-in), a 50 MHz oscillator, the SDRAM (W9825G6KH), and a host sending UDP via `ethernet-host/dma.py`; the custom PCB must drive the retyped bidir pads as I/O (`docs/hardware-notes.md`). To measure DCO frequency directly one would need DCO clock access, which the design lacks (inferred: use lock-frequency and tune code over CSR, or probe die internals).
## Notes and caveats
- **The platform repo link lands on a template-only `main`.** Make sure the dev branch is used. The precheck-passing GDS hash (d60b956c...) is recorded on dev, not on main.
- dev README table says "10x mux-chain ring DCO"; the tree supports 4 DCO styles x 3 filters.
- RMII RX at 50 MHz was reported marginal in STA at SS (-1.0 ns TT, -5.9 ns SS in an earlier run; later SDC modelling was said to close it); the final timing numbers on the submitted layout are not in the repo (one metrics.csv from RUN_2026-06-21).
- The submitted layout is "pre-fill stage of RUN_2026-07-08_13-52-47" and I could not verify it.
- Course/institution for the SC** group: SCTP states the CSE 127A/B Capstone at UCSC; SCML cites UCSC ECE 153/250 lectures; SCUP's author is at UCSC (GitHub profile); SCMT has only a GitHub bio. So UC Santa Cruz is supported for SCTP, SCML, SCUP, and by hint (bio, emails) for SCMT.

# GD04: Racquet Wide 1x0.5 (ws-run1)

| | |
|---|---|
| Repository | https://github.com/gregdavill/gf180mcu-racquet-1x0.5 @ a64a899 (develop, last commit 2026-04-05; tag release-r1p0 = aa954be, 2025-12-11) |
| Slot | 1x0p5 (die 3932 x 2531 um) |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 (LICENSE file) |
| README | TEMPLATE: 100% identical to the wafer-space project-template README, 0 words of own text |

Run 1 and run 2 point at the same repository and commit (see "Run 1 versus run 2" below); this file is identical in ws-run1/GD04 and ws-run2/GD04.

## What the repo actually contains

A 6-core SERV multi-core SoC (the "wide" half-height configuration of Racquet): `NUM_PROC_CORES = 6` (commit aa954be "Drop to 6 cores", earlier 8 and 9), six `gf180mcu_fd_ip_sram__sram512x8m8wm1` macros placed in two columns of three (`librelane/config.yaml`), Wishbone crossbar with GPIO/UART/timer/queue peripherals, SPI-flash boot loader. Same RTL family as GD02/GD03.

What is different from the siblings:
- **Standard cells: `gf180mcu_fd_sc_mcu9t5v0` (9-track, 5 V)** instead of 7t, selected in `librelane/slots/slot_1x0p5.yaml` (commit "feat: Use 9t cells"). Release netlist: 139,690 9t5v0 cells.
- **DFT scan chain with Difetto** (Donn's Yosys/LibreLane DFT plugin, `github:donn/difetto/978f710` in `flake.nix`). The custom flow list in `config.yaml` replaces Yosys.Synthesis with `Difetto.Synthesis`, `Difetto.Resynthesis`, `Difetto.ScanReplace`, `Difetto.Cut`, and inserts `Difetto.Chain` before CTS. `librelane/gf180_mapping.json` maps every dffq/dffrnq/dffsnq/dffrsnq (_1/_2/_4) to the matching `sdff*` scan cell. Four extra pads: `tm_pad` (test mode), `sce_pad` (scan enable), `sci_pad` (scan in), all `gf180mcu_fd_io__in_s`, and `sco_pad` (scan out, `bi_24t`, OE tied 1); scan clock is the functional `clk_PAD` (`DFT_TEST_CLOCK_WIRE: clk_PAD2CORE`). These pads sit together on the west edge. In the release netlist there are **3,555 scan flops** (1,434 sdffq + 1,994 sdffrnq + 127 sdffsnq) and no plain flops left; with one sci/sco pair this is, by inference, a single chain of about 3.5k cells. Difetto.BoundaryScan is commented out ("Looks incompatible with top-level I/O macros"). The `chip_core` DFT ports are commented out in `chip_top.sv`; Difetto wires them by name pattern (`DFT_SCAN_IN_PATTERN: sci_pad/Y`, etc.).
- Pads: 51 `bi_24t` (50 bidir + sco), 4 `in_s`, 1 `in_c`, 8 `dvdd`/8 `dvss` (ws_io). No analog.
- Clock 100 ns (10 MHz), `MAX_FANOUT_CONSTRAINT: 15`, `PL_TARGET_DENSITY_PCT: 75`, Yosys strategy `AREA 3`, `deferred_flatten`.
- Comment in config: "Issues seen with SCAN_IN/OUT pins not mapping.." (before `OpenROAD.RCX`), i.e. the authors hit LibreLane/Difetto problems with scan pins.
- Release r1p0 (only release, tag at aa954be, 2025-12-11): gds.gz, tar with lib/sdf/spef/odb/netlists/`metrics.json`. Metrics: 140,457 instances, die 3932 x 2531, stdcell utilisation 61%, **setup violated at slow corner**: max_ss_125C_4v50 WNS -4.26 ns (15 endpoints), nom_ss +0.48 ns, min_ss +4.4 ns; tt +43 to +48 ns; hold WNS +2.8 ps (max_ff_n40C_5v50, essentially zero margin). LVS 0, antenna 0, XOR 0, detailed-route DRC 0 after 25 iterations (an unusually long repair, counts up to 908 errors on iteration 4). Magic/KLayout DRC counts are not present in this metrics.json even though the flow lists those steps (not verified).
- No ATPG patterns, scan test bench, or scan documentation in the repo; `cocotb/` is the single functional bench. Scan was not simulated in the repo as far as I can see.

## Authors and affiliations

| Person | Role | Affiliation | Source |
|---|---|---|---|
| Greg Davill | design, Difetto integration (85 commits) | not stated (GitHub: Australia, gregdavill.com) | git shortlog, `gh api users/gregdavill` |
| Leo Moser | template author (74 commits) | not stated in repo | AUTHORS.md |
| Tim Ansell, TrevorPeyton | 1 commit each | not stated | git shortlog |
| Donn (difetto author) | DFT plugin used | not stated in repo | flake.nix input `github:donn/difetto` |

## Value for GF180MCU characterisation and PDK development

### Verdict: Medium
Not built as a test chip, but it is a 140k-cell 9-track 5 V design with a full scan chain reachable from four pads. A scan chain gives direct controllability and observability of ~3.5k flops (sdffq/sdffrnq/sdffsnq cells), which makes it the most useful of the Racquet set for yield and cell-level fault data and for checking the 9t library in silicon. It stops short of High because no ATPG vector set or fault model ships in the repo and there is no analog or device-level structure.

### Test structures and measurable circuits
| Structure | Exercises | Access | Where |
|---|---|---|---|
| Scan chain, ~3,555 scan flops | flop and scan-mux function of gf180mcu_fd_sc_mcu9t5v0 sdffq/sdffrnq/sdffsnq; stuck-at/transition fault data on 140k cells if patterns are generated; shift speed gives scan-path hold/setup | pads tm_PAD, sce_PAD, sci_PAD, sco_PAD, clk_PAD | `librelane/config.yaml` (DFT_*), `librelane/gf180_mapping.json`, `src/chip_top.sv` |
| 6 x sram512x8m8wm1 | foundry SRAM at 5 V (functional) | cores / SPI loader | `librelane/config.yaml` |
| 9-track vs 7-track comparison | 9t5v0 timing/power vs the 7t5v0 siblings GD02/GD03 on the same RTL | pads | compare with GD02/GD03 metrics |

STA/SDF/SPEF for nine corners exist in the release; hold slack at max_ff is only 2.8 ps and slow-corner setup is -4.3 ns, so Fmax and hold behaviour vs temperature/voltage would test those margins.

### Candidate PDK additions
- A reusable scan-cell mapping for the 9t5v0 library (`gf180_mapping.json`: dff -> sdff for 11 cell variants); a similar file for 7t5v0 is not in the repo.
- Documented flow gap: Difetto boundary scan incompatible with top-level IO macros; scan pins not mapping (config comments).
- DRC repair difficulty on the 9t library shows in the route DRC iteration history (not a documented PDK bug).

### What would be needed to use it
Packaged part and a tester able to drive a 3.5k-bit chain at the 10 MHz clock; the scan-in/scan-out order (chain order) and ATPG patterns are not in the repo (would have to be regenerated from the netlist with Difetto/quaigh, or reconstructed from the release `pnl` netlist); need to hold tm_PAD high and sce_PAD for shift/capture. Test-mode behaviour of the SRAM macros (they are not scannable) and of the reset/clock path in test mode is not documented.

## Run 1 versus run 2

- The same repository at the same HEAD (a64a899) was cloned for ws-run1 and ws-run2. A `diff -r` of the two `repo/` trees shows no difference outside `.git/` metadata (fetch timestamps). The releases (`gf180mcu-racquet-1x0.5-r1.0.gds.gz` 22,140,152 bytes and `.tar.gz` 221,842,753 bytes) are byte-identical in size; `releases.json` is identical.
- project.json differs only in the layout reference: run 1 `GD04/chip_top.gds`, sha256 51b9dd5629d2..., run 2 `GD04/chip_top.oas`, sha256 3fa8774ab2004..., and a differently formatted description (line breaks). So the run 2 submission is the same design resubmitted as OASIS; the repo cannot show whether any layout change was made. Neither platform hash equals the release GDS hash (0552087f...).
- The only commit after the release tag is a64a899 (2026-04-05, "update difetto plugin in flake.nix": flake.nix/flake.lock only, no RTL/config change), so it does not distinguish the runs.

## Notes and caveats

- Silicon has two nominally identical submissions: a comparison of run 1 versus run 2 dies would test run-to-run repeatability of the same layout, if the layouts really are the same (inferred; cannot be checked here without the submitted GDS/OAS).
- README is the untouched template; the platform description is the only prose.
- Setup is violated by 4.26 ns at max_ss_125C_4v50 in the shipped release.

# SCML: ML-Audio SC (ws-run2)

| | |
|---|---|
| Repository | https://github.com/kjconway5/ML-Audio @ 94e7733 (main, last commit 2026-08-07) |
| Slot | 1x1 |
| Top cell | chip_top |
| Licence in repo | Apache-2.0 |
| README | OK (1630 words, about 1330 own) |

## What the repo actually contains
A keyword-spotting pipeline: 1.003 MHz PDM, 5-stage CIC, 33-tap compensation FIR, 256-point STFFT (modified R2FFT), log-mel filterbank (PULP arithmetic IP), spectral VAD, int8 depthwise-separable CNN with a shared MAC array, requant, boot/flash loader over UART, trained in `src/ml/Pipeline` (PyTorch; models and hex weights in `src/ml/models`; Speech Commands wavs checked in). Flow: LibreLane + slang, **3.3 V** (gf180mcu_as_sc_mcu7t3v3 SCL, gf180mcu_ocd_io pads), 16 MHz (period 62.5 ns), PL density 42 %, corners tt_3v30 and ff_n40C_3v60 (ss_125C_3v00 only for SRAM libs). **38 SRAM macros** in `macros_3v3.yaml` (gf180mcu_ocd_ip_sram: 13 x 256x8, 2 x 512x8, 23 x 1024x8, about 28 KB); SRAM repo cloned by `make clone-pdk` from RTimothyEdwards/gf180mcu_ocd_ip_sram, plus `install-3v3-scl-hotfix`. 31 DFT/debug bidir pads (bidir[39:9]) and pad assignments for UART, KWS done/class, VAD drop and test-mode pins. Extensive cocotb tests (`cocotb/chip_core_tb.py`, module tests, GL+SDF wrapper `cocotb/sim/chip_top_sdf_wrapper.sv`). No `final/` or signoff reports in the repo; the 213 MB `chip_top.gds` is a release asset (`final-gds`). The commit log mentions clean LVS/manufacturability, "some slew violations remaining on 3.0v corner" and hold fixes.

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| Aydan Olaez | physical flow, timing, LVS | ucsc.edu email (hint only) | git |
| Jose Peralta, Diego Nocera, Michael Aguero | RTL, verification, docs | ucsc.edu emails (hint only) | git |
| Kye Conway (kjconway5) | repo owner | UC Santa Cruz (GitHub bio: studying Computer Engineering) | `gh api` |
| course | README cites "UCSC ECE 153/250 Digital Signal Processing" (H. Ye, 2026) in FIR/STFFT READMEs; no course for the project itself is stated | | src/rtl/FIR/README.md, src/rtl/STFFT/README.md |

## Value for GF180MCU characterisation and PDK development
### Verdict: Low
Large synthesised digital design with 38 SRAM macros of three sizes on the 3.3 V library; useful as an SRAM/SCL integration case and yield point, but no test structures.
### Test structures and measurable circuits
Nothing dedicated. The 31 debug pads expose internal state, and the design uses three SRAM sizes at 3.3 V; no simulation result in the repo (beyond functional sim logs in `src/ml/models/*/sim-core-results.txt`) is a timing reference.
### Candidate PDK additions
Documented PDK problems: `cocotb/sim/gf180mcu_as_sc_mcu7t3v3_missing_cells.v` says the shipped Verilog model lacks ao211_2, aoi211_2, oai211_2, xor2_2; `install-3v3-scl-hotfix` copies libs from AvalonSemiconductors/gf180mcu_as_sc_mcu7t3v3 over the PDK; commit message "fixed incorrect timing corners for 1024 srams"; GL-sim stubs, slew/max-cap violations at IO pads and SRAM inputs; `scripts/gen_specify_blocks.py` and `sdf_icarus_fixer.py` for SDF sim.
### What would be needed to use it
Packaged test with a UART boot of weights and PDM microphone or WAV playback; no bring-up plan in the repo.
## Notes and caveats
No signoff data in the repo; the release GDS was not opened. Submodule list (`.gitmodules`) is empty at HEAD.

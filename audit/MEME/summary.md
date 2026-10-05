# MEME: Artwork Meme Chip (ws-run2)

| | |
|---|---|
| Repository | https://github.com/anfroholic/meme_chip @ c11dda5 (main, last commit 2026-07-14) |
| Slot | 1x0p5 |
| Top cell | chip_top |
| Licence in repo | MIT (LICENSE; no SPDX headers) |
| README | OK (251 words), but it does not mention the PUF/resistor structures in the GDS |

## What the repo actually contains
Artifacts only, no source: `chip_top_submission.oas` (1.1 MB), `gds/meme.gds.gz` (20 MB; the README names `gds/chip_top.gds(.gz)`, which do not exist), `render/chip_top.png`, `precheck_metrics.json` (klayout DRC, antenna, density, zero-area and magic DRC all 0). README says the generator code is "coming soon". Two commits, one author.

I parsed the GDS with a hand-written record parser (shape counts and areas per cell and layer; layer meanings are from the GF180MCU GDS map and partly inferred; dbu assumed 1 nm, which gave sensible die sizes):
- **Artwork:** a Doge meme with captions ("much wow", "so chips", "such custom", "very silicon", "how value", "many manufacture"). Cell `meme` sits at (571, 532) um with a 4.185 mm^2 boundary and the same bitmap on **Poly2 (30/0, 355 polygons, 1.66 mm^2) and Metal1 to Metal5 (34, 36, 42, 46, 81; each about 94,400 polygons, about 1.65 mm^2, about 39 % of the artwork boundary)**. No COMP, so the poly is field poly. Stock fill cells (METAL1..5_FILL, POLY2_FILL, COMP_FILL) are present; precheck density gave 0 errors, so this is a density/DRC data point for a pixel-art pattern on poly and every metal.
- **Undocumented test structure:** `meme_puf_bank2` is a 12.3 x 8.7 um cell with four 11.0 x 0.8 um Poly2 strips, each with a Pplus cover, a 8.2 x 1.4 um layer-49 block over the body (SAB, inferred), contacts at both ends and M1 pads. Labels in the cell: `HI`, `LO`, `t1`. That is an unsilicided p+ poly resistor (rpolyp-like, inferred). Right ends of strips 2 and 3 are joined by M1. `meme_puf_cluster` (8 banks via SREF) is instanced 2 times at the left edge (x about 680 to 760 um); `meme_puf_cluster_e` (8 banks flattened) 4 times at the right edge (x about 3100 to 3200 um): 48 banks, about 192 resistors. `puf_routes` (M1 to M3 and M5) wires them; `puf_blocker` (129 x 48 um, 6 instances) is marker-only (probably a fill exclusion, inferred).
- Pads: **50 `gf180mcu_fd_io__asig_5p0` analog pads (analog_PAD[0..49])**, 4 `bi_24t` bidir, `in_c` (clk_PAD) and `in_s` (rst_n_PAD). A small 5 V digital block (gf180mcu_fd_sc_mcu7t5v0: 26 dffq_1, nand/nor/aoi, 89 buf_1) sits near (870 to 960, 475 to 515) um, probably bank select/readout (inferred, no netlist seen).
- The wafer.space ID IPs (qrcode_id, shuttle_id, project_id, marker) are present.

## Authors and affiliations
| Person | Role | Affiliation | Source |
|---|---|---|---|
| Andrew Wingate (anfroholic) | sole committer | Evezor, Chicago (GitHub profile) | `git shortlog`, `gh api users/anfroholic` |

## Value for GF180MCU characterisation and PDK development
### Verdict: Medium
Built as artwork, but the GDS carries about 192 identical drawn p+ poly resistors on 50 analog pads. That is a process-variation vehicle, undocumented; the resistor interpretation is inferred from layout alone.
### Test structures and measurable circuits
| Structure | What it exercises | Access | Where |
|---|---|---|---|
| `meme_puf_bank2` x 48 (4 poly resistors each) | p+ poly sheet resistance, within-bank and within-die mismatch, CD/etch variation | 50 `asig_5p0` pads (analog_PAD[0..49]); labels HI/LO/t1 | `gds/meme.gds.gz`, cells `meme_puf_cluster*`, `puf_routes` |
| Pixel-art on Poly2, M1 to M5, about 39 % coverage | density and DRC behaviour on irregular small features | none (layout/yield) | cell `meme` |
No simulation results, netlist, schematic or test plan in the repo.
### Candidate PDK additions
Nothing found.
### What would be needed to use it
Probing of the analog pads with an SMU or ADC; pad-to-resistor-tap mapping (not in repo, generator unpublished, ask the author); the function of the digital select logic. Compare against the PDK rpolyp model.
## Notes and caveats
README does not mention the PUF/resistors; file names in the README do not match the repo; the submitted OAS (platform sha 01cef474...) was not compared with the GDS.

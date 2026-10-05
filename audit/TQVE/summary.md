# TQVE: TinyQV - RISC-V SoC with experimental pad setup (ws-run2)

| | |
|---|---|
| Repository | none listed on platform.wafer.space |
| Slot | 0p5x0p5 |
| Top cell | chip_top |
| Licence in repo | n/a |
| README | n/a |

## What the repo actually contains

No repository was listed for this project, so nothing was cloned and there is nothing to audit. The only first-hand information is the platform record in `project.json`. Platform description: "This version of TinyQV uses the new 3v3 standard cell library, 3v3 SRAM macros and a single line of pads to allow more area with fewer pins.  The extra space is used for 9.5kB of scratch RAM.  It also has a USB CDC peripheral which should allow serial comms without an external UART.".

The manufactured layout is in the public reticle (`ws-run2`, layout `TQVE/chip_top.oas`, SHA256 `67b553d085bad20db1898fc5458e8875a7f82d59a7b519e3bcb8e71c247302e5`), so the design can still be inspected at layout level even without sources.

## Authors and affiliations

Not stated in the manifest. The submitter's identity is held on platform.wafer.space.

## Value for GF180MCU characterisation and PDK development

### Verdict: Unknown (no sources)

## Notes and caveats

This is a TinyQV variant by Michael Bell (description: new 3.3 V standard cell library, 3.3 V SRAM macros, a single line of pads, 9.5 kB of scratch RAM, USB CDC peripheral). Its sibling TQVD is `MichaelBell/ws02-tinyQV`, which is cloned at `../TQVD/repo`; that repo's branches are `main`, `dac` and `template` and its releases v1.0 to v1.4 do not mention the single-row pad variant, so TQVE's source is either unpublished or in a repository that was not listed. See `../TQVD/summary.md` for the closely related design.

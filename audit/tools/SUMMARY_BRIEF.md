# Brief: write `summary.md` for a wafer.space shuttle project

You are analysing chip-design repositories that were manufactured on the
wafer.space GF180MCU shuttle runs (run 1 = G801, run 2 = G802). The reader is
Tim Ansell, who runs wafer.space and maintains the open GF180MCU PDK work. He
wants to know, for every project, what is actually in the repo, who made it,
and above all whether the silicon contains anything that could be measured to
characterise the GF180MCU process, check the PDK's simulation models, or be
upstreamed into the PDK as a new feature.

## Where things are

Each project lives in `runs/<run>/<CODE>/` (`runs/` is the parent of this `tools/` directory):

- `project.json`: what the submitter declared on the platform (name, slot size,
  description, repository URL, top cell, layout hash).
- `repo/`: full clone, submodules initialised. Read-only for you: do not
  modify, build, or run anything inside it.
- `releases/`, `releases.json`: GitHub/GitLab release assets, if any.
- `clone_status.json`: HEAD commit, branch, submodules.
- `runs/audit.json` has the LICENSE/README audit
  record for each project (match on `run` + `code`).

Write exactly one file per project you are assigned:
`runs/<run>/<CODE>/summary.md`. Write nothing else.

## How to investigate

Read the README and docs, then verify against the actual contents: the
directory tree, RTL/schematic/layout sources (`.v`, `.sv`, `.sch`, `.sym`,
`.spice`, `.mag`, `.gds`, `.oas`, xschem/klayout/magic files), LibreLane or
other flow configs, pad/pin lists, testbenches, and `git log`. A README is a
claim; the sources are the evidence. Where they disagree, say so.

Large binary layouts cannot be read directly; use file names, sizes, cell names
(`strings` on a GDS is fine), netlists and schematics instead.

For authors use `git shortlog -sne --all`, copyright headers, README/docs
author lists, and paper/thesis references. For a GitHub login you may run
`gh api users/<login>` (fields: name, company, bio, location, blog) and
`gh api orgs/<org>`. State where each affiliation came from. If an affiliation
is not stated anywhere, write "not stated" rather than inferring one from an
email domain alone (an email domain may be mentioned as a hint, labelled as
such). Do not list private email addresses in full; names and GitHub logins
are enough.

## Required structure of `summary.md`

```
# <CODE>: <project name> (<run>)

| | |
|---|---|
| Repository | <url> @ <short HEAD> (<branch>, last commit <date>) |
| Slot | <slot size> |
| Top cell | <top> |
| Licence in repo | <from audit.json / what you see> |
| README | <audit verdict, one phrase> |

## What the repo actually contains
## Authors and affiliations
## Value for GF180MCU characterisation and PDK development
### Verdict: <High | Medium | Low | None>
### Test structures and measurable circuits
### Candidate PDK additions
### What would be needed to use it
## Notes and caveats
```

Guidance per section:

- **What the repo actually contains.** What the chip is and does, how it is
  built (flow, standard-cell library and voltage, SRAM/IO/analog macros used,
  with names), what is in each major directory, what is complete versus stub
  or unused, whether final layouts and verification results (DRC/LVS/timing
  reports, test results, silicon bring-up data) are present. For multi-project
  dies, list every sub-design with one line each.
- **Authors and affiliations.** A table: person or organisation, role or
  contribution, affiliation, source of that information.
- **Verdict.** `High`: purpose-built test structures or analog/device-level
  circuits with probe or pad access (device arrays, ring oscillators, SRAM or
  memory test chips, passives, ESD/leakage structures, references, PLLs, ADCs,
  custom cells). `Medium`: not built for characterisation but contains
  something measurable or reusable (a new cell library or macro used in
  anger, an oscillator, a DAC, timing-critical digital with known corners,
  unusual layers or devices). `Low`: ordinary synthesised digital on stock
  cells, useful only as a yield/functional data point. `None`: artwork or
  nothing measurable. Give one or two sentences of reasoning.
- **Test structures and measurable circuits.** A table where there is anything
  to list: structure, what device or model parameter it exercises (for example
  nfet_03v3 Vth/leakage, MIM capacitance, poly resistor sheet resistance, IO
  cell drive strength, standard-cell delay, SRAM bit-cell margins), how it is
  accessed (pad names, probe pads, on-chip mux, scan), and where it is in the
  repo (paths). Say which PDK devices and which voltage domain are used. Note
  explicitly whether simulation results exist in the repo that silicon could
  be compared against.
- **Candidate PDK additions.** New standard cells or cell libraries, IO cells,
  SRAM/ROM/eFuse/OTP macros, floating-gate or other non-standard devices,
  parameterised cells, DRC/LVS deck fixes or waivers, model changes, EM
  simulation flows, or anything the project had to work around in the PDK.
  Include bugs or limitations of the PDK that the authors documented.
- **What would be needed to use it.** Bare-die probing versus packaged test,
  required equipment, missing documentation, missing test plans.
- **Notes and caveats.** Anything you could not verify, discrepancies between
  the platform description and the repo, stale submodules, missing sources.

Write plainly and specifically: name files, cells, devices and numbers. Do not
pad sections; if a section has nothing, say "Nothing found" in one line. Mark
anything you inferred rather than read as inferred.

## What to send back

Your final message is read by the coordinating agent, not by Tim. For each
project return one block:

```
<run>/<CODE> | verdict: <High|Medium|Low|None>
what: <one sentence>
authors: <names / orgs, affiliation>
characterisation: <one or two sentences naming the specific structures, or "none">
pdk-additions: <one sentence or "none">
flags: <discrepancies, missing things, or "none">
```

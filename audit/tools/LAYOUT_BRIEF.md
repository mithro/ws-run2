# Brief: update a project summary from the taped-out layout

Each project on wafer.space GF180MCU run 1 (reticle G801) and run 2 (G802) has a
`summary.md` that was written from the project's git repository alone. Your job
is to check and extend it against the layout that was actually manufactured, and
to add renders of the parts of the layout the summary talks about.

The summaries are read by people deciding which dies are worth measuring to
characterise GF180MCU and compare against the simulation models, and what could
be added to the PDK. They will be published on GitHub.

## Where things are

Workspace: the `runs/` directory (the parent of this `tools/` directory); paths below are relative
to it. For a project `<run>/<CODE>`:

| Path | What |
|---|---|
| `<run>/<CODE>/summary.md` | the summary you are updating (edit it in place) |
| `<run>/<CODE>/layout/<CODE>.oas` | the design exactly as placed on the reticle (from the foundry-bound reticle file, including wafer.space's dummy fill, seal ring and ID marks) |
| `<run>/<CODE>/layout.json` | measurements of that layout: size, standard cells by library, SRAM macros, IO cells, layers, block tree with placement boxes, labels |
| `<run>/<CODE>/repo/` | full clone of the project's repository (read only; other branches are `origin/...`) |
| `<run>/<CODE>/releases/` | release assets, if any (often the submitted GDS) |
| `<run>/<CODE>/project.json` | manifest row: name, slot size, description, top cell |
| `<run>/<CODE>/images/` | put your renders here |

Projects with no repository (their summary says "Unknown (no sources)") have only
the layout. For those, write the summary from the layout: it is now the only
evidence, and usually enough to say what is on the die.

## Tools

**Always run KLayout code through the wrapper `runs/tools/kl`**
(use it exactly where you would write `python`: `tools/kl tools/layout_query.py ...`,
`tools/kl my_script.py`). It runs the workspace's Python (KLayout module, Pillow,
numpy) inside a memory-limited cgroup: 16 GB per process, 128 GB across all layout
jobs on the machine. Never call `.venv/bin/python`, `klayout`, `magic` or any other
layout tool directly, and do not raise the limit. If a command exits with code 137
it hit the limit: do the operation on a smaller region (`--box`) or per cell
instead of flattening the whole die. Read each tool's `--help` first.

- `tools/layout_query.py <oas> tree|find|layers|labels|probe|overlap` - hierarchy,
  where a cell is placed, layer usage and merged area in a region, text labels
  (pad names), what is at a point, and overlap of two layers (for checks such as
  "are these gates inside Dualgate?").
- `tools/layout_render.py <oas> --out images/x.webp [--box ...] [--style ...] [--mark ...] [--title ...]` -
  renders a region. Styles: `full`, `devices`, `routing`, `power` for overviews;
  `detail` and `analog` for close-ups of transistors and passives.
- For anything else write a short script against `klayout.db` (import
  `tools/layout_common.py` for helpers). The per-project OAS loads in seconds;
  do not load the full reticle. `klayout.db.LayoutToNetlist` or plain `Region`
  booleans across the metal and via layers can trace whether two shapes are
  connected when that question matters (for example: does this pad reach that
  block). GF180MCU stack: COMP 22/0, Poly2 30/0, Contact 33/0, Metal1 34/0,
  Via1 35/0, Metal2 36/0, Via2 38/0, Metal3 42/0, Via3 40/0, Metal4 46/0,
  Via4 41/0, Metal5 81/0, Via5 82/0, MetalTop 53/0, Pad 37/0. Thick oxide is
  Dualgate 55/0; 5 V/6 V transistors also carry V5_XTOR 112/1. Other layer names
  are in `layout.json` and `tools/layout_common.py:layer_names()`.

Coordinates are micrometres in the design's top cell, origin at the lower-left
corner of the die.

Shell rules: never use `2>/dev/null`, and never pipe a command into `grep`,
`head` or `tail`; redirect output to a file in your scratch directory and read
that. Do not modify anything under `repo/`, and do not write outside the
project directories you were given.

## What to do for each project

1. Read the existing `summary.md`, `project.json` and `layout.json`.
2. Look at the layout: hierarchy, blocks, pads and labels. Render an overview and
   look at it (use the Read tool on the image) so that you describe what is there
   and not what you expect.
3. **Check the summary's claims against the layout.** In particular:
   - Is the taped-out design the one the repository describes? Compare top-level
     blocks, macro counts, standard cell library, IO cell types and pad count
     with the repository's sources, config and any GDS in the repo or releases.
     If the repo has a GDS, compare its cell list and counts with the taped-out
     one and say whether they agree (wafer.space adds fill, seal ring and ID
     cells, and renames cells with `$n` suffixes; that is not a difference).
   - Every statement in the summary marked inferred, unverified, "needs
     checking", or listed under caveats: settle it from the layout if it can be
     settled, and rewrite the statement to say what the layout shows.
   - Every test structure or measurable circuit the summary lists: find it in the
     layout, give its cell name, position and size, and which pads it reaches if
     you can establish that. If it is not on the die, say so.
   - Devices actually used: which transistor flavours (3.3 V thin oxide, 5 V/6 V
     Dualgate, native, LDMOS), resistors, MIM capacitors, diodes, BJTs, eFuses,
     custom (non-library) cells. Give counts or dimensions when they matter for
     characterisation.
4. Look for things worth characterising that the summary missed because they
   are not obvious from the repository.
5. Make renders (see below) and embed them.
6. Edit `summary.md`.
7. Reply with the hand-back described at the end.

Do the analysis yourself with the tools; do not spawn further agents.

## Changes to make in summary.md

Edit the existing file directly with the Edit tool (this file is the deliverable
you were asked for; hand-back text alone is not enough). Keep its structure and
the exact heading `### Verdict: High|Medium|Low|None` (one word). Then:

- Add a row `| Taped-out layout | <reticle cell>, <W x H> um, <n> placement(s) on the G80x reticle |`
  to the table at the top.
- Add a section `## Taped-out layout` directly after `## What the repo actually contains`
  with:
  - a short table of measured facts (die size, pads and IO cell types, standard
    cell library and logic cell count, SRAM macros, notable custom blocks);
  - `### Does it match the repository?` - what you compared and the result;
  - the overview render and the close-ups, each with a one-sentence caption that
    says what the reader is looking at and where it is (coordinates);
  - for dies with test structures: a table locating each one (cell, position,
    size, device details measured from the layout, pads if established).
- Revise the rest of the summary wherever the layout confirms, corrects or
  contradicts it: the test-structure list, candidate PDK additions, "what would
  be needed to use it", notes and caveats, and the verdict if the layout changes
  it. Remove "inferred"/"unverified" wording from anything you have now checked,
  and keep it on anything you could not check, saying what would settle it.
- For a no-repository project, replace the placeholder text with a real summary
  built from the layout, keeping the same section headings. Authors stay "not
  stated" unless the layout carries names (text or artwork on the die counts;
  say that is the source).

Write plainly and specifically. State what you measured and how sure it is;
"geometry suggests" and "extracted connectivity shows" are different levels of
evidence, so say which. Do not pad: a plain digital design on stock cells needs
a short section (facts table, match check, overview render, perhaps one
close-up of anything unusual), not a long one.

## Renders

- 2 to 4 images for a plain digital design; up to about 10 for a die full of
  test structures, where each referenced structure should be visible in at
  least one close-up.
- Always include `images/overview.webp` (whole die, style `full`), with `--mark`
  boxes labelling the main blocks or test structures.
- WebP, width 1200 to 1600 px, aim for under 400 kB each (check the size the
  tool prints; reduce `--width` if needed).
- Look at each image before you embed it. If it does not show what the caption
  says, change the box or style.
- Embed with relative paths: `![caption](images/name.webp)`.

## Hand-back

Reply with, for each project you were given:

1. One line, tab-separated, no line breaks inside fields, in this exact field order:
   `<run>/<CODE>` TAB verdict TAB what it is TAB authors TAB test structures / measurable circuits TAB candidate PDK additions TAB caveats.
   Start from the project's existing line in `runs/digests.tsv`
   (if it has one) and revise it to match the updated summary. Put the line in a fenced code block.
2. Up to five bullets: what the layout confirmed, corrected or added, and
   anything you could not settle.
3. The list of image files you wrote.

### Recording the index line

Also append each project's tab-separated line (item 1 above) to
`runs/digests_layout.tsv` yourself, with a quoted
here-document (`cat >> ... <<'EOF'`), one line per project, real tab characters
between the seven fields. This is the one file outside your project directories
you may write to. Having done that, keep the hand-back short: the bullets
(item 2) and the image list (item 3) only, at most about 15 lines per project.

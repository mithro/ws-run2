#!/usr/bin/env python3
"""Split a run's reticle into one layout per public project and measure each.

For every design on the reticle whose code is in the run's manifest this writes

    runs/<run>/<CODE>/layout/<CODE>.oas   the design exactly as placed on the reticle
    runs/<run>/<CODE>/layout.json         measurements of that layout

Usage: layout_extract.py <run> [CODE ...]
"""
import json
import sys
from collections import Counter

import klayout.db as kdb

from layout_common import (RETICLES, RUNS, classify, flat_counts, hier_shape_counts, is_fill_cell, is_via_cell, layer_names,
                           load, um_box)

SKIP_PREFIXES = ("RETICLE_FILL", "TEXT")
MAX_TREE_NODES = 250
MAX_LABELS = 400


def block_tree(layout, top):
    """Non-library cells below the top cell, breadth first, with where they are placed.

    Coordinates are micrometres in the top cell's frame. Standard cells, SRAM
    macros and IO cells are leaves and are summarised separately.
    """
    nodes = []
    seen = set()
    queue = [(top, kdb.DCplxTrans(), 0, top.name)]
    while queue and len(nodes) < MAX_TREE_NODES:
        cell, trans, depth, path = queue.pop(0)
        children = Counter()
        first = {}
        for inst in cell.each_inst():
            child = inst.cell
            if (classify(child.name) and classify(child.name)[0] == "std") or is_fill_cell(child.name) \
                    or is_via_cell(child.name):
                continue
            children[child.cell_index()] += inst.cell_inst.size()
            first.setdefault(child.cell_index(), inst)
        for ci, count in sorted(children.items(), key=lambda kv: -layout.cell(kv[0]).bbox().area()):
            child = layout.cell(ci)
            inst = first[ci]
            child_trans = trans * inst.dcplx_trans
            box = child.dbbox().transformed(child_trans)
            kind = classify(child.name)
            nodes.append({"cell": child.name, "parent": cell.name, "depth": depth + 1, "count_in_parent": count,
                          "size_um": [round(child.dbbox().width(), 2), round(child.dbbox().height(), 2)],
                          "first_placement_box_um": um_box(box),
                          "kind": kind[0] if kind else "block",
                          "child_cells": child.child_cells()})
            if kind is None and ci not in seen and child.child_cells() and depth + 1 < 4:
                seen.add(ci)
                queue.append((child, child_trans, depth + 1, path + "/" + child.name))
            if len(nodes) >= MAX_TREE_NODES:
                break
    return nodes


def labels(layout, top, names):
    """Distinct text labels in the top cell and one level down, in top-cell coordinates.

    Labels inside library cells (the pad cells' internal net names) are left out.
    """
    out = []
    seen = set()
    for li in layout.layer_indexes():
        info = layout.get_info(li)
        it = kdb.RecursiveShapeIterator(layout, top, li)
        it.max_depth = 1
        it.shape_flags = kdb.Shapes.STexts
        while not it.at_end():
            text = it.shape().text.transformed(it.trans())
            if classify(it.cell().name) or (text.string, info.layer) in seen:
                it.next()
                continue
            seen.add((text.string, info.layer))
            out.append({"text": text.string, "layer": "%d/%d" % (info.layer, info.datatype),
                        "layer_name": names.get((info.layer, info.datatype), ""),
                        "xy_um": [round(text.x * layout.dbu, 2), round(text.y * layout.dbu, 2)]})
            it.next()
            if len(out) >= MAX_LABELS:
                return out, True
    return out, False


def measure(layout, cell, placements, names):
    dbu = layout.dbu
    box = cell.dbbox()
    kinds = flat_counts(cell, lambda c: classify(c.name))
    std = Counter()
    std_types = Counter()
    srams = Counter()
    ios = Counter()
    for key, count in kinds.items():
        if key[0] == "std":
            std[(key[1], "fill" if key[3] else "logic")] += count
            if not key[3]:
                std_types[(key[1], key[2])] += count
        elif key[0] == "sram":
            srams[key[1]] += count
        else:
            ios[key[1]] += count

    shape_counts = hier_shape_counts(layout, cell)
    layer_rows = []
    for li, count in shape_counts.items():
        info = layout.get_info(li)
        layer_rows.append({"layer": "%d/%d" % (info.layer, info.datatype),
                           "name": names.get((info.layer, info.datatype), ""), "shapes": count})
    layer_rows.sort(key=lambda r: tuple(int(x) for x in r["layer"].split("/")))

    # Every cell below the design, by flattened placement count, libraries excluded.
    all_cells = flat_counts_all(cell)
    other = [(layout.cell(ci), n) for ci, n in all_cells.items()
             if classify(layout.cell(ci).name) is None and not is_fill_cell(layout.cell(ci).name)
             and not is_via_cell(layout.cell(ci).name)]
    fill = sum(n for ci, n in all_cells.items() if is_fill_cell(layout.cell(ci).name))
    other.sort(key=lambda kv: -kv[1])

    label_rows, truncated = labels(layout, cell, names)
    return {
        "reticle_cell": cell.name,
        "size_um": [round(box.width(), 3), round(box.height(), 3)],
        "origin_um": [round(box.left, 3), round(box.bottom, 3)],
        "dbu_um": dbu,
        "placements_on_reticle": placements,
        "distinct_cells": len(all_cells),
        "standard_cells": [{"library": lib, "kind": kind, "placements": n}
                           for (lib, kind), n in sorted(std.items())],
        "standard_cell_types_top40": [{"library": lib, "type": t, "placements": n}
                                      for (lib, t), n in std_types.most_common(40)],
        "sram_macros": [{"macro": m, "placements": n} for m, n in sorted(srams.items())],
        "io_cells": [{"cell": m, "placements": n} for m, n in sorted(ios.items())],
        "fill_and_sealring_placements": fill,
        "other_cells_by_placements_top80": [
            {"cell": c.name, "placements": n, "size_um": [round(c.dbbox().width(), 2), round(c.dbbox().height(), 2)]}
            for c, n in other[:80]],
        "layers": layer_rows,
        "blocks": block_tree(layout, cell),
        "labels": label_rows,
        "labels_truncated": truncated,
    }


def flat_counts_all(cell):
    """Flattened placement count of every cell below `cell` (the cell itself excluded)."""
    totals = Counter()
    cache = {}

    def walk(c):
        ci = c.cell_index()
        if ci in cache:
            return cache[ci]
        counts = Counter()
        for inst in c.each_inst():
            n = inst.cell_inst.size()
            counts[inst.cell.cell_index()] += n
            for k, v in walk(inst.cell).items():
                counts[k] += v * n
        cache[ci] = counts
        return counts

    totals.update(walk(cell))
    return totals


def remeasure(key):
    """Redo layout.json for one project from its already extracted layout."""
    run, code = key.split("/")
    out_dir = RUNS / run / code
    old = json.load((out_dir / "layout.json").open())
    layout = load(out_dir / "layout" / ("%s.oas" % code))
    cell = layout.cell(old["reticle_cell"])
    info = {"run": run, "code": code, **measure(layout, cell, old["placements_on_reticle"], layer_names())}
    (out_dir / "layout.json").write_text(json.dumps(info, indent=1) + "\n")
    return key


def main():
    if sys.argv[1] == "--remeasure":
        import multiprocessing
        keys = sorted(str(p.parent.relative_to(RUNS)) for p in RUNS.glob("ws-run*/*/layout.json"))
        with multiprocessing.Pool(24) as pool:
            for i, key in enumerate(pool.imap_unordered(remeasure, keys), 1):
                print("EVT remeasured %d/%d %s" % (i, len(keys), key), flush=True)
        return
    run = sys.argv[1]
    only = set(sys.argv[2:])
    projects = {p["code"] for p in json.load((RUNS / "projects.json").open()) if p["run"] == run}
    names = layer_names()
    print("loading", RETICLES[run], flush=True)
    layout = load(RETICLES[run])
    top = layout.top_cells()[0]
    dbu = layout.dbu

    slots = {}
    for inst in top.each_inst():
        child = inst.cell
        if child.name.startswith(SKIP_PREFIXES):
            continue
        code = child.name.split("_", 1)[0]
        entry = slots.setdefault(code, {"cell": child, "placements": []})
        if entry["cell"].cell_index() != child.cell_index():
            print("WARNING: %s has more than one reticle cell: %s and %s" % (code, entry["cell"].name, child.name))
        for t in inst.cell_inst.each_trans():
            entry["placements"].append({"x_mm": round(t.disp.x * dbu / 1000, 3), "y_mm": round(t.disp.y * dbu / 1000, 3),
                                        "rotation": str(t).split(" ")[0]})
    print("reticle codes:", " ".join(sorted(slots)))
    print("manifest codes with no reticle cell:", " ".join(sorted(projects - set(slots))) or "none")
    print("reticle codes not in the manifest (private):", " ".join(sorted(set(slots) - projects)) or "none")

    done = 0
    for code in sorted(projects & set(slots)):
        if only and code not in only:
            continue
        cell = slots[code]["cell"]
        out_dir = RUNS / run / code
        (out_dir / "layout").mkdir(parents=True, exist_ok=True)
        info = measure(layout, cell, slots[code]["placements"], names)
        info = {"run": run, "code": code, **info}
        (out_dir / "layout.json").write_text(json.dumps(info, indent=1) + "\n")
        options = kdb.SaveLayoutOptions()
        options.format = "OASIS"
        options.oasis_compression_level = 2
        cell.write(str(out_dir / "layout" / ("%s.oas" % code)), options)
        done += 1
        print("EVT done %d %s %s %.0f x %.0f um, %d distinct cells" % (
            done, code, cell.name, info["size_um"][0], info["size_um"][1], info["distinct_cells"]), flush=True)
    print("EVT finished", run, done)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ask questions of a layout without opening a GUI.

    layout_query.py <layout.oas> tree   [--cell NAME] [--depth N] [--all]
        Cells placed inside a cell: count, size, kind. Standard cells, router vias and dummy fill are hidden unless --all.
    layout_query.py <layout.oas> find   REGEX [--cell NAME] [--limit N]
        Where cells whose name matches REGEX are placed (boxes in the root cell's coordinates).
    layout_query.py <layout.oas> layers [--cell NAME] [--box x0,y0,x1,y1]
        Shapes and merged area per layer inside a cell or a region of it.
    layout_query.py <layout.oas> labels [REGEX] [--cell NAME] [--box x0,y0,x1,y1] [--depth N]
        Text labels with layer and position.
    layout_query.py <layout.oas> probe  X,Y [--cell NAME]
        Which cells (full hierarchy path) and which layers cover a point.
    layout_query.py <layout.oas> overlap A B [--cell NAME] [--box x0,y0,x1,y1]
        Count and area of the regions where layers A and B (layer/datatype) overlap,
        plus where A is and is not covered by B. Use it for checks such as
        "are these gates (30/0 over 22/0) inside Dualgate (55/0)?".

All coordinates are micrometres in the coordinates of --cell (default: the top cell).
"""
import argparse
import re
from collections import Counter

import klayout.db as kdb

from layout_common import classify, flat_counts, hier_shape_counts, is_fill_cell, is_via_cell, layer_names, load, pick_cell


def dbox(text):
    x0, y0, x1, y1 = (float(v) for v in text.split(","))
    return kdb.DBox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def cmd_tree(layout, cell, args):
    def show(c, depth, indent):
        children = Counter()
        for inst in c.each_inst():
            children[inst.cell.cell_index()] += inst.cell_inst.size()
        rows = sorted(children.items(), key=lambda kv: -layout.cell(kv[0]).bbox().area())
        hidden = Counter()
        for ci, n in rows:
            child = layout.cell(ci)
            kind = classify(child.name)
            if is_fill_cell(child.name) and not args.all:
                hidden["the dummy fill / seal ring"] += n
                continue
            if is_via_cell(child.name) and not args.all:
                hidden["router via cells"] += n
                continue
            if kind and kind[0] == "std" and not args.all:
                hidden[kind[1]] += n
                continue
            b = child.dbbox()
            print("%s%-60s x%-6d %9.2f x %9.2f um  %s" % (indent, child.name, n, b.width(), b.height(),
                                                         kind[0] if kind else "children=%d" % child.child_cells()))
            if depth > 1 and (kind is None):
                show(child, depth - 1, indent + "  ")
        for lib, n in hidden.items():
            print("%s(%d placements from %s not listed)" % (indent, n, lib))
    b = cell.dbbox()
    print("%s  %.2f x %.2f um, box %s" % (cell.name, b.width(), b.height(), b))
    show(cell, args.depth, "  ")


def cmd_find(layout, cell, args):
    pattern = re.compile(args.regex)
    targets = {c.cell_index() for c in layout.each_cell() if pattern.search(c.name)}
    counts = flat_counts(cell, lambda c: c.name if c.cell_index() in targets else None)
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        b = layout.cell(name).dbbox()
        print("%-60s placements=%d size=%.2f x %.2f um" % (name, n, b.width(), b.height()))
    shown = [0]

    def walk(c, trans, path):
        if shown[0] >= args.limit:
            return
        for inst in c.each_inst():
            child = inst.cell
            if child.cell_index() not in reach:
                continue
            for t in inst.cell_inst.each_cplx_trans():
                if shown[0] >= args.limit:
                    return
                dt = trans * kdb.DCplxTrans(t, layout.dbu) if False else trans * kdb.DCplxTrans(
                    t.mag, t.angle, t.is_mirror(), t.disp.x * layout.dbu, t.disp.y * layout.dbu)
                if child.cell_index() in targets:
                    b = child.dbbox().transformed(dt)
                    print("  %s at box %.2f,%.2f,%.2f,%.2f  (%s)" % (child.name, b.left, b.bottom, b.right, b.top,
                                                                    path + "/" + child.name))
                    shown[0] += 1
                else:
                    walk(child, dt, path + "/" + child.name)

    # Only descend into cells that contain a target somewhere below.
    reach = set(targets)
    for ci in targets:
        reach.update(layout.cell(ci).caller_cells())
    walk(cell, kdb.DCplxTrans(), cell.name)
    if shown[0] >= args.limit:
        print("  ... stopped after %d placements (raise --limit)" % args.limit)


def cmd_layers(layout, cell, args):
    names = layer_names()
    if not args.box:
        counts = hier_shape_counts(layout, cell)
        for li in sorted(counts, key=lambda i: (layout.get_info(i).layer, layout.get_info(i).datatype)):
            info = layout.get_info(li)
            print("%4d/%-3d %-22s shapes=%d" % (info.layer, info.datatype, names.get((info.layer, info.datatype), ""),
                                                counts[li]))
        print("(merged areas are only computed with --box)")
        return
    box = dbox(args.box)
    ibox = kdb.Box(box.left / layout.dbu, box.bottom / layout.dbu, box.right / layout.dbu, box.top / layout.dbu)
    for li in sorted(layout.layer_indexes(), key=lambda i: (layout.get_info(i).layer, layout.get_info(i).datatype)):
        region = kdb.Region(kdb.RecursiveShapeIterator(layout, cell, li, ibox))
        if region.is_empty():
            continue
        raw = region.count()
        region &= kdb.Region(ibox)
        region.merge()
        info = layout.get_info(li)
        print("%4d/%-3d %-22s shapes=%-8d merged_polygons=%-7d area=%.2f um2 (%.1f%% of box)" % (
            info.layer, info.datatype, names.get((info.layer, info.datatype), ""), raw, region.count(),
            region.area() * layout.dbu ** 2, 100 * region.area() / ibox.area()))


def cmd_labels(layout, cell, args):
    names = layer_names()
    pattern = re.compile(args.regex) if args.regex else None
    box = dbox(args.box) if args.box else None
    n = 0
    for li in layout.layer_indexes():
        info = layout.get_info(li)
        it = kdb.RecursiveShapeIterator(layout, cell, li)
        it.shape_flags = kdb.Shapes.STexts
        if args.depth is not None:
            it.max_depth = args.depth
        while not it.at_end():
            text = it.shape().text.transformed(it.trans())
            x, y = text.x * layout.dbu, text.y * layout.dbu
            if (pattern is None or pattern.search(text.string)) and (box is None or box.contains(kdb.DPoint(x, y))):
                print("%-40s %4d/%-3d %-14s %.2f,%.2f  in %s" % (text.string, info.layer, info.datatype,
                                                                names.get((info.layer, info.datatype), ""), x, y,
                                                                it.cell().name))
                n += 1
                if n >= args.limit:
                    print("... stopped after %d labels (raise --limit)" % n)
                    return
            it.next()
    print("%d labels" % n)


def cmd_probe(layout, cell, args):
    names = layer_names()
    x, y = (float(v) for v in args.xy.split(","))
    p = kdb.Point(round(x / layout.dbu), round(y / layout.dbu))
    search = kdb.Box(p.x - 1, p.y - 1, p.x + 1, p.y + 1)
    paths = set()
    for li in layout.layer_indexes():
        info = layout.get_info(li)
        it = kdb.RecursiveShapeIterator(layout, cell, li, search)
        hit = False
        while not it.at_end():
            shape = it.shape()
            poly = None
            if shape.is_box() or shape.is_polygon() or shape.is_path() or shape.is_simple_polygon():
                poly = shape.polygon.transformed(it.trans())
            if poly is not None and poly.inside(p):
                hit = True
                paths.add("/".join([cell.name] + [e.inst().cell.name for e in it.path()]))
            it.next()
        if hit:
            print("layer %4d/%-3d %s" % (info.layer, info.datatype, names.get((info.layer, info.datatype), "")))
    for path in sorted(paths):
        print("in", path)


def cmd_overlap(layout, cell, args):
    def region(spec):
        layer, datatype = (int(v) for v in spec.split("/"))
        li = layout.find_layer(kdb.LayerInfo(layer, datatype))
        if li is None or li < 0:
            return kdb.Region()
        if args.box:
            box = dbox(args.box)
            ibox = kdb.Box(box.left / layout.dbu, box.bottom / layout.dbu, box.right / layout.dbu, box.top / layout.dbu)
            r = kdb.Region(kdb.RecursiveShapeIterator(layout, cell, li, ibox)) & kdb.Region(ibox)
        else:
            r = kdb.Region(kdb.RecursiveShapeIterator(layout, cell, li))
        r.merge()
        return r
    a, b = region(args.a), region(args.b)
    k = layout.dbu ** 2
    both, a_only = a & b, a - b
    print("A=%s: %d merged polygons, %.2f um2" % (args.a, a.count(), a.area() * k))
    print("B=%s: %d merged polygons, %.2f um2" % (args.b, b.count(), b.area() * k))
    print("A and B:     %d polygons, %.2f um2" % (both.count(), both.area() * k))
    print("A not in B:  %d polygons, %.2f um2" % (a_only.count(), a_only.area() * k))
    print("A polygons fully inside B: %d; touching B: %d; outside B: %d" % (
        a.inside(b).count(), a.interacting(b).count(), a.not_interacting(b).count()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layout")
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cell")
    p = sub.add_parser("tree", parents=[common])
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--all", action="store_true")
    p = sub.add_parser("find", parents=[common])
    p.add_argument("regex")
    p.add_argument("--limit", type=int, default=40)
    p = sub.add_parser("layers", parents=[common])
    p.add_argument("--box")
    p = sub.add_parser("labels", parents=[common])
    p.add_argument("regex", nargs="?")
    p.add_argument("--box")
    p.add_argument("--depth", type=int)
    p.add_argument("--limit", type=int, default=300)
    p = sub.add_parser("probe", parents=[common])
    p.add_argument("xy")
    p = sub.add_parser("overlap", parents=[common])
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--box")
    args = ap.parse_args()

    layout = load(args.layout)
    cell = pick_cell(layout, args.cell)
    globals()["cmd_" + args.cmd](layout, cell, args)


if __name__ == "__main__":
    main()

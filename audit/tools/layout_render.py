#!/usr/bin/env python3
"""Render part of a layout to an image.

    layout_render.py <layout.oas> --out images/name.webp
        [--cell NAME]            cell to draw (default: the largest top cell)
        [--box x0,y0,x1,y1]      region in micrometres, in that cell's coordinates (default: whole cell)
        [--style STYLE]          full | devices | routing | power | detail | analog | lyp | layer list such as 22/0,30/0,55/0
        [--width PX]             image width in pixels (default 1600; height follows the aspect ratio)
        [--title TEXT]           caption drawn along the top
        [--mark x0,y0,x1,y1[:label]]  outline a region (repeatable)
        [--fill]                 also draw the dummy fill cells (hidden by default)

Every style except `lyp` draws each mask layer as a tinted film with a legend:
  full     all mask layers, for whole-die and block overviews
  devices  nwell, diffusion, poly
  routing  metal 1-3
  power    metal 4, 5, top metal and pad openings
  detail   close-up of transistors: wells, Dualgate (thick oxide), diffusion, poly, contacts, metal 1-2
  analog   like detail plus SAB, resistor, BJT and Schottky markers and the MIM top plate
`lyp` uses the standard GF180MCU KLayout stipples; it is usually harder to read.
A scale bar is always drawn. Dummy fill is hidden unless --fill is given.
"""
import argparse
import io
from pathlib import Path

import klayout.db as kdb
import klayout.lay as lay
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

from layout_common import LYP, is_fill_cell, load, pick_cell

OVERSAMPLING = 3

# GF180MCU mask layers as (label, GDS layers, RGB tint). Dummy fill (datatype 4) is drawn with its layer.
LAYERS = {
    "nwell": ("Nwell", [(21, 0)], (40, 44, 70)),
    "comp": ("Diffusion", [(22, 0), (22, 4)], (60, 190, 90)),
    "poly": ("Polysilicon", [(30, 0), (30, 4)], (235, 70, 70)),
    "metal1": ("Metal 1", [(34, 0), (34, 4)], (60, 120, 255)),
    "metal2": ("Metal 2", [(36, 0), (36, 4)], (200, 80, 230)),
    "metal3": ("Metal 3", [(42, 0), (42, 4)], (50, 210, 220)),
    "metal4": ("Metal 4", [(46, 0), (46, 4)], (240, 200, 60)),
    "metal5": ("Metal 5", [(81, 0), (81, 4)], (245, 140, 50)),
    "metaltop": ("Top metal", [(53, 0), (53, 4)], (230, 230, 235)),
    "pad": ("Pad openings", [(37, 0)], (255, 255, 255)),
    "dnwell": ("Deep Nwell", [(12, 0)], (70, 50, 20)),
    "dualgate": ("Dualgate (thick oxide)", [(55, 0)], (90, 40, 90)),
    "contact": ("Contact", [(33, 0)], (255, 255, 255)),
    "sab": ("SAB (silicide block)", [(49, 0)], (120, 120, 40)),
    "resistor": ("Resistor marker", [(62, 0), (110, 5)], (150, 100, 30)),
    "mim": ("MIM top plate (FuseTop)", [(75, 0)], (255, 120, 180)),
    "schottky": ("Schottky marker", [(241, 0)], (0, 150, 150)),
    "bjt": ("BJT marker", [(118, 5), (127, 5)], (120, 60, 0)),
}
STYLES = {
    "full": ["nwell", "comp", "poly", "metal1", "metal2", "metal3", "metal4", "metal5", "metaltop"],
    "devices": ["nwell", "comp", "poly"],
    "routing": ["metal1", "metal2", "metal3"],
    "power": ["metal4", "metal5", "metaltop", "pad"],
    # Close-ups: transistor-level view with thick-oxide marker and first two metals.
    "detail": ["dnwell", "nwell", "dualgate", "comp", "poly", "contact", "metal1", "metal2"],
    # Passive and special devices: resistors, MIM capacitors, Schottky diodes, BJTs.
    "analog": ["dnwell", "nwell", "dualgate", "sab", "resistor", "bjt", "schottky", "comp", "poly", "metal1",
               "metal2", "mim"],
}
FULL_OPACITY = {"nwell": 0.9, "comp": 0.85, "poly": 0.85, "metal1": 0.6, "metal2": 0.5, "metal3": 0.42,
                "metal4": 0.32, "metal5": 0.26, "metaltop": 0.22}
PALETTE = [(60, 190, 90), (235, 70, 70), (60, 120, 255), (200, 80, 230), (50, 210, 220), (240, 200, 60),
           (245, 140, 50), (230, 230, 235)]


def make_view(layout, cell, show_fill):
    view = lay.LayoutView()
    view.show_layout(layout, False)
    if not show_fill:  # the dummy metal/diffusion/poly fill covers everything and hides the design
        for c in layout.each_cell():
            if is_fill_cell(c.name) and not c.name.lower().startswith("sealring"):
                view.hide_cell(c.cell_index(), 0)
    view.set_config("background-color", "#000000")
    view.set_config("grid-visible", "false")
    view.set_config("text-visible", "false")
    view.set_config("guiding-shape-visible", "false")
    view.active_cellview().cell = cell
    view.max_hier()
    return view


def coverage(view, gds_layers, box, width, height):
    """One greyscale image: the fraction of each pixel covered by the given layers."""
    view.clear_layers()
    for layer, datatype in gds_layers:
        props = lay.LayerProperties()
        props.source = "%d/%d@1" % (layer, datatype)
        props.fill_color = props.frame_color = 0xFFFFFF
        props.dither_pattern = 0
        props.width = 0
        props.visible = True
        props.transparent = False
        view.insert_layer(view.end_layers(), props)
    pixels = view.get_pixels_with_options(width, height, 1, OVERSAMPLING, 1.0, box)
    return Image.open(io.BytesIO(pixels.to_png_data())).convert("L")


def render_films(view, style, box, width, height):
    if style in STYLES:
        stack = [(LAYERS[k][1], LAYERS[k][2], FULL_OPACITY[k] if style == "full" else None, LAYERS[k][0])
                 for k in STYLES[style]]
    else:  # explicit list of layer/datatype pairs
        stack = []
        for i, item in enumerate(style.split(",")):
            layer, datatype = (int(x) for x in item.split("/"))
            stack.append(([(layer, datatype)], PALETTE[i % len(PALETTE)], None, item))
    image = Image.new("RGB", (width, height))
    legend = []
    for gds_layers, colour, opacity, label in stack:
        cov = coverage(view, gds_layers, box, width, height)
        if opacity is not None:
            mask = cov.point(lambda v, o=opacity: int(v * o))
            image = Image.composite(Image.new("RGB", (width, height), colour), image, mask)
        else:
            image = ImageChops.screen(image, ImageOps.colorize(cov, (0, 0, 0), colour))
        legend.append((label, colour))
    return image, legend


def render_lyp(view, box, width, height):
    view.load_layer_props(str(LYP))
    view.add_missing_layers()
    view.set_config("text-visible", "true")
    pixels = view.get_pixels_with_options(width, height, 1, OVERSAMPLING, 1.0, box)
    return Image.open(io.BytesIO(pixels.to_png_data())).convert("RGB"), []


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def nice_length(target_um):
    """Largest 1/2/5 x 10^n length not above the target."""
    best = 1e-3
    for exp in range(-3, 5):
        for mant in (1, 2, 5):
            if mant * 10 ** exp <= target_um:
                best = mant * 10 ** exp
    return best


def annotate(image, box, legend, title, marks):
    width, height = image.size
    scale = width / box.width()  # pixels per um
    draw = ImageDraw.Draw(image, "RGBA")
    f = font(max(13, width // 90))

    for (x0, y0, x1, y1), label in marks:
        px0, px1 = (x0 - box.left) * scale, (x1 - box.left) * scale
        py0, py1 = (box.top - y1) * scale, (box.top - y0) * scale
        draw.rectangle([px0, py0, px1, py1], outline=(255, 255, 0, 255), width=max(2, width // 600))
        if label:
            tw = draw.textlength(label, font=f)
            ty = py0 - f.size - 6 if py0 > f.size + 8 else py1 + 2
            draw.rectangle([px0, ty, px0 + tw + 8, ty + f.size + 4], fill=(0, 0, 0, 200))
            draw.text((px0 + 4, ty + 1), label, fill=(255, 255, 0, 255), font=f)

    bar_um = nice_length(box.width() / 5)
    bar_px = bar_um * scale
    text = "%g um" % bar_um if bar_um < 1000 else "%g mm" % (bar_um / 1000)
    pad = 10
    bw = max(bar_px, draw.textlength(text, font=f)) + 2 * pad
    bh = f.size + 18 + pad
    x, y = width - bw - pad, height - bh - pad
    draw.rectangle([x, y, x + bw, y + bh], fill=(0, 0, 0, 200))
    draw.rectangle([x + pad, y + bh - pad - 6, x + pad + bar_px, y + bh - pad], fill=(255, 255, 255, 255))
    draw.text((x + pad, y + 5), text, fill=(255, 255, 255, 255), font=f)

    if legend:
        lw = max(draw.textlength(lbl, font=f) for lbl, _ in legend) + f.size + 3 * pad
        lh = len(legend) * (f.size + 5) + 2 * pad - 5
        ly = height - lh - pad
        draw.rectangle([pad, ly, pad + lw, ly + lh], fill=(0, 0, 0, 200))
        for i, (lbl, colour) in enumerate(legend):
            ty = ly + pad + i * (f.size + 5)
            draw.rectangle([2 * pad, ty + 1, 2 * pad + f.size - 2, ty + f.size - 1], fill=colour + (255,))
            draw.text((2 * pad + f.size + 6, ty - 1), lbl, fill=(255, 255, 255, 255), font=f)

    if title:
        tw = draw.textlength(title, font=f)
        draw.rectangle([pad, pad, pad + tw + 2 * pad, pad + f.size + 12], fill=(0, 0, 0, 200))
        draw.text((2 * pad, pad + 5), title, fill=(255, 255, 255, 255), font=f)
    return image


def parse_box(text):
    x0, y0, x1, y1 = (float(v) for v in text.split(","))
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layout")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cell")
    ap.add_argument("--box")
    ap.add_argument("--style", default="full")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--title")
    ap.add_argument("--mark", action="append", default=[])
    ap.add_argument("--fill", action="store_true", help="also draw the dummy fill (hidden by default)")
    args = ap.parse_args()

    layout = load(args.layout)
    cell = pick_cell(layout, args.cell)
    box = kdb.DBox(*parse_box(args.box)) if args.box else cell.dbbox()
    if box.width() <= 0 or box.height() <= 0:
        raise SystemExit("empty box")
    width = args.width
    height = max(16, round(width * box.height() / box.width()))
    if height > 2.5 * width:  # tall region: cap the height instead
        height = round(2.5 * width)
        width = max(16, round(height * box.width() / box.height()))

    view = make_view(layout, cell, args.fill)
    if args.style == "lyp":
        image, legend = render_lyp(view, box, width, height)
    else:
        image, legend = render_films(view, args.style, box, width, height)

    marks = []
    for item in args.mark:
        coords, _, label = item.partition(":")
        marks.append((parse_box(coords), label))
    image = annotate(image, box, legend, args.title, marks)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix == ".webp":
        image.save(out, "WEBP", quality=84, method=6)
    else:
        image.save(out)
    print("wrote %s %dx%d px, region %.1f x %.1f um (%.3f um/px), %d bytes" % (
        out, width, height, box.width(), box.height(), box.width() / width, out.stat().st_size))


if __name__ == "__main__":
    main()

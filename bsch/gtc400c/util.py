#!/usr/bin/env python

import argparse, io, os

from .jpeg import thermoblob_extr
from .metadata import metadata_extr
from .fusion import Thermography
from . import colormaps

def get_cmap(name):
    """
    Return the first matching colormap with that name by trying with:

    * bsch.gtc400c.colormaps.get_cmap()
    * matplotlib.cm.get_cmap()

    Raises ValueError if not found.
    """
    try:
        return colormaps.get_cmap(name)
    except ValueError:
        import matplotlib as mpl
        return mpl.cm.get_cmap(name)

def remove_ext(filename, ext=".JPG"):
    if filename.endswith(ext):
        return filename[:-len(ext)]
    return filename

def cli_thermogram():
    from matplotlib import pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    parser = argparse.ArgumentParser()
    parser.add_argument("--cmap", type=get_cmap, metavar="CMAP_NAME", help=f"Colormap to use. By default, the one stored in the JPEG is used. You can choose from the GTC colormaps {', '.join(colormaps.colormaps())}. As an ALTERNATIVE, select one of matplotlib's colormaps: {', '.join(plt.colormaps())}")
    parser.add_argument("--output", help="Output filename. By default, it will be derived from the jpeg_file.")
    parser.add_argument("jpeg_file", type=argparse.FileType("rb"))
    args = parser.parse_args()
    if args.output is None and args.jpeg_file.name:
        args.output = remove_ext(args.jpeg_file.name) + ".thermogram.png"

    t = Thermography(args.jpeg_file.read())

    if args.cmap is None:
        args.cmap = colormaps.get_cmap(t.get("color_map").name)

    fig = plt.figure(figsize=(8, 6), dpi=96)
    ax = plt.gca()
    matrix = t.get_matrix_lst()
    plt.suptitle(os.path.basename(args.jpeg_file.name), size=16)
    plt.title(f"min: {min(map(min, matrix)):.2f}  max: {max(map(max, matrix)):.2f}", size=10)
    im = ax.imshow(matrix, extent=(0, 160, 0, 120), cmap=args.cmap)
    ax_divider = make_axes_locatable(ax)
    cax = ax_divider.append_axes("right", size="4%", pad="2%")
    cbar = fig.colorbar(im, cax=cax)
    plt.tight_layout()
    cbar.set_label(t.unit, labelpad=-1)
    plt.savefig(args.output)
    print(args.output)

def cli_plot():
    from matplotlib import pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument("jpeg_file", type=argparse.FileType("rb"))
    args = parser.parse_args()

    t = Thermography(args.jpeg_file.read())
    cmap = colormaps.get_cmap(t.get("color_map").name)

    plt.imshow(t.get_matrix_lst(), cmap=cmap)
    plt.colorbar()
    plt.show()

def blend_real_and_ir(t: Thermography, scale=3.25, shift=(8, 6), opacity=0.80, sat=0.4, cmap=None):
    """ blend the real and the ir images together """

    from matplotlib import pyplot as plt
    from PIL import Image, ImageEnhance

    if cmap is None:
        # use the one embedded in the JPEG:
        cmap = colormaps.get_cmap(t.get("color_map").name)
    elif type(cmap) == str:
        cmap = get_cmap(cmap)

    matrix = t.get_matrix_lst()

    fig, ax = plt.subplots(figsize=(scale*4, scale*3), dpi=40, frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.imshow(matrix, cmap=cmap)
    fig.patch.set_visible(False)
    #plt.colorbar()

    #thermo = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    # or...
    tmp = io.BytesIO()
    fig.canvas.print_png(tmp)
    tmp.seek(0)
    thermo = Image.open(tmp)

    blend = t.get_real_im().copy()

    if sat != 1.0:
        converter = ImageEnhance.Color(blend)
        blend = converter.enhance(sat)

    ts, rs = thermo.size, blend.size
    offset = (rs[0] - ts[0]) // 2, (rs[1] - ts[1]) // 2
    offset = offset[0] + shift[0], offset[1] + shift[1]

    # remap opacity from range 0.0 = transparent, 1.0 = opaque  to:  0x00 = transparent, 0xff = opaque
    opacity = int(round(opacity * 255))
    thermo.putalpha(opacity)
    blend.putalpha(0xff)
    blend.paste(thermo, offset, thermo)

    return blend

def cli_blend():
    from matplotlib import pyplot as plt
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--scale", type=float, default=3.25, help="Scale the IR image up by this factor.")
    parser.add_argument("--shift", type=lambda x: tuple(int(e) for e in x.split(",")), default=(8, 6), help="Shift the IR image w.r.t. the real image by this amount of pixels.")
    parser.add_argument("--opacity", type=float, default=0.667, help="Opacity of the IR thermography overlay, range: 0.0 - 1.0.")
    parser.add_argument("--sat", type=float, default=0.4, help="Saturation of the real image, range: 0.0 - 1.0.")
    parser.add_argument("--cmap", type=get_cmap, metavar="CMAP_NAME", help=f"Colormap to use. By default, the one stored in the JPEG is used. You can choose from the GTC colormaps {', '.join(colormaps.colormaps())}. As an ALTERNATIVE, select one of matplotlib's colormaps: {', '.join(plt.colormaps())}")
    parser.add_argument("--output", help="Output filename. If None, it will be derived from the jpeg_file.")
    parser.add_argument("jpeg_file", type=argparse.FileType("rb"))
    args = parser.parse_args()
    if not args.output:
        output = remove_ext(args.jpeg_file.name) + ".blend.png"
    t = Thermography(args.jpeg_file.read())
    if args.cmap is None:
        args.cmap = colormaps.get_cmap(t.get("color_map").name)
    blend = blend_real_and_ir(t, scale=args.scale, shift=args.shift, opacity=args.opacity, sat=args.sat, cmap=args.cmap)
    blend.save(output)
    print(output)

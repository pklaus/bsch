#!/usr/bin/env python

import argparse, io

from .jpeg import thermoblob_extr
from .metadata import metadata_extr
from .fusion import Thermography

def remove_ext(filename, ext=".JPG"):
    if filename.endswith(ext):
        return filename[:-len(ext)]
    return filename

def cli_plot():
    from matplotlib import pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument("jpeg_file", type=argparse.FileType("rb"))
    args = parser.parse_args()

    t = Thermography(args.jpeg_file.read())

    plt.imshow(t.get_matrix_lst())
    plt.colorbar()
    plt.show()

def blend_real_and_ir(t: Thermography, scale=3.25, shift=(8, 6), alpha=0.667, sat=0.4, cmap="rainbow"):
    """ blend the real and the ir images together """

    from matplotlib import pyplot as plt
    from PIL import Image, ImageEnhance

    if type(cmap) == str:
        cmap = plt.get_cmap(cmap)

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

    # remap alpha from range 1.0 = opaque, 0.0 = transparent  to:  0xff = opaque, 0x00 = transparent
    alpha = int(round(alpha * 255))
    thermo.putalpha(alpha)
    blend.putalpha(0xff)
    blend.paste(thermo, offset, thermo)

    return blend

def cli_blend():
    from matplotlib import pyplot as plt
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--scale", type=float, default=3.25, help="Scale the IR image up by this factor.")
    parser.add_argument("--shift", type=lambda x: tuple(int(e) for e in x.split(",")), default=(8, 6), help="Shift the IR image w.r.t. the real image by this amount of pixels.")
    parser.add_argument("--alpha", type=float, default=0.667, help="Transparency of the IR thermography overlay, range: 0.0 - 1.0.")
    parser.add_argument("--sat", type=float, default=0.4, help="Saturation of the real image, range: 0.0 - 1.0.")
    parser.add_argument("--cmap", type=plt.get_cmap, default="rainbow", help="Colormap to use. See matplotlib's documentation.")
    parser.add_argument("--output", help="Output filename. If None, it will be derived from the jpeg_file.")
    parser.add_argument("jpeg_file", type=argparse.FileType("rb"))
    args = parser.parse_args()
    if not args.output:
        output = remove_ext(args.jpeg_file.name) + ".blend.png"
    t = Thermography(args.jpeg_file.read())
    blend = blend_real_and_ir(t, scale=args.scale, shift=args.shift, alpha=args.alpha, sat=args.sat, cmap=args.cmap)
    blend.save(output)
    print(output)

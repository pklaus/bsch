#!/usr/bin/env python

import struct
import io
from typing import Union

from .jpeg import thermoblob_extr
from .metadata import metadata_extr


class Thermography:
    def __init__(self, jpeg_data: Union[bytes, str]):
        if type(jpeg_data) == str:
            with open(jpeg_data, "rb") as f:
                jpeg_data = f.read()
        self.jpeg_data = jpeg_data
        self.thermoblob = thermoblob_extr(jpeg_data)
        self.metadata = metadata_extr(self.thermoblob)

    def get(self, key):
        return {f.name: v for f, v in self.metadata}[key]

    def get_matrix_np(self):
        import numpy as np
        matrix = np.frombuffer(self.thermoblob[0x22:0x9622], dtype=np.uint16)
        matrix = matrix.reshape((120, 160))
        matrix = (matrix - 10000) * 0.01 # scaling to deg C
        return matrix

    def get_matrix_lst(self):
        """ Get the array as a list of 120 x 160 values """
        matrix = struct.unpack("<19200H", self.thermoblob[0x22:0x22+38400])
        # reshape the list
        n_rows, n_cols = 120, 160
        matrix = [list(matrix[i*n_cols:(i+1)*n_cols]) for i in range(n_rows)]
        # scale to deg C and round to 2 decimals:
        matrix = [[round((v-10000)*0.01, 2) for v in row] for row in matrix]
        return matrix

    def get_real_im(self):
        from PIL import Image
        return Image.open(io.BytesIO(self.jpeg_data))

def cli_plot():
    from matplotlib import pyplot as plt
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("measurement_file")
    args = parser.parse_args()

    with open(args.measurement_file, "rb") as f:
        t = Thermography(f.read())

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
    import argparse
    from matplotlib import pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=3.25, help="Scale the IR image up by this factor.")
    parser.add_argument("--shift", type=lambda x: tuple(int(e) for e in x.split(",")), default=(8, 6), help="Shift the IR image w.r.t. the real image by this amount of pixels.")
    parser.add_argument("--alpha", type=float, default=0.667, help="Transparency of the IR thermography overlay, range: 0.0 - 1.0.")
    parser.add_argument("--sat", type=float, default=0.4, help="Saturation of the real image, range: 0.0 - 1.0.")
    parser.add_argument("--cmap", type=plt.get_cmap, default="rainbow", help="Colormap to use. See matplotlib's documentation.")
    parser.add_argument("measurement_file")
    args = parser.parse_args()
    t = Thermography(args.measurement_file)
    blend = blend_real_and_ir(t, scale=args.scale, shift=args.shift, alpha=args.alpha, sat=args.sat, cmap=args.cmap)
    blend.save(args.measurement_file + ".blend.png")
    print(args.measurement_file + ".blend.png")
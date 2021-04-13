#!/usr/bin/env python

import struct
import io
from typing import Union

from .jpeg import thermoblob_extr
from .metadata import metadata_extr


class Thermography:

    unit = "°C"

    def __init__(self, jpeg_data: Union[bytes, str]):
        if type(jpeg_data) == str:
            with open(jpeg_data, "rb") as f:
                jpeg_data = f.read()
        self.jpeg_data = jpeg_data
        self.thermoblob = thermoblob_extr(jpeg_data)
        self.metadata = list(metadata_extr(self.thermoblob))

    def get(self, key):
        return {f.name: v for f, v in self.metadata}[key]

    def get_matrix_np(self):
        import numpy as np
        matrix = np.frombuffer(self.thermoblob[0x20:0x9620], dtype=np.uint16)
        matrix = matrix.reshape((120, 160))
        matrix = (matrix - 10000) * 0.01 # scaling to deg C
        return matrix

    def get_matrix_lst(self):
        """ Get the array as a list of 120 x 160 values """
        matrix = struct.unpack("<19200H", self.thermoblob[0x20:0x20+38400])
        # reshape the list
        n_rows, n_cols = 120, 160
        matrix = [list(matrix[i*n_cols:(i+1)*n_cols]) for i in range(n_rows)]
        # scale to deg C and round to 2 decimals:
        matrix = [[round((v-10000)*0.01, 2) for v in row] for row in matrix]
        return matrix

    def get_real_im(self):
        from PIL import Image
        return Image.open(io.BytesIO(self.jpeg_data))

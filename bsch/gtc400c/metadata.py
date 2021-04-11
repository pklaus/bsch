#!/usr/bin/env python

import collections
import struct

Field = collections.namedtuple("Field", ("name", "address", "format", "size", "precision"))

fields = [
  # not metadata:
  #Field("matrix", 0x22, "<19200H", 38400, None),
  Field("colorscale_min", 0x9622, "<f", 4, 2),
  Field("colorscale_max", 0x9626, "<f", 4, 2),
  Field("mode_flags", 0x962a, "B", 1, None),
  Field("centerpoint", 0x962b, "B", 1, None),
  Field("color_map", 0x962e, "B", 1, None),
  Field("transparency", 0x9634, "B", 1, None),
  Field("heat_detector_threshold", 0x9635, "B", 1, None),
  Field("cold_detector_threshold", 0x9636, "B", 1, None),
  Field("reflected_t", 0x963a, "<f", 4, 2),
  Field("sys_t", 0x963e, "<f", 4, 2),
  Field("epsilon", 0x9642, "<f", 4, 2),
  Field("material", 0x9646, "B", 1, None),
]

materials = {
  0: 'User-def.',
  1: 'Concrete',
  2: 'Mortar',
  3: 'Roofing tiles',
  4: 'Roofing felt',
  5: 'Radiator paint',
  6: 'Wood',
  7: 'Linoleum',
  8: 'Paper',
}

mode_flags = {
  0b10000000: 'coldest_indicator',
  0b01000000: 'hottest_indicator',
  0b00100000: 'cold_detector_mode',
  0b00010000: 'heat_detector_mode',
  0b00001000: 'blend_center',
  0b00000100: 'blend_transparent',
  0b00000010: 'blend_threshold',
  0b00000001: 'colorscale_lock',
}

color_maps = {
  0x0: 'Rainbow',
  0x1: 'Rainbow HM',
  0x2: 'Iron',
  0x3: 'Greyscale',
}

def metadata_extr(thermoblob):

    for field in fields:
        value = struct.unpack(field.format, thermoblob[field.address:field.address+field.size])
        if len(value) == 1:
            value = value[0]
        if field.precision:
            value = round(value, field.precision)
        if field.name == "material":
            value = materials[value]
        if field.name == "color_map":
            value = color_maps[value]
        if field.name == "mode_flags":
            flags = []
            for flag, name in mode_flags.items():
                if value & flag:
                    flags.append(name)
            value = flags
        yield field, value

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("thermoblob")
    args = parser.parse_args()


    with open(args.thermoblob, "rb") as f:
        content = f.read()
    for field, value in get_data(content):
        if field.name == "matrix":
            continue
        print(field.name, value)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import collections
import struct
import enum

Field = collections.namedtuple("Field", ("name", "address", "format", "size", "precision"))

fields = [
  Field("metadata_v", 0x0, "4s", 4, None),
  Field("firmware_v", 0x4, "4s", 4, None),
  Field("model", 0x8, "19s", 19, None),
  #Field("padding01", 0x1b, "c", 1, None),
  Field("serial", 0x1c, "I", 4, None),
  # not metadata:
  #Field("matrix", 0x20, "<19200H", 38400, None),
  Field("min", 0x9620, "<f", 4, 2),
  Field("max", 0x9624, "<f", 4, 2),
  Field("display_settings", 0x9628, "<I", 4, None),
  Field("color_map", 0x962c, "B", 1, None),
  #Field("padding02", 0x962d, "c", 1, None),
  Field("pip_x", 0x962e, "<H", 2, None),
  Field("pip_y", 0x9630, "<H", 2, None),
  Field("opacity", 0x9632, "B", 1, None),
  Field("heat_detector_threshold", 0x9633, "B", 1, None),
  Field("cold_detector_threshold", 0x9634, "B", 1, None),
  Field("center_foi", 0x9635, "B", 1, None),
  #Field("padding03", 0x9636, "2c", 2, None),
  Field("reflected_t", 0x9638, "<f", 4, 2),
  Field("sys_t", 0x963c, "<f", 4, 2),
  Field("epsilon", 0x9640, "<f", 4, 2),
  Field("material", 0x9644, "B", 1, None),
  #Field("padding04", 0x9645, "3c", 3, None),
  Field("vis_shift_x", 0x9648, "<h", 2, None),
  Field("vis_shift_y", 0x964a, "<h", 2, None),
  Field("vis_flip_x", 0x964c, "B", 1, None),
  Field("vis_flip_y", 0x964d, "B", 1, None),
  #Field("padding05", 0x964e, "2c", 2, None),
  Field("vis_scale_up", 0x9650, "<f", 4, None),
  Field("warmup_mode", 0x9654, "B", 1, None),
  Field("ir_gain_mode", 0x9655, "B", 1, None),
  Field("warn_inaccurate_low_gain_low_temp_thresh", 0x9656, "<H", 2, None),
  Field("warn_inaccurate_high_gain_high_temp_thresh", 0x9658, "<H", 2, None),
  #Field("padding06", 0x965a, "2c", 2, None),
  Field("device_date_code", 0x965c, "4s", 4, None),
  Field("reserved", 0x9660, "20s", 20, None),
]

class Material(enum.IntEnum):
  UserDefined = 0
  Concrete = 1
  Mortar = 2
  RoofingTiles = 3
  RoofingFelt = 4
  RadiatorPaint = 5
  Wood = 6
  Linoleum = 7
  Paper = 8

class DisplaySetting(enum.IntEnum):
  DegreeF        = 0b1000000000
  CenterSpot     = 0b0100000000
  ColdSpot       = 0b0010000000
  HotSpot        = 0b0001000000
  ColdDetector   = 0b0000100000
  HeatDetector   = 0b0000010000
  PicInPic       = 0b0000001000
  Alpha          = 0b0000000100
  VisDiscoloured = 0b0000000010
  TempscaleLock  = 0b0000000001

class ColorMap(enum.IntEnum):
  Rainbow = 0
  RainbowHM = 1
  Iron = 2
  Greyscale = 3

def metadata_extr(thermoblob):

    for field in fields:
        value = struct.unpack(field.format, thermoblob[field.address:field.address+field.size])
        if len(value) == 1:
            value = value[0]
        if field.name in ("metadata_v", "firmware_v"):
            value = tuple(value)
        if field.precision:
            value = round(value, field.precision)
        if field.name == "material":
            value = Material(value)
        if field.name in ("model", "device_date_code"):
            value = value.partition(b'\0')[0].decode('ascii')
        if field.name == "color_map":
            value = ColorMap(value)
        if field.name == "display_settings":
            flags = []
            for ds in DisplaySetting:
                if value & ds:
                    flags.append(ds.name)
            value = flags
        yield field, value

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("thermoblob")
    args = parser.parse_args()

    with open(args.thermoblob, "rb") as f:
        content = f.read()
    for field, value in metadata_extr(content):
        if field.name == "matrix":
            continue
        print(field.name, value)

if __name__ == "__main__":
    main()

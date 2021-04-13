"""
Tools to handle the JPG files saved by the Bosch GTC 400 C.
Main task: extract the 'thermoblob', i.e. the binary
thermography data embedded into the file.
"""

VERBOSE = False

segment_signatures = [
  {'name': 'SOI',         'marker': b'\xFF\xD8', 'length': 0},
  {'name': 'JFIF-APPO',   'marker': b'\xFF\xE0', 'length': 'header', 'signature': b'\x4A\x46\x49\x46\x00'},
  #{'name': 'EXIF-APP1',   'marker': b'\xFF\xE1', 'length': 'header', 'signature': b'\x45\x78\x69\x66\x00'},
  {'name': 'BSCH-APPF',   'marker': b'\xFF\xEF', 'length': 'header'},
  {'name': 'Quantization','marker': b'\xFF\xDB', 'length': 'header'},
  {'name': 'SOF0',        'marker': b'\xFF\xC0', 'length': 'header'},
  {'name': 'DHT',         'marker': b'\xFF\xC4', 'length': 'header'},
  {'name': 'SOS',         'marker': b'\xFF\xDA', 'length': 'scan'},
  {'name': 'EOI',         'marker': b'\xFF\xD9', 'length': 0},
]

class InvalidFileError(Exception):
    pass

def thermoblob_extr(jpeg_data):
    """ Extract the thermoblob from the given JPEG data """

    thermoblob = None

    content = jpeg_data

    # SOI - Start of Image
    assert content[0:2] == b'\xFF\xD8'
    # APPO - JFIF tag
    assert content[2:4] == b'\xFF\xE0'
    assert content[6:11] == b'\x4A\x46\x49\x46\x00'
    
    
    pos = 0
    eoi_found = False
    while True:
        marker = content[pos:pos+2]
        if VERBOSE: print(f"0x{pos:08X} - {marker[0]:02X} {marker[1]:02X} - ", end='')
        last_pos = pos
        for segdef in segment_signatures:
            if marker == segdef['marker'] and segdef.get('length') == 0:
                pos += 2
                if VERBOSE: print(f"Found {segdef['name']} segment.")
                if segdef['name'] == 'EOI':
                    eoi_found = True
                break
            if marker == segdef['marker'] and segdef.get('length') == 'header' and content[pos+4:pos+9] == segdef.get('signature') or \
               marker == segdef['marker'] and segdef.get('length') == 'header' and 'signature' not in segdef:
                length = content[pos+2] * 256 + content[pos+3]
                if VERBOSE: print(f"Found {segdef['name']} segment with {length} bytes length.")
                if segdef['name'] == "BSCH-APPF":
                    thermoblob = content[pos+4:pos+2+length]
                    # basically we can abort reading the file at this point...
                    return thermoblob
                pos += 2 + length
                break
            if marker == segdef['marker'] and segdef.get('length') == 'scan':
                if VERBOSE: print(f"Found {segdef['name']} segment. Reading...")
                delete_pos = []
                length = 0
                payload = b''
                while True:
                    if length % (1024*1024) == 0:
                        if VERBOSE: print(f"{length/(1024*1024)} MiB")
                    if content[pos+2+length:pos+2+length+2] == b'\xff\x00':
                        # FF 00 (FF in data, 00 as noop)
                        delete_pos.append(length+1)
                        length += 2
                    elif content[pos+2+length] == 255 and content[pos+2+length+1] in range(208, 208+8):
                        # FF (D0..D7)
                        delete_pos.append(length)
                        delete_pos.append(length+1)
                        length += 2
                    elif content[pos+2+length] == 255:
                        # FF with following byte other than 00, D0..D7 (-> new segment)
                        #payload = list(content[pos+2:pos+2+length])
                        # Takes too much time... skip for now:
                        #if VERBOSE: print(f"payload size before deleting zeros: {len(payload)}")
                        #for payload_pos in reversed(sorted(delete_pos)):
                        #    del payload[payload_pos]
                        #if VERBOSE: print(f"payload size after deleting zeros: {len(payload)}")
                        #payload = bytes(payload)
                        #if VERBOSE: print(f"payload (bytes) size after deleting zeros: {len(payload)}")
                        pos += 2 + length
                        break
                    else:
                        length += 1
                if VERBOSE: print(f"Found {segdef['name']} segment with {length} bytes length.")
        if eoi_found:
            break
        if pos == last_pos and pos < len(content):
            if VERBOSE: print(f"unknown marker: {marker} @ pos {pos:X}h")
            pos += 1
        if pos == len(content)-1:
            break
    if pos < len(content):
        trailing_content = content[pos:]
        if VERBOSE: print(f"0x{pos:08X} Trailing content: {len(trailing_content)} bytes long")
    else:
        if VERBOSE: print(f"No trailing content.")

    if thermoblob is None:
        raise InvalidFileError("No thermography data found, please open an image like RB-----Y.JPG")

    return thermoblob

def main():
    global VERBOSE

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('jpeg_file')
    args = parser.parse_args()

    if args.output is None:
        args.output = args.jpeg_file + ".thermoblob"

    VERBOSE = args.verbose

    with open(args.jpeg_file, 'rb') as f:
        thermoblob = thermoblob_extr(f.read())

    with open(args.output, "wb") as f:
        f.write(thermoblob)

if __name__ == "__main__":
    main()

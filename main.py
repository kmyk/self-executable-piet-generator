# Python Version: 3.x
# -*- coding: utf-8 -*-
import PIL.Image  # https://pypi.python.org/pypi/Pillow/5.0.0
import base64
import binascii
import hashlib
import io
import os
import struct
import zlib

# NOTE: network byte order
p8  = lambda n: struct.pack('!B', n)
p16 = lambda n: struct.pack('!H', n)
p32 = lambda n: struct.pack('!I', n)
p64 = lambda n: struct.pack('!Q', n)
u8  = lambda s: struct.unpack('!B', s)[0]
u16 = lambda s: struct.unpack('!H', s)[0]
u32 = lambda s: struct.unpack('!I', s)[0]
u64 = lambda s: struct.unpack('!Q', s)[0]

def generate_png_chunk(chunk_type, data, fh):
    fh.write(p32(len(data)))
    fh.write(chunk_type.encode())
    fh.write(data)
    fh.write(p32(binascii.crc32(chunk_type.encode() + data)))

def generate_png_ihdr_chunk(im, fh):
    data = b''.join([
        p32(im.width),
        p32(im.height),
        p8(8),  # bit depth
        p8(2),  # colour type = truecolour
        p8(0),  # compression method
        p8(0),  # filter method
        p8(0),  # interlace method
    ])
    generate_png_chunk('IHDR', data, fh)

def generate_png_idat_chunk(im, fh):
    pix = im.load()
    data = []
    for y in range(im.height):
        data += [ 0 ]  # line filter method = none
        for x in range(im.width):
            data += pix[x, y]
    generate_png_chunk('IDAT', zlib.compress(bytes(data)), fh)

def generate_png_text_chunk_1(command, delimiter, fh, embed=None):
    # tEXt chunk for the interpreter
    data = []
    data += [ b'Comment\0' ]  # keyword
    escape = bytes(reversed(list(filter(lambda c: c in b"\"'`", fh.getvalue()))))  # TODO: do strictly
    data += [ escape + b'= :;' ]
    if embed is not None:
        with open(embed, 'rb') as embed_fh:
            data += [ b"base64 -d <<EOF > %s\n" % os.path.basename(embed).encode() ]
            data += [ base64.b64encode(embed_fh.read()) + b'\n' ]
            data += [ b'EOF\n' ]
    data += [ command.encode() + b'\n' ]
    data += [ b": <<'%s'\n" % delimiter ]
    generate_png_chunk('tEXt', b''.join(data), fh)

def generate_png_text_chunk_2(delimiter, fh):
    data = b"\n%s\n#" % delimiter  # close heredoc
    generate_png_chunk('tEXt', data, fh)

def generate_png(im, command, embed=None):
    fh = io.BytesIO()
    fh.write(b'\x89PNG\r\n\x1a\n') # PNG file signature
    generate_png_ihdr_chunk(im, fh)
    delimiter = hashlib.sha256(b'piet').hexdigest().encode()  # use heredoc to escape other chunks
    generate_png_text_chunk_1(command, delimiter, fh, embed=embed)
    generate_png_idat_chunk(im, fh)
    generate_png_text_chunk_2(delimiter, fh)
    generate_png_chunk('IEND', b'', fh) # IEND chunk
    return fh.getvalue()

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('--command', default='exec npiet $0')
    parser.add_argument('--embed')
    args = parser.parse_args()

    if args.file is None:
        x = PIL.Image.open(sys.stdin.buffer)
    else:
        x = PIL.Image.open(args.file)
    y = generate_png(x, command=args.command, embed=args.embed)
    sys.stdout.buffer.write(y)

if __name__ == '__main__':
    main()

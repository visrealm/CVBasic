#!/usr/bin/env python3

import os.path
import sys

# take the first name, and return (base,zeros)
# where zeros is how many leading zeros are in the index
def parseFilename(fn):
    zerocnt = 1
    namebase = fn[:-5]
    while (namebase[-1] == '0'):
        zerocnt += 1
        namebase = namebase[:-1]
    return (namebase, zerocnt)

# converts a binary from xas99 (xas99.py -b -R file.a99) with banks to a single non-inverted cart image
# note: minimal error checking - GIGO.
# pass the name of the first file (ie: file_b0.bin)
if (len(sys.argv) < 3):
    print('Pass the first output file (ie: file_b0.bin), and the output file, and optionally a name for the cart')
    print('ie: linkticart.py file_b0.bin file_8.bin "AWESOME GAME"')
    exit(1)

f = open(sys.argv[1], 'rb')
data = f.read()
f.close()

# first 80 bytes are the cartridge header
hdr = data[0:80]

def update_cart_name(header_data, cart_name):
    """Update all instances of CVBASIC GAME in the header"""
    original = b'CVBASIC GAME        *'
    if original in header_data:
        name_bytes = bytearray(cart_name, 'utf-8') + b'*'
        return header_data.replace(original, name_bytes)
    return header_data

cart_name = None
if (len(sys.argv) > 3):
    cart_name = sys.argv[3].upper()
    while (len(cart_name)<20):
        cart_name += ' '
    hdr = update_cart_name(hdr, cart_name)
    if b'CVBASIC GAME' in hdr:
        print('WARNING: Could not find cart name to set it')

# after 16k starts the RAM data
ram = data[16384:]

# make sure we have 3 pages to pull from (especially if not banked, it won't be padded)
while len(ram) < 8192*3:
    ram += b'\xff'*8192

fo = open(sys.argv[2], 'wb')

# write the loader pages
fo.write(hdr)
fo.write(ram[0:8112])
fo.write(hdr)
fo.write(ram[8112:16224])
fo.write(hdr)
fo.write(ram[16224:24336])
# any excess is discarded

# now check if there are any pages to concatenate
# track pages written so we can square up the final size
sz = 3

if (sys.argv[1][-5:] != '0.bin'):
    print('Banking not detected - finishing cart...')
else:
    print('Banked cart detected...')

    (namebase,zerocnt) = parseFilename(sys.argv[1])

    file = namebase + str(sz).zfill(zerocnt) + '.bin'
    
    while os.path.isfile(file):
        f = open(file, 'rb')
        data = f.read()
        if len(data) < 8192:
            while len(data)<8192:
                data += b'\xff'
        f.close()
        # Update cart name in this bank's header if present
        if cart_name and len(data) >= 80 and b'CVBASIC GAME' in data[0:80]:
            bank_hdr = data[0:80]
            bank_hdr = update_cart_name(bank_hdr, cart_name)
            data = bank_hdr + data[80:]
        fo.write(data)
        sz+=1
        file = namebase + str(sz).zfill(zerocnt) + '.bin'

# calculate number of files needed for power of two
desired=0
if sz>64:
    desired=128
elif sz>32:
    desired=64
elif sz>16:
    desired=32
elif sz>8:
    desired=16
elif sz>4:
    desired=8
else:
    desired=4

while sz<desired:
    sz+=1
    fo.write(hdr)
    fo.write(b'\xff'*8112)

fo.close()
print('Wrote final cart size:',sz*8,'KB')

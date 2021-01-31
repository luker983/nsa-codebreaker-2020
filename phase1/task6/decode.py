#!/usr/bin/env python3


# masks derived from mask_finder.py
masks = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0],
[0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
[0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
[0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0],
[0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0],
[0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0],
[0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
[0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
[0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0],
[0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0],
[0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0],
[0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
[0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0],
[0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0],
[0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
[1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0],
[1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
[1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
[1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
[1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
[1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0],
[1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0],
[1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
[1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0],
[1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
[1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
[1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0],
[1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0],
[1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
[1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
]

# which bits are data? not sure, trial and error here
data_bit_masks = [
#[2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]
#[3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15],
#[1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 14],
# this one is correct:
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
]

def bitstring_to_bytes(s):
    return bytes(int(s[i : i + 8], 2) for i in range(0, len(s), 8))

# yet another parity check function, this time uses all masks and returns
# index of bit that needs to be flipped
# totally not necessary for this challenge, but I learned something so that's cool
def parity_check(s):
    sum = 0
    
    # make list of the indices with ones in them
    columns = []
    for i, c in enumerate(s):
        if c:
            columns.append(i)

    # generate syndrome
    syndrome = []
    for mask in masks:
        sum = 0
        for x in columns:
            sum += mask[x]
        syndrome.append(sum % 2)

    # error stays -1 if no error
    error = -1
    # check masks against syndrome
    if any(syndrome):
        for i in range(0, 17):
            for j, mask in enumerate(masks):
                if mask[i] != syndrome[j]:
                    break
                if j == len(masks) - 1:
                    error = i
            if error != -1:
                break
                
    return error

# read bitstream from float parse
with open('bits.txt', 'r') as f:
    bit_stream = f.read()

# break into 17 bit chunks
segments = [bit_stream[i:i+17] for i in range(0, len(bit_stream), 17)]
blocks = []

# string to int
for i, s in enumerate(segments):
    blocks.append([])
    for b in s:
        blocks[i].append(int(b))

# error correction (again, not necessary)
for i, block in enumerate(blocks):
    # check for an error
    e = parity_check(block)
    if e != -1:
        # correct error
        blocks[i][e] = (blocks[i][e] + 1) % 2

# not sure which bits are data, try multiple
# removed code that tests every bit offset

# now we have error-corrected bit stream with no offset
for i, mask in enumerate(data_bit_masks):
    bit_stream = ''
    for j, block in enumerate(blocks):
        for index in mask:
            bit_stream += str(block[index])

    with open('playable_output' + str(i), 'wb') as f:
        b = bitstring_to_bytes(bit_stream)
        f.write(b)

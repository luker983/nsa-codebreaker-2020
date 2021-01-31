#!/usr/bin/env python3

# check to see if there is an extended parity bit
def parity_check(s):
    sum = 0
     
    for b in s:
        if b == "1":
            sum += 1
            
    if sum % 2 != 0:
        return False
    
    return True 

# read bit stream from float_parser.py
with open('bits.txt', 'r') as f:
    bit_stream = f.read()

# shorten bit stream because we don't need that many to get decent statistics
# also, find section of bits that isn't all zeros
small_bit_stream = bit_stream[len(bit_stream) // 2:len(bit_stream) // 2 + 8192]

# print(small_bit_stream)

best_rate = 0
best_size = -1
# we received part of a transmission, code could start at any offset within the block size
for offset in range(0, 128):
    # minimum distance is 3, can go bigger than 128 but...
    # unlikely considering max characters in parity-check-matrix submission
    for block_size in range(3, 128):
        parity_count = 0
        # break up bitstream into block_size chunks
        segments = [small_bit_stream[i:i+block_size] for i in range(0, len(small_bit_stream), block_size)]
        # see if there's parity between all of the bits
        for s in segments:
            if parity_check(s):
                parity_count += 1

        # should have very high success rate if this is correct block size
        rate = parity_count / len(segments)
        if rate > best_rate:
            best_rate = rate
            best_size = block_size

    # shift bits to try new offset
    small_bit_stream = small_bit_stream[1:]

# now find offset from beginning of bit stream
bit_stream = bit_stream[:8192]
best_rate = 0
best_offset = -1
for offset in range(0, 128):
    parity_count = 0
    # break up bitstream into block_size chunks
    segments = [bit_stream[i:i+best_size] for i in range(0, len(bit_stream), best_size)]
    # see if there's parity between all of the bits
    for s in segments:
        # debug
        #if offset == 0:
        #    print(s)
        if parity_check(s):
            parity_count += 1

    # should have very high success rate if this is correct block size
    rate = parity_count / len(segments)
    if rate > best_rate:
        best_rate = rate
        best_offset = offset

    bit_stream = bit_stream[1:]

print("Most Likely Block Size:", best_size, "Offset:", best_offset, "Best Rate:", best_rate)

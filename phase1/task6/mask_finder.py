#!/usr/bin/env python3

import random
from tqdm import tqdm

# parity check, this time with a variable mask
def parity_check(s, mask):
    sum = 0
   
    for i in range(0, len(s)):
            sum += mask[i] & s[i]

    if sum % 2 != 0:
        return False
    
    return True

with open('bits.txt', 'r') as f:
    bit_stream = f.read()

# we know it's in 17 bit chunks now and offset starts at 0
segments = [bit_stream[i:i+17] for i in range(0, len(bit_stream), 17)]
blocks = []

# numbers are easier (faster) to work with than strings
for i, s in enumerate(segments):
    blocks.append([])
    for b in s:
        blocks[i].append(int(b))

# only need a subset of blocks, and not all zeros
blocks = blocks[4096:4096 + 256]

candidates = []
#print(blocks)
# try every possible mask to determine which ones are viable
for mask in tqdm(range(0, 2**16)):
    # generate mask
    mask_res = [int(i) for i in list('{0:0b}'.format(mask))] 
    mask_res = [0] * (16 - len(mask_res)) + mask_res + [0]
    parity_count = 0
    
    for block in blocks:
        if parity_check(block, mask_res):
            parity_count += 1

    # set threshold of 0.95
    if (parity_count / len(blocks)) > 0.95:
        candidates.append(mask_res)

for c in candidates:
    print(c)

#!/usr/bin/env python3

import numpy as np
#!/usr/bin/env python3

import numpy as np
import random

# read bytes from signal.ham
with open('signal.ham', 'rb') as f:
    raw = f.read()

# convert to list of two bytes each
floats = [raw[i:i+2] for i in range(0, len(raw), 2)]

# convert each two-byte segment into a half-precision float
bits = []
for f in floats:
    bits.append(np.frombuffer(f, dtype=np.float16)[0])

# each bit can be stringified and written to a file
bit_stream = ''
for b in bits:
    # nan edge case
    if np.isnan(b):
        bit_stream += random.choice(["0","1"])
    else:
        if b < 0:
            bit_stream += "0"
        else:
            bit_stream += "1"

with open('bits.txt', 'w') as f:
    f.write(bit_stream)

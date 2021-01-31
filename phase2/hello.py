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

    print("sending HELLO:")
    print('\n'.join(chunker(frame.hex(), 16)))
    s.send(frame)

    print("RECVing HELLO...")
    pkt = s.receive()
    print('\n'.join(chunker(pkt.hex(), 16)))

    (flags, msg, unknown_zeros), rest = parse_pkt(pkt)
    assert flags == 1
    assert msg == 0
    assert len(rest) == 35
    # nodetype seems to correspond to the the first argument to "router"
    unknown_maybe_random, nodetype, name = struct.unpack('>HB32s', rest)
    name = name.rstrip(b'\x00')
    print('connected to:', unknown_maybe_random, nodetype, name)
    return s


def run(host, port, v=False):
    s = connect(host, port)
    s
    # TODO... do something

def send_packet(filename, host, port, v=False):
    s = connect(host, port)
    with open(filename, 'rb') as fobj:
        packet_data = fobj.read(0xFFFF) # 0xFFFF maximum frame size
    s.send(make_frame(packet_data))
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

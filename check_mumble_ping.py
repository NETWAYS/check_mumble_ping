#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2021 NETWAYS GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -*- coding: utf-8
# Based on pcgod's mumble-ping script found at http://0xy.org/mumble-ping.py.
# Based on https://github.com/mumble-voip/mumble-scripts/blob/master/Non-RPC/mumble-ping.py

import sys
import argparse
import socket
import datetime

from struct import pack, unpack

def return_plugin(status, msg):
    states = {
        0: "OK",
        1: "WARNING",
        2: "CRITICAL",
        3: "UNKNOWN"
    }

    print("Mumble: {0} - {1}".format(states[status], msg))

    return status

def ping_mumble(host, port=64738):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)

    buf = pack(">iQ", 0, datetime.datetime.now().microsecond)
    s.sendto(buf, (host, port))

    data, _ = s.recvfrom(1024)

    r = unpack(">bbbbQiii", data)

    version = r[1:4]
    # r[0,1,2,3] = version
    # r[4] = ts
    # r[5] = users
    # r[6] = max users
    # r[7] = bandwidth

    ping = (datetime.datetime.now().microsecond - r[4]) / 1000.0
    if ping < 0:
        ping = ping + 1000

    return {
        "version": version,
        "user": r[5:7],
        "time": ping,
        "rate": r[7],
        "len": len(data)
    }

def commandline(args):
    parser = argparse.ArgumentParser(prog="check_mumble_ping.py")

    parser.add_argument('-H', '--host', type=str, required=True,
                        help='Mumble host')
    parser.add_argument('-p', '--port', type=int, required=False,
                        default=64738,
                        help='Mumble port (default is 64738')

    return parser.parse_args(args)


def main(args):
    try:
        ping = ping_mumble(args.host, args.port)
    except Exception as e: # pylint: disable=broad-except
        return return_plugin(3, "Error: could not send ping ({0})".format(e) )

    items = [
        "version={0[0]}.{0[1]}.{0[2]}".format(ping["version"]),
        "user={0[0]}/{0[1]}".format(ping["user"]),
        "time={:.2f}ms".format(ping["time"]),
        "rate={:.2f}kbit/s".format(ping["rate"]/1000),
        "len={:d}b".format(ping["len"])
    ]

    return return_plugin(0, ", ".join(items))


if __name__ == '__main__': # pragma: no cover
    try:
        ARGS = commandline(sys.argv[1:])
        sys.exit(main(ARGS))
    except SystemExit:
        # Re-throw the exception
        raise sys.exc_info()[1].with_traceback(sys.exc_info()[2]) # pylint: disable=raise-missing-from
    except:
        print("UNKNOWN - Error: %s" % (str(sys.exc_info()[1])))
        sys.exit(3)

#!/usr/bin/env python3

import argparse
import logging
import binascii
from src.tmpclient import TMPClient
from src.tmp import HDR_SZ, CTRL_SZ

def handle_args():
    """
    A wrapper for the command line argument handling.

    :return: args object
    :rtype: Namespace
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
            "host",
            help="""Host IPv4""",
        )
    parser.add_argument(
            "port",
            help="""TCP port""",
            default=20002,
        )
    parser.add_argument(
            "-p","--payload",
            help="""Data to send""",
            default="",
        )
    parser.add_argument(
            "-o","--opcode",
            dest="opcode",
            help="""TMP opcode""",
            default="0",
        )
    parser.add_argument(
            "-v","--verbose",
            dest="verbose",
            help="""Verbose mode - logging enabled""",
            action="store_true",
        )

    return parser.parse_args()

def main():
    """
    Wraps the main logic of the program into one function.
    """
    args = handle_args()

    # determine log level
    logging.basicConfig(
        level = (logging.DEBUG if args.verbose else logging.INFO)
    )

    client = TMPClient(
                args.host,
                args.port
            )

    ## example client session ##
    client.assoc()
    client.hello()
    pkt = client.recv()
    client.send(
        int(args.opcode,16),
        bytes(args.payload,'utf-8')
    )
    pkt = client.recv()
    print(pkt[HDR_SZ+CTRL_SZ:].decode())
    client.bye()
    pkt = client.recv()
    client.close()

if __name__ == "__main__":
    main()

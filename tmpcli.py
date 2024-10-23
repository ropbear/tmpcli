#!/usr/bin/env python3

import argparse
import logging
from src.tmpclient import TmpClient

def handle_args():
    """
    A wrapper for the command line argument handling.

    Return: Argparse object with parsed arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
            "server",
            help="""Server IP""",
        )
    parser.add_argument(
            "port",
            help="""Server port""",
            default=20002,
        )
    parser.add_argument(
            "-p","--payload",
            help="""Payload to send""",
            default="",
        )
    parser.add_argument(
            "-V","--version",
            dest="version",
            help="""TMP version""",
            default=0,
        )
    parser.add_argument(
            "-B","--business-type",
            dest="business_type",
            help="""Who knows what this is, @tplink""",
            default=2,
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

    client = TmpClient(
                args.server,
                args.port,
                args.business_type,
                args.version,
            )
    client.send(int(args.opcode,16), bytes(args.payload,'utf-8'))

if __name__ == "__main__":
    main()

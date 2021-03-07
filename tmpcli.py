#!/usr/bin/env python3

import argparse
from src.logger import Logger
from src.client import TmpClient

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
            "-T","--packet-type",
            dest="packet_type",
            help="""Toggle TDP or OneMesh""",
            default="1",
        )
    parser.add_argument(
            "-o","--opcode",
            dest="opcode",
            help="""TMP/TDP opcode""",
            default="0",
        )
    parser.add_argument(
            "-t","--tdp",
            dest="use_tdp",
            action="store_true",
            help="""Send payload over TDP instead of TMP""",
            default=False,
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
    logger = Logger(verbosity=4)
    logger.verbosity = 4 if args.verbose else 0

    # logger up TMP Client
    logger.log("TMPCLI","INFO","Creating TMP Client")
    client = TmpClient(
                args.server, args.port, logger,
                args.business_type, args.version,
            )
    if args.use_tdp:
        client.use_tdp = True
    logger.log("TMPCLI","INFO","Sending payload")
    if args.use_tdp:
        client.send(args.opcode, args.payload, args.packet_type)
    else:
        client.send(args.opcode, args.payload)

if __name__ == "__main__":
    main()

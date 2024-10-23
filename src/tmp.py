import binascii
import struct
import logging
from enum import Enum

MAXSIZE = 0x400
HDR_SZ = 0x18
DATA_SZ = MAXSIZE - HDR_SZ

PKT_REQ         = 1
PKT_RSP         = 2
PKT_PUSH_ACK    = 3
PKT_PULL        = 4
PKT_DATA        = 5
PKT_PUSH        = None
PKT_PULL_ACK    = None


# the following diagram is 32 bits wide
"""
 0                   1                   2                   3  
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       1       |       V       |              typ              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|              len              |              flg              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             serial                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             chksum                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       B       |               op              |      pad      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|               |                                               |
+-+-+-+-+-+-+-+-+                                               +
|                              data                             |
+                                                               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
"""

def checksum(header, payload):
    """
    Calculate the CRC32 checksum of a packet
    """
    crc32 = binascii.crc32(header + payload)
    return struct.pack('!L', crc32)

class TMPPacket:
    """
    A class to house the structure and functionality of a Tether Management Protocol (TMP) packet.
    """

    def __init__(
        self, opcode=0, data=b"", serial=0xdeadbeef,
        packet_type=PKT_REQ, flags=0, version=0, business_type=2
    ):
        self.opcode         = opcode
        self.data           = data
        self.serial         = serial
        self.packet_type    = packet_type
        self.flags          = flags
        self.version        = version
        self.btype          = business_type

        self.packet = self.__construct()

    def __repr__(self) -> str:
        pass



    def __construct(self):
        header = struct.pack("B", 1) # always 1
        header += struct.pack("B", self.version)
        header += struct.pack("<H", self.packet_type)
        if self.packet_type != PKT_DATA:
            # REQ and RSP packet types are only 4 bytes
            return header

        # building data packet
        header += struct.pack("!H", 8+len(self.data)) # from after checksum
        header += struct.pack("<H", self.flags)
        header += struct.pack("!L", self.serial)
        header += struct.pack("!L", 0x5a6b7c8d) # placeholder checksum
        header += struct.pack("!B", self.btype)
        header += struct.pack("!B", 1) # always 1
        header += struct.pack("!H", self.opcode)
        header += struct.pack("!L", 0) # some padding maybe?

        crc = checksum(header, self.data)

        if self.data is not None:
            # only add the checksum if it's a data packet
            header = header[:12] + crc + header[16:]
            logging.debug(f"Packet checksum {binascii.hexlify(crc)}")
            return header + self.data
        else:
            return header

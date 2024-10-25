import binascii
import struct
import logging
from src.util import checksum, CRC_DEFAULT
from enum import Enum

MAXSIZE = 0x4000
HDR_SZ  = 0x10
CTRL_SZ = 0x8
DATA_SZ = MAXSIZE - HDR_SZ

PKT_REQ         = 1
PKT_RSP         = 2
PKT_HELLO       = 4
PKT_DATA        = 5
PKT_BYE         = 6

STRUCT_TMP_PKT = "!BBBBHHLLBBHL"

"""
 0                   1                   2                   3  
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   ver_major   |   ver_minor   |      type     |     reason    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             length            |             flags             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             serial                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            checksum                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    svc_type   |    svc_ver    |             opcode            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            padding                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
"""

class TMPPacket:
    """
    A class to house the structure and functionality of a Tether Management Protocol (TMP) packet.
    """

    def __init__(self):
        pass

    def __repr__(self) -> str:
        pass

    def __construct(self):
        header = struct.pack(
            STRUCT_TMP_PKT,
            self.ver_major,
            self.ver_minor,
            self.packet_type,
            self.reason_code,
            self.length,
            self.flags,
            self.serial,
            CRC_DEFAULT,
            self.service_type,
            self.service_ver,
            self.opcode,
            self.token
        )

        if self.packet_type in [PKT_REQ, PKT_RSP]:
            # REQ and RSP packet types are only 4 bytes
            return header[:4]
        
        elif self.packet_type in [PKT_HELLO, PKT_BYE]:
            self.data = b""
            header = header[:16]


        crc = checksum(header, self.data)

        header = header[:12] + crc + header[16:]
        return header + self.data

    def pack(
        self, ver_major=1, ver_minor=0,
        packet_type=PKT_REQ, reason_code=0, flags=0,
        serial=0,
        service_type=1, service_version=1,
        opcode=0, token=0, data=None,
    ):
        """
        Handles defaults for the TMPPacket, then constructs the packet with __construct()

        :param int ver_major: Major version, always has been 1
        :param int ver_minor: Minor version, always has been 0
        :param int packet_type: The packet type (REQ, RSP, HELLO, DATA, BYE)
        :param int reason_code: always has been 0
        :param int length: Length of data calculated starting from after CRC32
        :param int flags: Misc flags, have not seen them used
        :param int serial: Serial number, usually NULL
        :param int service_type: Service you want to access, usually 1
        :param int service_version: Unsure, but has always been 1
        :param int opcode: Opcode to execute on the service
        :param int token: Maybe used for token at some point, but maybe just padding
        :param bytes data: payload, usually JSON sometimes not 
        """
        self.ver_major      = ver_major
        self.ver_minor      = ver_minor
        self.packet_type    = packet_type
        self.reason_code    = reason_code
        self.length         = len(data) + CTRL_SZ if packet_type == PKT_DATA else 0
        self.flags          = flags
        self.serial         = serial
        self.service_type   = service_type
        self.service_ver    = service_version
        self.opcode         = opcode
        self.token          = token
        self.data           = data

        return self.__construct()

    def unpack(self, rawdata):
        #TODO
        self.data = rawdata

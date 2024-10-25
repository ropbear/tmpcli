import binascii
import struct

CRC_DEFAULT = 0x5a6b7c8d

def checksum(header, payload):
    """
    Calculate the CRC32 checksum of a packet
    """
    data = b"" if payload is None else payload
    crc32 = binascii.crc32(header + data)
    return struct.pack('!L', crc32)

def pp(pkt):
    pretty = ""
    hx = binascii.hexlify(pkt).decode()
    for i in range(0,len(hx),8):
        pretty += hx[i:i+8]
        pretty += "\n"
    return pretty
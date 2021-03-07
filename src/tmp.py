import binascii
import struct

class TmpPacket:
    """
    A class to house the structure and functionality of a TMP/TDP packet.

    `opcode[int]`: The opcode to send.

    `data[str]`: Data to send.
    """

    MAXSIZE = 0x400
    HDR_SZ = 0x10
    DATA_SZ = MAXSIZE - HDR_SZ

    TYPE_REQ = 1
    TYPE_RSP = 2
    TYPE_DAT = 5

    def __init__(self, logger, opcode=0, data=""):
        self.opcode = opcode
        self.data = data
        self.serial = 0xdeadbeef

        self.logger = logger

        # placeholders
        self.header = b""
        self.checksum = b""
        self.payload = b""
        self.packet_type = self.TYPE_REQ
        self.flags = 0 # flags set manually due to infrequent use
        self.version = 0
        self.btype = 2

    def __checksum(self):
        """
        Calculate the checksum of the packet.

        Returns: None (sets checksum attribute)
        """
        crc32 = binascii.crc32(self.header + self.payload)
        self.checksum = struct.pack('!L', crc32)
        if self.packet_type == self.TYPE_DAT:
            # only add the checksum if it's a data packet
            self.header = self.header[:12] + self.checksum + self.header[16:]

    def __header(self):
        """
        Determine the packet header bytes.

        Returns: None (creates header attribute).
        """
        header = struct.pack("B", 1) # always 1
        header += struct.pack("B", self.version)
        header += struct.pack("<H", self.packet_type)
        if self.packet_type != self.TYPE_DAT:
            # REQ and RSP packet types are only 4 bytes
            self.header = header
            return
        header += struct.pack("!H", 8+len(self.data)) # from after checksum
        header += struct.pack("<H", self.flags)
        header += struct.pack("!L", self.serial)
        header += struct.pack("!L", 0x5a6b7c8d) # placeholder checksum
        header += struct.pack("!B", self.btype)
        header += struct.pack("!B", 1) # always 1
        header += struct.pack("!H", self.opcode)
        header += struct.pack("!L", 0) # some padding maybe?
        self.header = header

    def __payload(self):
        """
        Prepare the data for transmission as payload

        Returns: None (creates payload attribute)
        """
        if self.packet_type == self.TYPE_DAT:
            # only add the payload if it's a data packet
            self.payload = bytes(self.data, 'utf-8')
        else:
            self.payload = bytes("", 'utf-8')

    def build(self, packet_type=TYPE_REQ, version=0, business_type=2):
        """
        Construct the packet.

        `version[int]`: The TMP version to use

        `packet_type[int]`: The type of packet to send.

        `business_type[int]`: Sets some flag in the header that changes flow.

        Returns: Packet bytes
        """
        self.packet_type = packet_type
        self.version = version
        self.btype = business_type
        self.__header()
        self.__payload()
        self.__checksum()

        self.logger.log("TMP_PACKET","INFO","Checksum %s" %
                    binascii.hexlify(self.checksum)
                )

        packet_bytes = self.header + self.payload
        return packet_bytes

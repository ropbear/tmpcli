import binascii
import struct

class TdpPacket:
    """
    A class to house the structure and functionality of a TDP packet.

    `opcode[int]`: The opcode to send.

    `data[str]`: Data to send.
    """

    MAXSIZE = 0x400
    HDR_SZ = 0x10
    DATA_SZ = MAXSIZE - HDR_SZ

    TYPE_TDPD = 1
    TYPE_ONEMESH = 0xf0 # onemesh payloads are AES encrypted

    def __init__(self, logger, opcode=0, data=""):
        self.opcode = opcode
        self.data = data
        self.serial = 0xdeadbeef

        self.logger = logger

        # placeholders
        self.header = b""
        self.checksum = b""
        self.payload = b""
        self.packet_type = self.TYPE_TDPD
        self.flags = 0 # flags set manually due to infrequent use
        self.version = 1

    def __checksum(self):
        """
        Calculate the checksum of the packet.

        Returns: None (sets checksum attribute)
        """
        crc32 = binascii.crc32(self.header + self.payload)
        self.checksum = struct.pack("!L", crc32)
        if self.packet_type != self.TYPE_TDPD:
            self.header = self.header[:12] + self.checksum + self.header[16:]
        else:
            self.header = self.header[:12] + self.checksum

    def __header(self):
        """
        Determine the packet header bytes.

        Returns: None (creates header attribute).
        """

        self.logger.log("TDP_PACKET","INFO","Payload Length is %d" %
                    len(self.data)
                )

        header = struct.pack("!B", self.version)
        header += struct.pack("!B", self.packet_type)
        header += struct.pack("!H", self.opcode)
        header += struct.pack("!H", len(self.data)) # from after checksum
        header += struct.pack("!B", self.flags)
        header += struct.pack("!B", 0) # unknown
        header += struct.pack("!L", self.serial)
        header += struct.pack("!L", 0x5a6b7c8d) # placeholder checksum
        self.header = header

    def __payload(self):
        """
        Prepare the data for transmission as payload

        Returns: None (creates payload attribute)
        """
        self.payload = bytes(self.data, 'utf-8')

    def build(self, packet_type=TYPE_TDPD, version=1):
        """
        Construct the packet.

        `packet_type[int]`: The type of packet to send.

        `version[int]`: The TDP version to use

        Returns: Packet bytes
        """
        self.packet_type = packet_type
        self.version = version
        self.__header()
        self.__payload()
        self.__checksum()

        self.logger.log("TDP_PACKET","INFO","Checksum %s" %
                    binascii.hexlify(self.checksum)
                )

        packet_bytes = self.header + self.payload
        return packet_bytes

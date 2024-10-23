import socket
import logging
import src.tmp as tmp

RECVBUF_SIZE = 4096

class TmpClient:
    """
    A client to interface with the TMP server running on TP-Link routers.

    :param str host:              Server where tmpServer is running (TP-Link router)
    :param int port:                Port which tmpServer is running (20002)
    :param logging.Logger logger:   Logger instance
    :param int business_type:       Flag that changes logic flow
    :param int version:             tmpServer version
    """

    def __init__(self, host, port, business_type=2, version=1):
        self.btype      = business_type
        self.version    = version
        self.host     = host
        self.port       = int(port)


    def __create_socket(self):
        """
        Creates a socket object based on the ip, port, and protocol

        :return: socket.socket
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        logging.info(f"Connected to {self.host}:{self.port}")
        return sock


    def __do_handshake(self, sock):
        """
        Handle initial connection handshake with TMP/TDP server

        :param socket.socket sock:
        """
        sock.sendall(
            tmp.TMPPacket(
                packet_type     = tmp.PKT_REQ,
                business_type   = self.btype,
                version         = self.version
            ).packet
        )

        logging.debug("Request sent...")

        recv = sock.recv(RECVBUF_SIZE)
        logging.debug(f"Received {recv}")

        sock.sendall(
            tmp.TMPPacket(
                packet_type     = tmp.PKT_RSP,
                business_type   = self.btype,
                version         = self.version
            ).packet
        )
        logging.debug("Response sent.")


    def send(self, opcode, data):
        """
        Handing sending data over TCP to the TMP server.

        :param int opcode:      The desired opcode
        :param str data:        The data to send
        :return:                Boolean success
        """
        sock = self.__create_socket()
        self.__do_handshake(sock)

        sock.sendall(
            tmp.TMPPacket(
                opcode          = opcode,
                data            = data,
                packet_type     = tmp.PKT_DATA,
                business_type   = self.btype,
                version         = self.version
            ).packet
        )
        logging.info(f"sent packet with opcode {hex(opcode)}")


        #TODO build recv func
        data = b""
        recv = sock.recv(RECVBUF_SIZE)
        data += recv
        while recv == RECVBUF_SIZE:
            recv = sock.recv(RECVBUF_SIZE)
            data += recv

        logging.info("recieved %s" % data)
        return True


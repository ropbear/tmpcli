import socket
import logging
import src.tmp as tmp
from src.util import pp

RECVBUF_SIZE = 4096

class TMPClient:
    """
    A client to interface with the TMP server running on TP-Link routers.

    :param str host:              Server where tmpServer is running (TP-Link router)
    :param int port:                Port which tmpServer is running (20002)
    """

    def __init__(self, host, port):
        self.host       = host
        self.port       = int(port)
        self.sock       = self.__create_socket()


    def __create_socket(self):
        """
        Creates a socket object based on the ip, port, and protocol

        :return: socket.socket
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        logging.info(f"Connected to {self.host}:{self.port}")
        return sock


    def assoc(self):
        """
        Handle initial connection handshake with the TMP server
        """
        req = tmp.TMPPacket().pack(packet_type=tmp.PKT_REQ)
        self.sock.sendall(req)
        logging.debug(f"Sent req:\n{pp(req)}")

        recv = self.sock.recv(RECVBUF_SIZE)
        logging.debug(f"Received rsp:\n{pp(recv)}")

        rsp = tmp.TMPPacket().pack(packet_type=tmp.PKT_RSP)
        self.sock.sendall(rsp)

        logging.debug(f"Sent rsp:\n{pp(rsp)}")


    def hello(self):
        """
        Send a "hello" packet
        """
        pkt = tmp.TMPPacket().pack(packet_type=tmp.PKT_HELLO)
        self.sock.sendall(pkt)
        logging.debug(f"Sent hello:\n{pp(pkt)}")


    def bye(self):
        """
        Send a "bye" packet
        """
        pkt = tmp.TMPPacket().pack(packet_type=tmp.PKT_BYE)
        self.sock.sendall(pkt)
        logging.debug(f"Sent bye:\n{pp(pkt)}")


    def send(self, opcode, data):
        """
        Handing sending data over TCP to the TMP server.

        :param int opcode:      The desired opcode
        :param str data:        The data to send
        :return:                Boolean success
        """

        pkt = tmp.TMPPacket().pack(
                opcode          = opcode,
                data            = data,
                packet_type     = tmp.PKT_DATA,
                ver_minor       = 0,
                flags           = 0,
                service_type    = 1,
                service_version = 1,
                reason_code     = 0,
                token           = 0,
                serial          = 0
            )
        self.sock.sendall(pkt)
        logging.debug(f"Sent pkt:\n{pp(pkt)}")


    def recv(self):
        """
        Receive data from the socket, unpack it

        :return: pkt.data
        """
        #TODO add timeout
        data = b""
        while True:
            recv = self.sock.recv(RECVBUF_SIZE)
            data += recv
            if len(recv) < RECVBUF_SIZE:
                break

        pkt = tmp.TMPPacket()
        pkt.unpack(data)
        logging.debug(f"Received pkt:\n{pp(pkt.data)}")
        return pkt.data


    def close(self):
        """
        Closes the socket

        :return: return value of socket.close()
        """
        return self.sock.close()


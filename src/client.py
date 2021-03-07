import socket
from src.tmp import TmpPacket
from src.tdp import TdpPacket

class TmpClient:
    """
    A client to interface with the TMP and TDP servers running on TP-Link routers.

    `server[str]`: Server where tmpServer is running (TP-Link router)

    `port[int]`: Port which tmpServer is running (20002)

    `logger[obj]`: Logger instance

    `business_type[int]`: Flag that changes logic flow

    `version[int]`: tmpServer version
    """
    use_tdp = False # must be set manually

    def __init__(self, server, port, logger, business_type=2, version=1):
        self.btype = business_type
        self.version = version

        self.server = server
        self.port = int(port)
        self.logger = logger

    def __handle_socket(self):
        """
        Creates a socket object based on the ip, port, and protocol

        Supports domain names, IPv4, and IPv6

        Returns: Connected socket object, None on failure.
        """
        sock = None
        socktype = socket.SOCK_DGRAM if self.use_tdp else socket.SOCK_STREAM
        res = socket.getaddrinfo(
                self.server,
                self.port,
                socket.AF_UNSPEC,
                type=socktype
            )[0]
        addr_fam, sock_type, proto, canonname, sock_addr = res
        try:
            sock = socket.socket(family=addr_fam, type=socktype, proto=proto)
            self.logger.log("CLIENT","INFO","Socket created: %s %d (%s)" %
                    (
                        self.server,
                        self.port,
                        "UDP" if self.use_tdp else "TCP"
                    )
                )
        except OSError as msg:
            err = msg
        try:
            sock.connect(sock_addr)
        except OSError as msg:
            sock.close()
            sock = None
            err = msg
        if sock is None:
            self.logger.log("CLIENT","ERRO","Connection error: %s" % err)
        else:
            self.logger.log("CLIENT","INFO","Connected to %s:%d over %s" %
                    (
                        self.server,
                        self.port,
                        "UDP" if self.use_tdp else "TCP"
                    )
                )
        return sock

    def __do_handshake(self, sock):
        """
        Handle initial connection handshake with TMP/TDP server

        Returns: True on success, otherwise False
        """
        req = TmpPacket(self.logger)
        payload = req.build(TmpPacket.TYPE_REQ, int(self.version))
        sock.sendall(payload)

        self.logger.log("CLIENT","INFO","Request sent...")

        recv = sock.recv(1024)
        self.logger.log("CLIENT","INFO","Received %s" % recv)

        rsp = TmpPacket(self.logger)
        payload = rsp.build(TmpPacket.TYPE_RSP, int(self.version))
        sock.sendall(payload)
        self.logger.log("CLIENT","INFO","Response sent.")

    def send(self, opcode, data, packet_type=1):
        """
        Abstract sending functionality between TMP and TDP

        `opcode[int]`: The operation code to execute

        `data[str]`: The data to send

        Return: True on success, otherwise false.
        """
        if self.use_tdp:
            return self.send_tdp(packet_type, opcode, data)
        return self.send_tmp(opcode, data)

    def send_tmp(self, opcode, data):
        """
        Handing sending data over TCP to the TMP server.

        `opcode[int]`: The operation code to execute

        `data[str]`: The data to send

        Return: True on success, otherwise false.
        """
        sock = self.__handle_socket()
        if sock is None:
            return False

        self.__do_handshake(sock)
        packet = TmpPacket(
                    self.logger,
                    int(opcode,base=16),
                    data,
                )
        payload = packet.build(
                        TmpPacket.TYPE_DAT,
                        int(self.version),
                        int(self.btype)
                    )
        sock.sendall(payload)
        self.logger.log("CLIENT","INFO","Sent TMP Packet.")
        recv = sock.recv(1024)
        self.logger.log("CLIENT","INFO","Received %s" % recv)
        return True

    def send_tdp(self, packet_type, opcode, data):
        """
        Handling sending data over UDP to the TDP server.

        Input: Payload to be sent

        Return: True on success, otherwise false.
        """
        sock = self.__handle_socket()

        if sock is None:
            return False
        packet = TdpPacket(
                    self.logger,
                    int(opcode,base=16),
                    data
                )
        payload = packet.build(
                    int(packet_type,base=16),
                    int(self.version)
                )
        sock.sendall(payload)
        self.logger.log("CLIENT","INFO","Sent TDP Packet.")
        recv = sock.recv(1024)
        self.logger.log("CLIENT","INFO","Received %s" % recv)
        return True

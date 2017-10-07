import _thread
import json
import socket
import uuid

import byte_utils


class SocketServer:
    ip = None
    port = None
    motd = None
    version_text = None
    kick_message = None
    samples = None
    server_icon = None
    s = None

    def __init__(self, ip, port, motd, version_text, kick_message, samples, server_icon, logger):
        self.ip = ip
        self.port = port
        self.motd = motd
        self.version_text = version_text
        self.kick_message = kick_message
        self.samples = samples
        self.server_icon = server_icon
        self.logger = logger

    def on_new_client(self, client_socket, addr):
        data = client_socket.recv(1024)
        (length, i) = byte_utils.read_varint(data, 0)
        (packetID, i) = byte_utils.read_varint(data, i)

        if packetID == 0:
            (version, i) = byte_utils.read_varint(data, i)
            (ip, i) = byte_utils.read_utf(data, i)

            ip = ip.replace('\x00', '')
            is_using_fml = False

            if ip.endswith("FML"):
                is_using_fml = True
                ip = ip[:-3]

            (port_tuple, i) = byte_utils.read_ushort(data, i)
            (state, i) = byte_utils.read_varint(data, i)
            if state == 1:
                self.logger.info(("[%s:%s] Received client " + ("(using ForgeModLoader) " if is_using_fml else "") +
                                  "ping packet (%s:%s).") % (addr[0], addr[1], ip, port_tuple[0]))
                motd = {}
                motd["version"] = {}
                motd["version"]["name"] = self.version_text
                motd["version"]["protocol"] = 2
                motd["players"] = {}
                motd["players"]["max"] = 0
                motd["players"]["online"] = 0
                motd["players"]["sample"] = []

                for sample in self.samples:
                    motd["players"]["sample"].append({"name": sample, "id": str(uuid.uuid4())})

                motd["description"] = {"text": self.motd}

                if self.server_icon and len(self.server_icon) > 0:
                    motd["favicon"] = self.server_icon

                self.write_response(client_socket, json.dumps(motd))
            elif state == 2:
                name = ""
                if len(data) != i:
                    (some_int, i) = byte_utils.read_varint(data, i)
                    (some_int, i) = byte_utils.read_varint(data, i)
                    (name, i) = byte_utils.read_utf(data, i)
                self.logger.info(
                    ("[%s:%s] " + (name + " t" if len(name) > 0 else "T") + "ries to connect to the server " +
                     ("(using ForgeModLoader) " if is_using_fml else "") + "(%s:%s).")
                    % (addr[0], addr[1], ip, port_tuple[0]))
                self.write_response(client_socket, json.dumps({"text": self.kick_message}))
            else:
                self.logger.info(
                    "[%s:%d] Tried to request a login/ping with an unknown state: %d" % (addr[0], addr[1], state))
        elif packetID == 1:
            (long, i) = byte_utils.read_long(data, i)
            response = bytearray()
            byte_utils.write_varint(response, 9)
            byte_utils.write_varint(response, 1)
            bytearray.append(long)
            client_socket.sendall(bytearray)
            self.logger.info("[%s:%d] Responded with pong packet." % (addr[0], addr[1]))
        else:
            self.logger.warning("[%s:%d] Sent an unexpected packet: %d" % (addr[0], addr[1], packetID))

    def write_response(self, client_socket, response):
        response_array = bytearray()
        byte_utils.write_varint(response_array, 0)
        byte_utils.write_utf(response_array, response)
        length = bytearray()
        byte_utils.write_varint(length, len(response_array))
        client_socket.sendall(length)
        client_socket.sendall(response_array)

    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.ip, self.port))
        self.s.settimeout(5000)
        self.s.listen(30)
        self.logger.info("Server started on %s:%s! Waiting for incoming connections..." % (self.ip, self.port))
        while 1:
            (client, address) = self.s.accept()
            _thread.start_new_thread(self.on_new_client, (client, address,))

    def close(self):
        self.s.close()

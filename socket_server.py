import json
import socket
import uuid
from threading import Thread

import byte_utils


class SocketServer:
    def __init__(self, ip, port, motd, version_text, kick_message, samples, server_icon, logger, show_hostname, player_max, player_online, protocol):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.motd = motd
        self.version_text = version_text
        self.kick_message = kick_message
        self.samples = samples
        self.server_icon = server_icon
        self.logger = logger
        self.show_hostname = show_hostname
        self.player_max = player_max
        self.player_online = player_online
        self.protocol = protocol

    def on_new_client(self, client_socket, addr):
        data = client_socket.recv(1024)
        client_ip = addr[0]

        fqdn = socket.getfqdn(client_ip)
        if self.show_hostname and client_ip != fqdn:
            client_ip = fqdn + "/" + client_ip

        try:
            (length, i) = byte_utils.read_varint(data, 0)
            (packetID, i) = byte_utils.read_varint(data, i)

            if packetID == 0:
                (version, i) = byte_utils.read_varint(data, i)
                (ip, i) = byte_utils.read_utf(data, i)

                ip = ip.replace('\x00', '').replace("\r", "\\r").replace("\t", "\\t").replace("\n", "\\n")
                is_using_fml = False

                if ip.endswith("FML"):
                    is_using_fml = True
                    ip = ip[:-3]

                (port, i) = byte_utils.read_ushort(data, i)
                (state, i) = byte_utils.read_varint(data, i)

                if state == 1:
                    self.logger.info(("[%s:%s] Received client " + ("(using ForgeModLoader) " if is_using_fml else "") +
                                      "ping packet (%s:%s).") % (client_ip, addr[1], ip, port))
                    motd = {}
                    motd["version"] = {}
                    motd["version"]["name"] = self.version_text
                    motd["version"]["protocol"] = self.protocol
                    motd["players"] = {}
                    motd["players"]["max"] = self.player_max
                    motd["players"]["online"] = self.player_online
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
                        % (client_ip, addr[1], ip, port))
                    self.write_response(client_socket, json.dumps({"text": self.kick_message}))
                else:
                    self.logger.info(
                        "[%s:%d] Tried to request a login/ping with an unknown state: %d" % (client_ip, addr[1], state))
            elif packetID == 1:
                (long, i) = byte_utils.read_long(data, i)
                response = bytearray()
                byte_utils.write_varint(response, 9)
                byte_utils.write_varint(response, 1)
                bytearray.append(long)
                client_socket.sendall(bytearray)
                self.logger.info("[%s:%d] Responded with pong packet." % (client_ip, addr[1]))
            else:
                self.logger.warning("[%s:%d] Sent an unexpected packet: %d" % (client_ip, addr[1], packetID))
        except (TypeError, IndexError):
            self.logger.warning("[%s:%s] Received invalid data (%s)" % (client_ip, addr[1], data))
            return

    def write_response(self, client_socket, response):
        response_array = bytearray()
        byte_utils.write_varint(response_array, 0)
        byte_utils.write_utf(response_array, response)
        length = bytearray()
        byte_utils.write_varint(length, len(response_array))
        client_socket.sendall(length)
        client_socket.sendall(response_array)

    def start(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(5)
        self.sock.listen(30)
        self.logger.info("Server started on %s:%s! Waiting for incoming connections..." % (self.ip, self.port))
        while 1:
            try:
                (client, address) = self.sock.accept()
            except socket.timeout:
                continue  # timeouts may occur but shouldn't worry uns server-side
            
            Thread(target=self.on_new_client, daemon=True, args=(client, address,)).start()

    def close(self):
        self.sock.close()

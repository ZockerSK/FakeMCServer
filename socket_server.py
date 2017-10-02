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

    def __init__(self, ip, port, motd, version_text, kick_message, samples, server_icon):
        self.ip = ip
        self.port = port
        self.motd = motd
        self.version_text = version_text
        self.kick_message = kick_message
        self.samples = samples
        self.server_icon = server_icon

    def on_new_client(self, client_socket, addr):
        data = client_socket.recv(1024)
        (length, i) = byte_utils.read_varint(data, 0)
        (packetID, i) = byte_utils.read_varint(data, i)

        if packetID == 0:
            (version, i) = byte_utils.read_varint(data, i)
            (ip, i) = byte_utils.read_utf(data, i)
            (port_tuple, i) = byte_utils.read_ushort(data, i)
            (state, i) = byte_utils.read_varint(data, i)
            if state == 1:
                print("%s:%s has sent a ping to the server (%s:%s)" % (addr[0], addr[1], ip, port_tuple[0]))

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

                if len(self.server_icon) > 0:
                    motd["favicon"] = self.server_icon

                self.write_response(client_socket, json.dumps(motd))
            elif state == 2:
                print("%s:%s has tried to connect to the server (%s:%s)" % (addr[0], addr[1], ip, port_tuple[0]))
                self.write_response(client_socket, json.dumps({"text": self.kick_message}))
            else:
                print("%s:%s tried to request a login/ping with a unknown state: %s" % (addr[0], addr[1], state))
        elif packetID == 1:
            (long, i) = byte_utils.read_long(data, i)
            response = bytearray()
            byte_utils.write_varint(response, 9)
            byte_utils.write_varint(response, 1)
            bytearray.append(long)
            client_socket.sendall(bytearray)
            print("Send pong to %s" % addr)
        else:
            print("%s tried to request a unknown packet: %s" % (addr, packetID))

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
        print("Server started!")
        while 1:
            (client, address) = self.s.accept()
            _thread.start_new_thread(self.on_new_client, (client, address,))

    def close(self):
        self.s.close()
